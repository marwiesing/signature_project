import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")  # Needed for flash/login/session
    # Add more custom configs if needed

config = Config()
