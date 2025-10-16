from dotenv import load_dotenv
import os

load_dotenv()

NEON_DB_URL = os.getenv("NEON_DB_URL")