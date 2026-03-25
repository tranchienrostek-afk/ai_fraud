import openai
from src.config import config


class Agent05Explanation:
    def __init__(self):
        self.name = "The Narrator"

        # Initialize OpenAI Client for Chat
        openai.api_type = "azure"
        openai.api_key = config.AZURE_OPENAI_API_KEY
        openai.api_base = config.AZURE_OPENAI_ENDPOINT
        openai.api_version = config.AZURE_OPENAI_API_VERSION

    def generate_explanation(self, claim_data: dict, analysis_results: dict) -> str:
        """
        Uses Azure OpenAI (GPT-4o) with ReAct prompting to explain the fraud score.
        """
        score = analysis_results["final_score"]
        level = analysis_results["risk_level"]
        factors = analysis_results["details"]

        # ReAct Prompt Structure
        prompt = f"""
        Act as a Senior Insurance Fraud Investigator. Use the ReAct (Reasoning + Acting) philosophy.
        
        Task: Analyze the inputs and provide a final verdict explanation (in Vietnamese).
        
        Inputs:
        1. Claim Context: Diagnosis '{claim_data["diagnosis_desc"]}' - Amount {claim_data["claim_amount"]}
        2. Automated Scores: 
           - Graph Risk: {factors["graph_contrib"]} (indicates organized fraud)
           - Anomaly Risk: {factors["anomaly_contrib"]} (indicates outlier behavior)
           - Final Aggregated Score: {score} ({level})

        Process:
        1. THOUGHT: Reflect on the scores. Is there a conflict? (e.g., High Graph but Low Anomaly). What does this imply?
        2. REASONING: Synthesize the evidence. If Graph is high, it's likely a syndicate even if the cost is normal.
        3. FINAL ANSWER: Write the report for the human investigator.

        Output Format:
        [THOUGHT]: ... (Internal monologue)
        [REPORT]: 
        - Headline: [ALERT LEVEL]
        - Summary: ...
        - Key Drivers: ...
        - Recommendation: ...
        """

        try:
            response = openai.ChatCompletion.create(
                engine=config.MODEL_CHAT,  # e.g., "gpt-4o-mini"
                messages=[
                    {
                        "role": "system",
                        "content": "You are a specialized AI Investigator that thinks before speaking.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more focused reasoning
                max_tokens=500,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating explanation: {str(e)}"


agent_05 = Agent05Explanation()
