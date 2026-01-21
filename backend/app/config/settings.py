import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CLERK_ISSUER = os.getenv("CLERK_ISSUER")
    CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

settings = Settings()
