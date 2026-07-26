import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
url = "https://b040fb2d-0371-4ec0-9b1a-523b858d0124.eu-central-1-0.aws.cloud.qdrant.io"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6ZTQzNzc3MjUtZGFmYS00MTNlLTkyYjctYmNhZmIzYWRkMDgxIn0.Af3xS5Y3aXD8cJzCQBf_5bIO8GHwAuE-bMPmY-yF7DI"

try:
    print("Connecting to Qdrant...")
    client = QdrantClient(url=url, api_key=api_key)
    print("Collections:", client.get_collections())
except Exception as e:
    import traceback
    traceback.print_exc()
