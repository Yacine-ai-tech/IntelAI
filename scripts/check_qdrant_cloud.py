"""
Helper script to test connection to Qdrant Cloud cluster using environment variables.
"""
import os
from qdrant_client import QdrantClient

url = os.getenv("QDRANT_URL", "")
api_key = os.getenv("QDRANT_API_KEY", "")

if not (url and api_key):
    print("ℹ️ QDRANT_URL or QDRANT_API_KEY not set in environment.")
else:
    try:
        print(f"Connecting to Qdrant at {url}...")
        client = QdrantClient(url=url, api_key=api_key)
        print("Collections:", client.get_collections())
    except Exception as e:
        import traceback
        traceback.print_exc()
