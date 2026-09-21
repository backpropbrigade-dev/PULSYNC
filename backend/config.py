import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "PULSYNC API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pulsync.db")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Recommendation weights
    W_INTENT: float = float(os.getenv("W_INTENT", "0.30"))
    W_PAGE: float = float(os.getenv("W_PAGE", "0.20"))
    W_USER: float = float(os.getenv("W_USER", "0.20"))
    W_RECENT: float = float(os.getenv("W_RECENT", "0.20"))
    W_INFO: float = float(os.getenv("W_INFO", "0.10"))

settings = Settings()
