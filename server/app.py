#!/usr/bin/env python3
"""Combined API + Static file server for Kimi Chat History Dashboard."""

import logging
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import app as api_app

# Create a new FastAPI app that includes both API and static files
app = FastAPI(
    title="Kimi Chat History",
    description="Combined API and Dashboard server"
)

# Mount the API
app.mount("/api", api_app)

# Mount static files (dashboard)
static_path = Path(__file__).parent.parent / "dashboard"
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")
    logging.info(f"Serving static files from {static_path}")
else:
    logging.warning(f"Dashboard directory not found at {static_path}")

# Add CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
