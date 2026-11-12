"""Simple launcher script for AI Swarm backend."""
import sys
import os
from pathlib import Path

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 70)
    print("  AI SWARM: FROM INDIVIDUAL TO INTELLIGENT TEAMS")
    print("  FastAPI Backend & Orchestration Engine")
    print("=" * 70)
    print("  * Dashboard & Unified SPA : http://127.0.0.1:8000")
    print("  * Interactive Swagger API : http://127.0.0.1:8000/docs")
    print("  * Health & Mode Check     : http://127.0.0.1:8000/health")
    print("=" * 70 + "\n")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(backend_dir)],
    )
