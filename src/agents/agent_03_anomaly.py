import openai
from src.config import config
from src.database import qdrant_client
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np
from sklearn.ensemble import IsolationForest


class Agent03Anomaly:
    def __init__(self):
        self.name = "The Anomaly Hunter"
        self.collection_name = "medical_claims"

        # Initialize OpenAI Client
        openai.api_type = "azure"
        openai.api_key = config.AZURE_EMBEDDINGS_API_KEY
        openai.api_base = config.AZURE_EMBEDDINGS_ENDPOINT
        openai.api_version = config.AZURE_OPENAI_API_VERSION

        # Ensure Qdrant Collection Exists
        try:
            qdrant_client.get_collection(self.collection_name)
        except:
            qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

        # Mock Isolation Forest Model (In prod, load from .pkl)
        self.clf = IsolationForest(contamination=0.05)
        # Fit with some dummy data to avoid errors on first run
        self.clf.fit(np.random.rand(100, 1))

    def get_embedding(self, text):
        response = openai.Embedding.create(
            input=text,
            engine="text-embedding-ada-002",  # Ensure this matches your Azure Deployment Name
        )
        return response["data"][0]["embedding"]

    def analyze(self, claim_data: dict) -> dict:
        """
        Detects anomalies using Sementic Search & Statistical Outliers.
        Returns: {"score": float, "reason": str}
        """
        # 1. Semantic Anomaly (Text)
        text_desc = (
            f"{claim_data['diagnosis_desc']} treated via {claim_data['diagnosis_code']}"
        )
        vector = self.get_embedding(text_desc)

        # Search existing claims for similarity
        search_result = qdrant_client.search(
            collection_name=self.collection_name, query_vector=vector, limit=3
        )

        semantic_score = 0
        if search_result:
            # Logic: If nearest neighbor is very different, it's an anomaly?
            # For simplicity here: If highest similarity < 0.7, it's weird.
            top_score = search_result[0].score
            if top_score < 0.7:
                semantic_score = 60  # High risk

        # 2. Statistical Anomaly (Cost)
        cost = np.array([[claim_data["claim_amount"]]])
        is_outlier = self.clf.predict(cost)[0]  # -1 for outlier, 1 for inlier

        stats_score = 0
        if is_outlier == -1:
            stats_score = 80  # Very high risk

        # 3. Save current claim to Vector DB for future training
        # In prod, do this async
        # qdrant_client.upsert(...)

        final_score = max(semantic_score, stats_score)

        reasons = []
        if semantic_score > 0:
            reasons.append("Diagnosis description is semantically rare.")
        if stats_score > 0:
            reasons.append(f"Claim amount {cost[0][0]} is a statistical outlier.")

        return {
            "score": final_score,
            "reason": "; ".join(reasons) if reasons else "Behavior is normal.",
        }


agent_03 = Agent03Anomaly()
