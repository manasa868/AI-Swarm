"""Researcher Agent: Researches technical information, best practices, and architecture patterns."""
from typing import Dict, Any, List
from app.agents.base import BaseAgent


class ResearcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="researcher",
            name="Researcher Agent",
            role="Technical Research & Solution Architect",
        )

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        task_desc = f"Conducting technical and architectural research for project '{state.get('name')}'"
        self.start(task_desc)

        project_type = state.get("project_type", "general")
        user_request = state.get("user_request", "")

        if project_type == "ml":
            research_data = {
                "domain": "Machine Learning & Natural Language Processing",
                "recommended_architecture": "TF-IDF / N-gram Feature Extraction + Regularized Linear / Ensemble Classifier",
                "algorithms_evaluated": [
                    {"name": "PassiveAggressiveClassifier", "suitability": "High", "reason": "Superior performance on streaming text and fake news classification tasks."},
                    {"name": "Logistic Regression (L2)", "suitability": "High", "reason": "Fast, highly interpretable baseline with probability estimates."},
                    {"name": "Multinomial Naive Bayes", "suitability": "Medium", "reason": "Fast baseline but assumes conditional feature independence."}
                ],
                "data_pipeline": [
                    "Text normalization (lowercasing, punctuation stripping)",
                    "Stopword removal and vocabulary pruning",
                    "Sublinear TF-IDF scaling (smooth_idf=True)"
                ],
                "sources_and_references": [
                    {"title": "Automated Fake News Detection: An In-Depth Survey", "ref": "IEEE Transactions on Knowledge and Data Engineering"},
                    {"title": "Scikit-Learn Text Feature Extraction Best Practices", "ref": "scikit-learn.org/stable/modules/feature_extraction.html"},
                    {"title": "FastAPI Production Deployment Guidelines", "ref": "fastapi.tiangolo.com/deployment"}
                ],
                "security_considerations": [
                    "Sanitize incoming text payload against denial-of-service via huge strings",
                    "Do not use untrusted pickle loading in production without hash verification"
                ]
            }
        elif project_type == "web":
            research_data = {
                "domain": "Full-Stack Web Systems & Relational Modeling",
                "recommended_architecture": "Layered Architecture (API -> Service -> Repository -> SQLite/Postgres)",
                "entity_models": [
                    "User / Admin (RBAC: Admin, Student, Driver)",
                    "Bus (Plate, Capacity, Model, Status)",
                    "Route (Origin, Destination, Stops, Distance)",
                    "Assignment (Bus <-> Driver <-> Route scheduling)"
                ],
                "sources_and_references": [
                    {"title": "REST API Design Guidelines", "ref": "Microsoft REST API Guidelines (github.com/microsoft)"},
                    {"title": "SQLAlchemy 2.0 Unified Mapping Standard", "ref": "docs.sqlalchemy.org/en/20"},
                    {"title": "Clean Architecture: A Craftsman's Guide to Software Structure", "ref": "Robert C. Martin"}
                ],
                "security_considerations": [
                    "Password hashing with bcrypt / argon2",
                    "Parameterized SQL queries to prevent SQL Injection",
                    "CORS origin whitelisting"
                ]
            }
        elif project_type == "data_analysis":
            research_data = {
                "domain": "Unsupervised Learning & Customer Segmentation",
                "recommended_architecture": "ETL -> StandardScaler -> Dimensionality Reduction (PCA) -> KMeans Clustering -> Silhouette Validation",
                "algorithms_evaluated": [
                    {"name": "KMeans Clustering", "suitability": "High", "reason": "Standard industrial algorithm for spherical clusters and clear centroids."},
                    {"name": "DBSCAN", "suitability": "Medium", "reason": "Good for arbitrary shapes but sensitive to epsilon parameter."}
                ],
                "sources_and_references": [
                    {"title": "Customer Segmentation using RFM Analysis & Machine Learning", "ref": "Journal of Marketing Analytics"},
                    {"title": "Cluster Analysis: Determining the Optimal Number of Clusters", "ref": "Nature Methods"}
                ],
                "security_considerations": [
                    "Anonymization of PII (Personally Identifiable Information) before analytical clustering",
                    "Data integrity validation on CSV inputs"
                ]
            }
        else:
            research_data = {
                "domain": "Software Engineering & Microservice Architecture",
                "recommended_architecture": "Clean Modular Architecture with Dependency Injection",
                "sources_and_references": [
                    {"title": "Twelve-Factor App Methodology", "ref": "12factor.net"},
                    {"title": "Design Patterns: Elements of Reusable Object-Oriented Software", "ref": "Gang of Four"}
                ],
                "security_considerations": [
                    "Strict input schema validation",
                    "Safe error handling without exposing stack traces to untrusted clients"
                ]
            }

        self.complete()
        return research_data
