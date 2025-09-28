# File: core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Model name for Hugging Face API
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Hugging Face token
HF_API_KEY = os.getenv("HF_API_KEY")

# --- Chroma settings ---
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
