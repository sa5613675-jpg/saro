"""
WSGI Entry Point for Production
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing app
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✅ Loaded .env from {env_path}")
else:
    print(f"⚠️  .env file not found at {env_path}")

from app import create_app

# Create the application instance
app = create_app('production')

if __name__ == "__main__":
    app.run()
