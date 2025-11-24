import os
from typing import Optional

class Config:
    # OpenAI API 
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = "gpt-4.1-nano"
    TEMPERATURE: float = 0.3
    
    # Sentence Transformer Model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # SpaCy Model
    SPACY_MODEL: str = "en_core_web_sm"
    
    # Thresholds
    MIN_MATCH_SCORE: float = 60.0
    HIGH_MATCH_SCORE: float = 80.0

config = Config()