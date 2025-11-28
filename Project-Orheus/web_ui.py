"""
Project Orpheus - Web Interface Launcher
Launches the FastAPI server for the music generation studio
"""

import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    print("=" * 60)
    print("PROJECT ORPHEUS - AI Music Generation Studio")
    print("=" * 60)
    print(f"\nStarting server on http://localhost:{port}")
    print(f"API docs available at http://localhost:{port}/docs")
    print(f"Landing page: http://localhost:{port}")
    print(f"Generator Studio: http://localhost:{port}/generator.html")
    print("\nPress CTRL+C to stop the server\n")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
