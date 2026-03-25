from src.database import neo4j_conn


class Agent02Graph:
    def __init__(self):
        self.name = "The Graph Detective"

    def analyze(self, claim_data: dict) -> dict:
        """
        Queries Neo4j for suspicious patterns.
        Returns: {"score": float, "reason": str, "features": dict}
        """
        user_id = claim_data["user_id"]
        phone = claim_data["phone_number"]
        ip = claim_data.get("ip_address", "0.0.0.0")

        # 1. Sync Data to Graph (Ensure Node exists)
        self._sync_claim_to_graph(claim_data)

        # 2. Check: Shared Phone Number with Rejected Claims
        query_shared_phone = """
        MATCH (u:User {id: $user_id})-[:HAS_PHONE]->(p:Phone)<-[:HAS_PHONE]-(other:User)
        MATCH (other)-[:FILED]->(c:Claim)
        WHERE c.status = 'REJECTED'
        RETURN count(c) as bad_link_count
        """
        results = neo4j_conn.query(query_shared_phone, {"user_id": user_id})
        bad_link_count = results[0]["bad_link_count"] if results else 0

        # 3. Check: Shared IP Cluster
        query_ip_cluster = """
        MATCH (u:User {id: $user_id})-[:USED_IP]->(ip:IP)<-[:USED_IP]-(other:User)
        RETURN count(distinct other) as cluster_size
        """
        results_ip = neo4j_conn.query(query_ip_cluster, {"user_id": user_id})
        cluster_size = results_ip[0]["cluster_size"] if results_ip else 0

        # Scoring Logic
        score = 0
        reasons = []

        if bad_link_count > 0:
            score += 50
            reasons.append(f"Linked to {bad_link_count} rejected claims via Phone.")

        if cluster_size > 5:
            score += 40
            reasons.append(f"Part of a large IP cluster ({cluster_size} users).")

        final_score = min(score, 100)
        return {
            "score": final_score,
            "reason": "; ".join(reasons) if reasons else "No graph anomalies detected.",
            "features": {"bad_links": bad_link_count, "cluster_size": cluster_size},
        }

    def _sync_claim_to_graph(self, data):
        """
        Upsert User, Phone, IP nodes and relationships.
        """
        query = """
        MERGE (u:User {id: $user_id})
        MERGE (p:Phone {number: $phone})
        MERGE (ip:IP {addr: $ip})
        MERGE (u)-[:HAS_PHONE]->(p)
        MERGE (u)-[:USED_IP]->(ip)
        """
        neo4j_conn.query(
            query,
            {
                "user_id": data["user_id"],
                "phone": data["phone_number"],
                "ip": data.get("ip_address", "unknown"),
            },
        )


agent_02 = Agent02Graph()
