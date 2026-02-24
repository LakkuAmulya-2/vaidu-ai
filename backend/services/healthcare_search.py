"""
Vertex AI Search integration for healthcare visual Q&A.
Production-ready implementation with both API and LangChain support.
"""
import base64
import logging
import os
import subprocess
from typing import List, Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class HealthcareSearch:
    """
    Healthcare search using Vertex AI Search for visual Q&A.
    """
    
    def __init__(self, project_id: Optional[str] = None, 
                 location: str = "global",
                 collection_id: str = "default_collection",
                 data_store_id: str = "medical-data-store"):
        """
        Initialize healthcare search client.
        
        Args:
            project_id: GCP project ID
            location: Search location (global or us)
            collection_id: Collection ID
            data_store_id: Data store ID
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location
        self.collection_id = collection_id
        self.data_store_id = data_store_id
        
        # Serving config path for API calls
        if self.project_id:
            self.serving_config = (
                f"projects/{self.project_id}/locations/{self.location}/"
                f"collections/{self.collection_id}/dataStores/{self.data_store_id}/"
                f"servingConfigs/default_search"
            )
            self.api_endpoint = (
                f"https://discoveryengine.googleapis.com/v1/"
                f"projects/{self.project_id}/locations/{self.location}/"
                f"collections/{self.collection_id}/dataStores/{self.data_store_id}/"
                f"servingConfigs/default_search:search"
            )
        else:
            self.serving_config = None
            self.api_endpoint = None
        
        self.client = None
        self.langchain_retriever = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize both Discovery Engine client and LangChain retriever."""
        # Try Discovery Engine client
        try:
            if self.project_id:
                from google.cloud import discoveryengine_v1 as discoveryengine
                self.client = discoveryengine.SearchServiceClient()
                logger.info("Discovery Engine client initialized successfully")
        except ImportError:
            logger.warning("google-cloud-discoveryengine not installed. Using REST API fallback.")
        except Exception as e:
            logger.warning(f"Could not initialize Discovery Engine client: {e}")
        
        # Try LangChain retriever
        try:
            if self.project_id:
                from langchain_google_community import VertexAISearchRetriever
                self.langchain_retriever = VertexAISearchRetriever(
                    project_id=self.project_id,
                    data_store_id=self.data_store_id,
                    location_id=self.location,
                    engine_data_type=1,  # 1 = unstructured, 2 = structured
                    max_documents=10,
                )
                logger.info("LangChain retriever initialized successfully")
        except ImportError:
            logger.warning("langchain-google-community not installed. Using REST API only.")
        except Exception as e:
            logger.warning(f"Could not initialize LangChain retriever: {e}")
    
    def _get_access_token(self) -> str:
        """Get Google Cloud access token."""
        try:
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return ""
    
    def search_with_image(self, image_bytes: bytes, query: str, 
                         page_size: int = 10) -> List[Dict[str, Any]]:
        """
        Search healthcare knowledge base with image and text query.
        Uses REST API for maximum compatibility.
        
        Args:
            image_bytes: Image data
            query: Text query
            page_size: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.project_id or not self.api_endpoint:
            logger.warning("Search not configured. Returning fallback results.")
            return self._fallback_search(query)
        
        try:
            # Method 1: Try Discovery Engine client (if available)
            if self.client:
                return self._search_with_client(image_bytes, query, page_size)
            
            # Method 2: Use REST API (always works)
            return self._search_with_rest_api(image_bytes, query, page_size)
            
        except Exception as e:
            logger.error(f"Error in healthcare search: {e}")
            return self._fallback_search(query)
    
    def _search_with_client(self, image_bytes: bytes, query: str, page_size: int) -> List[Dict[str, Any]]:
        """Search using Discovery Engine client."""
        from google.cloud import discoveryengine_v1 as discoveryengine
        
        # Create search request with image
        request = discoveryengine.SearchRequest(
            serving_config=self.serving_config,
            query=query,
            image_query=discoveryengine.SearchRequest.ImageQuery(
                image_bytes=base64.b64encode(image_bytes).decode()
            ),
            page_size=page_size
        )
        
        # Execute search
        response = self.client.search(request)
        
        # Parse results
        results = []
        for result in response.results:
            doc_data = result.document.struct_data
            results.append({
                "title": doc_data.get("title", ""),
                "content": doc_data.get("content", "")[:500],  # First 500 chars
                "snippet": doc_data.get("snippet", ""),
                "link": doc_data.get("link", ""),
                "image_url": doc_data.get("image_url", ""),
                "diagnosis": doc_data.get("diagnosis", ""),
                "relevance_score": result.relevance_score if hasattr(result, 'relevance_score') else 0.0,
                "source": "vertex_ai_search"
            })
        
        return results
    
    def _search_with_rest_api(self, image_bytes: bytes, query: str, page_size: int) -> List[Dict[str, Any]]:
        """Search using REST API (fallback method)."""
        access_token = self._get_access_token()
        if not access_token:
            raise ValueError("Could not get access token")
        
        # Encode image to base64
        img_b64 = base64.b64encode(image_bytes).decode()
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        request_body = {
            "servingConfig": self.serving_config,
            "query": query,
            "imageQuery": {
                "imageBytes": img_b64
            },
            "pageSize": page_size,
        }
        
        # Make API call
        response = requests.post(
            self.api_endpoint,
            headers=headers,
            json=request_body,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"API error: {response.status_code} - {response.text}")
            raise ValueError(f"API returned {response.status_code}")
        
        # Parse results
        results = []
        for r in response.json().get("results", []):
            doc = r.get("document", {})
            struct_data = doc.get("structData", {})
            
            results.append({
                "title": struct_data.get("title", ""),
                "content": struct_data.get("content", "")[:500],
                "snippet": struct_data.get("snippet", ""),
                "link": struct_data.get("link", ""),
                "image_url": struct_data.get("image_url", ""),
                "diagnosis": struct_data.get("diagnosis", ""),
                "relevance_score": r.get("relevanceScore", 0.0),
                "source": "vertex_ai_search_api"
            })
        
        return results
    
    def search_text_only(self, query: str, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        Search with text query only (no image).
        Uses LangChain retriever if available, otherwise REST API.
        
        Args:
            query: Text query
            page_size: Number of results
            
        Returns:
            List of search results
        """
        if not self.project_id:
            logger.warning("Search not configured. Returning fallback results.")
            return self._fallback_search(query)
        
        try:
            # Method 1: Try LangChain retriever (fastest)
            if self.langchain_retriever:
                docs = self.langchain_retriever.invoke(query)
                return [{
                    "title": doc.metadata.get("title", ""),
                    "content": doc.page_content[:500],
                    "snippet": doc.page_content[:200],
                    "link": doc.metadata.get("link", ""),
                    "relevance_score": doc.metadata.get("score", 0.0),
                    "source": "langchain_retriever"
                } for doc in docs[:page_size]]
            
            # Method 2: Use Discovery Engine client
            if self.client:
                from google.cloud import discoveryengine_v1 as discoveryengine
                
                request = discoveryengine.SearchRequest(
                    serving_config=self.serving_config,
                    query=query,
                    page_size=page_size
                )
                
                response = self.client.search(request)
                
                results = []
                for result in response.results:
                    doc_data = result.document.struct_data
                    results.append({
                        "title": doc_data.get("title", ""),
                        "content": doc_data.get("content", "")[:500],
                        "snippet": doc_data.get("snippet", ""),
                        "link": doc_data.get("link", ""),
                        "relevance_score": result.relevance_score if hasattr(result, 'relevance_score') else 0.0,
                        "source": "discovery_engine"
                    })
                
                return results
            
            # Method 3: REST API fallback
            return self._search_text_rest_api(query, page_size)
            
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return self._fallback_search(query)
    
    def _search_text_rest_api(self, query: str, page_size: int) -> List[Dict[str, Any]]:
        """Text search using REST API."""
        access_token = self._get_access_token()
        if not access_token:
            raise ValueError("Could not get access token")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        request_body = {
            "servingConfig": self.serving_config,
            "query": query,
            "pageSize": page_size,
        }
        
        response = requests.post(
            self.api_endpoint,
            headers=headers,
            json=request_body,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"API error: {response.status_code}")
            raise ValueError(f"API returned {response.status_code}")
        
        results = []
        for r in response.json().get("results", []):
            doc = r.get("document", {})
            struct_data = doc.get("structData", {})
            
            results.append({
                "title": struct_data.get("title", ""),
                "content": struct_data.get("content", "")[:500],
                "snippet": struct_data.get("snippet", ""),
                "link": struct_data.get("link", ""),
                "relevance_score": r.get("relevanceScore", 0.0),
                "source": "rest_api"
            })
        
        return results
    
    def _fallback_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Fallback search using Gemini when Vertex AI Search is not available.
        
        Args:
            query: Search query
            
        Returns:
            List of generated results
        """
        try:
            from utils.vertex_client import predict_text_with_retry
            
            prompt = f"""You are a medical information assistant. Answer this query based on standard medical knowledge:

Query: {query}

Provide a clear, accurate answer with:
1. Main explanation (2-3 sentences)
2. Key points (3-4 bullet points)
3. When to see a doctor
4. Reliable sources for more information

Keep it simple and practical for patients in rural India.
"""
            
            response = predict_text_with_retry("medgemma_4b", prompt)
            
            return [{
                "title": f"Answer to: {query}",
                "snippet": response[:300],
                "link": "",
                "relevance_score": 0.8,
                "source": "AI-generated (Gemini)"
            }]
        
        except Exception as e:
            logger.error(f"Error in fallback search: {e}")
            return [{
                "title": "Search unavailable",
                "snippet": "Healthcare search is temporarily unavailable. Please try again later or consult a healthcare professional.",
                "link": "",
                "relevance_score": 0.0,
                "source": "error"
            }]
    
    def is_available(self) -> bool:
        """Check if search service is available."""
        return self.client is not None and self.serving_config is not None


# Singleton instance
healthcare_search = HealthcareSearch()
