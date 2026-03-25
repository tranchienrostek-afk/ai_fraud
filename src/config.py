import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")
    
    # Embeddings
    AZURE_EMBEDDINGS_ENDPOINT = os.getenv("AZURE_EMBEDDINGS_ENDPOINT")
    AZURE_EMBEDDINGS_API_KEY = os.getenv("AZURE_EMBEDDINGS_API_KEY")
    
    # Models
    MODEL_CHAT = os.getenv("MODEL1", "gpt-4o-mini")
    MODEL_REASONING = os.getenv("MODEL2", "gpt-5-mini")
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.1))

    # Databases
    POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5432/fraud_detection")
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

config = Config()
