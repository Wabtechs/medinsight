import sys
import os

# Ensure backend modules are importable by Vercel serverless runtime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app  # noqa: E402
