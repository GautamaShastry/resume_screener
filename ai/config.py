import os
from typing import Optional

class Config:
    # OpenAI API 
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = "gpt-4o-mini"  # Fastest model with good quality
    TEMPERATURE: float = 0.3
    
    # Sentence Transformer Model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # SpaCy Model
    SPACY_MODEL: str = "en_core_web_sm"
    
    # Thresholds
    MIN_MATCH_SCORE: float = 60.0
    HIGH_MATCH_SCORE: float = 80.0
    
    # Performance settings - OPTIMIZED FOR SPEED
    SKIP_LLM_PARSING: bool = True   # Use NLP-only for parsing (saves ~5s)
    COMBINE_ADVICE_CALLS: bool = True  # Combine ATS + Career into one LLM call (saves ~3s)
    SKIP_REPORTS: bool = True  # Skip PDF/HTML generation (saves ~2s)
    USE_LLM_FOR_ADVICE: bool = False  # Use rule-based advice (saves ~3s)

config = Config()