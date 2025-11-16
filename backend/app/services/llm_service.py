"""
LLM service for flashcard generation using Ollama.
"""

import httpx
import json
from typing import List, Dict, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with Ollama LLM API"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_API_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = 120.0  # 2 minutes timeout
    
    async def generate_flashcards(
        self,
        text: str,
        num_cards: int = 5,
        difficulty: str = "medium"
    ) -> List[Dict[str, str]]:
        """
        Generate flashcards from text using Ollama.
        
        Args:
            text: Input text to generate flashcards from
            num_cards: Number of flashcards to generate
            difficulty: Difficulty level (easy, medium, hard)
        
        Returns:
            List of {question, answer} dictionaries
        """
        prompt = self._build_prompt(text, num_cards, difficulty)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.7,
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # Parse the response
                flashcards = self._parse_response(result.get("response", ""))
                return flashcards[:num_cards]
        
        except httpx.HTTPError as e:
            logger.error(f"Ollama API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            return []
    
    def _build_prompt(self, text: str, num_cards: int, difficulty: str) -> str:
        """Build prompt for flashcard generation"""
        difficulty_guidance = {
            "easy": "Create simple flashcards that test basic comprehension and recall of key facts.",
            "medium": "Create moderately challenging flashcards that test understanding and application of concepts.",
            "hard": "Create challenging flashcards that test deep understanding, synthesis, and critical thinking."
        }
        
        prompt = f"""Generate exactly {num_cards} flashcards from the following text.

Text:
{text}

{difficulty_guidance.get(difficulty, difficulty_guidance['medium'])}

Format your response as a JSON array with objects containing "question" and "answer" keys.
Example format:
[
  {{"question": "What is...", "answer": "..."}},
  {{"question": "Explain...", "answer": "..."}}
]

Return ONLY the JSON array, no other text.
Flashcards:"""
        
        return prompt
    
    def _parse_response(self, response: str) -> List[Dict[str, str]]:
        """Parse LLM response to extract flashcards"""
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Find JSON array
            start_idx = response.find("[")
            end_idx = response.rfind("]") + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                flashcards = json.loads(json_str)
                
                # Validate and clean flashcards
                validated = []
                for card in flashcards:
                    if isinstance(card, dict) and "question" in card and "answer" in card:
                        validated.append({
                            "question": str(card["question"]).strip(),
                            "answer": str(card["answer"]).strip()
                        })
                
                return validated
        
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
        
        return []
    
    async def check_health(self) -> bool:
        """Check if Ollama service is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/tags",
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False


class VectorEmbeddingService:
    """Service for generating vector embeddings for semantic search"""
    
    @staticmethod
    def simple_embedding(text: str, dimension: int = 384) -> List[float]:
        """
        Generate simple embedding using TF-IDF-like approach.
        For production, use sentence-transformers or similar.
        
        Args:
            text: Text to embed
            dimension: Embedding dimension
        
        Returns:
            List of floats representing the embedding
        """
        import hashlib
        
        # Simple hash-based embedding generation
        # In production, use proper embedding model
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        
        embedding = []
        for i in range(dimension):
            val = hash_val % 1000 / 1000.0
            embedding.append(val)
            hash_val = (hash_val >> 1) ^ (hash_val & 1) if hash_val & 1 else hash_val >> 1
        
        return embedding
    
    @staticmethod
    def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        import math
        
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = math.sqrt(sum(a * a for a in embedding1))
        norm2 = math.sqrt(sum(b * b for b in embedding2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
