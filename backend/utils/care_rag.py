"""
utils/care_rag.py
Context-Aware Retrieval-Enhanced Generation (CARE-RAG)
Query-type aware knowledge retrieval system
"""
import logging
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class CARERAG:
    """
    Context-Aware RAG system that adapts retrieval strategy based on query type
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize CARE-RAG with separate collections for different knowledge types"""
        try:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Use lightweight embedding model
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Separate collections for different medical knowledge types
            self.collections = {
                "diagnostic": self.client.get_or_create_collection(
                    name="diagnostic_kb",
                    metadata={"description": "Diagnostic criteria and symptoms"}
                ),
                "treatment": self.client.get_or_create_collection(
                    name="treatment_kb",
                    metadata={"description": "Treatment protocols and medications"}
                ),
                "preventive": self.client.get_or_create_collection(
                    name="preventive_kb",
                    metadata={"description": "Preventive care and lifestyle"}
                ),
                "emergency": self.client.get_or_create_collection(
                    name="emergency_kb",
                    metadata={"description": "Emergency protocols and danger signs"}
                )
            }
            
            logger.info("CARE-RAG initialized successfully")
            
        except Exception as e:
            logger.error(f"CARE-RAG initialization error: {e}")
            raise
    
    def classify_query(self, query: str) -> Dict[str, any]:
        """
        Enhanced query classification with intent detection and context extraction.
        
        Returns: {
            "intent": "diagnostic/treatment/preventive/emergency/general",
            "confidence": 0-1,
            "medical_entities": [...],
            "urgency": "low/medium/high/critical",
            "query_type": "factual/procedural/diagnostic/comparative"
        }
        """
        from utils.vertex_client import predict_text_with_retry
        import json
        
        query_lower = query.lower()
        
        # Quick rule-based classification for emergency
        emergency_keywords = [
            "emergency", "urgent", "severe", "bleeding", "unconscious",
            "chest pain", "difficulty breathing", "stroke", "heart attack",
            "అత్యవసరం", "తీవ్రమైన", "రక్తస్రావం", "ఆపాతకాలం"
        ]
        if any(keyword in query_lower for keyword in emergency_keywords):
            return {
                "intent": "emergency",
                "confidence": 1.0,
                "medical_entities": [],
                "urgency": "critical",
                "query_type": "procedural"
            }
        
        # Use AI for detailed classification
        try:
            prompt = f"""Classify this medical query and extract information.

Query: {query}

Return ONLY valid JSON:
{{
  "intent": "diagnostic/treatment/preventive/emergency/general",
  "confidence": 0.0-1.0,
  "medical_entities": ["entity1", "entity2"],
  "urgency": "low/medium/high/critical",
  "query_type": "factual/procedural/diagnostic/comparative",
  "is_medical": true/false,
  "requires_image": true/false,
  "suggested_collection": "diagnostic/treatment/preventive/emergency"
}}

Intent definitions:
- diagnostic: Asking about symptoms, causes, diagnosis
- treatment: Asking about treatment, medication, therapy
- preventive: Asking about prevention, lifestyle, diet
- emergency: Urgent medical situation
- general: General health information

Medical entities: Extract diseases, symptoms, body parts, medications mentioned.
"""
            
            result = predict_text_with_retry("medgemma_4b", prompt)
            
            try:
                classification = json.loads(result)
                return classification
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse classification")
                    
        except Exception as e:
            logger.error(f"AI classification error: {e}, falling back to rule-based")
            return self._rule_based_classification(query)
    
    def _rule_based_classification(self, query: str) -> Dict[str, any]:
        """
        Fallback rule-based classification.
        """
        query_lower = query.lower()
        
        # Diagnostic keywords
        diagnostic_keywords = [
            "diagnosis", "what is", "symptoms", "cause", "why",
            "లక్షణాలు", "ఎందుకు", "కారణం", "రోగం"
        ]
        if any(keyword in query_lower for keyword in diagnostic_keywords):
            return {
                "intent": "diagnostic",
                "confidence": 0.7,
                "medical_entities": [],
                "urgency": "medium",
                "query_type": "diagnostic"
            }
        
        # Treatment keywords
        treatment_keywords = [
            "treatment", "cure", "therapy", "medicine", "medication",
            "how to treat", "చికిత్స", "మందు"
        ]
        if any(keyword in query_lower for keyword in treatment_keywords):
            return {
                "intent": "treatment",
                "confidence": 0.7,
                "medical_entities": [],
                "urgency": "medium",
                "query_type": "procedural"
            }
        
        # Preventive keywords
        preventive_keywords = [
            "prevent", "avoid", "risk", "diet", "exercise", "lifestyle",
            "తగ్గించడం", "నివారణ", "ఆహారం"
        ]
        if any(keyword in query_lower for keyword in preventive_keywords):
            return {
                "intent": "preventive",
                "confidence": 0.7,
                "medical_entities": [],
                "urgency": "low",
                "query_type": "factual"
            }
        
        return {
            "intent": "general",
            "confidence": 0.5,
            "medical_entities": [],
            "urgency": "low",
            "query_type": "factual"
        }
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, str]]:
        """
        Query-type aware retrieval with adaptive strategy
        
        Args:
            query: User query
            k: Number of results to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            classification = self.classify_query(query)
            query_type = classification.get("intent", "general")
            results = []
            
            if query_type == "general":
                # Search all collections with fusion
                for col_name, collection in self.collections.items():
                    try:
                        col_results = collection.query(
                            query_texts=[query],
                            n_results=min(k, 2)
                        )
                        
                        if col_results['documents'] and col_results['documents'][0]:
                            for doc, metadata, distance in zip(
                                col_results['documents'][0],
                                col_results['metadatas'][0] if col_results['metadatas'] else [{}] * len(col_results['documents'][0]),
                                col_results['distances'][0] if col_results['distances'] else [0] * len(col_results['documents'][0])
                            ):
                                results.append({
                                    "content": doc,
                                    "source": col_name,
                                    "relevance": 1 - distance,  # Convert distance to relevance
                                    "metadata": metadata
                                })
                    except Exception as e:
                        logger.warning(f"Error querying {col_name}: {e}")
                        continue
            else:
                # Specialized retrieval from specific collection
                collection = self.collections.get(query_type)
                if collection:
                    try:
                        col_results = collection.query(
                            query_texts=[query],
                            n_results=k
                        )
                        
                        if col_results['documents'] and col_results['documents'][0]:
                            for doc, metadata, distance in zip(
                                col_results['documents'][0],
                                col_results['metadatas'][0] if col_results['metadatas'] else [{}] * len(col_results['documents'][0]),
                                col_results['distances'][0] if col_results['distances'] else [0] * len(col_results['documents'][0])
                            ):
                                results.append({
                                    "content": doc,
                                    "source": query_type,
                                    "relevance": 1 - distance,
                                    "metadata": metadata
                                })
                    except Exception as e:
                        logger.error(f"Error in specialized retrieval: {e}")
            
            # Sort by relevance
            results.sort(key=lambda x: x['relevance'], reverse=True)
            return results[:k]
            
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []
    
    def add_knowledge(self, collection_name: str, documents: List[str], 
                     metadatas: List[Dict] = None, ids: List[str] = None):
        """
        Add documents to a specific knowledge collection
        
        Args:
            collection_name: Name of collection (diagnostic, treatment, etc.)
            documents: List of document texts
            metadatas: Optional metadata for each document
            ids: Optional IDs for documents
        """
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Unknown collection: {collection_name}")
            
            collection = self.collections[collection_name]
            
            # Generate IDs if not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # Add documents
            collection.add(
                documents=documents,
                metadatas=metadatas or [{} for _ in documents],
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
            raise


# Global instance
_care_rag_instance = None

def get_care_rag() -> CARERAG:
    """Get or create global CARE-RAG instance"""
    global _care_rag_instance
    if _care_rag_instance is None:
        _care_rag_instance = CARERAG()
    return _care_rag_instance
