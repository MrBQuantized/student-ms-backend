import uvicorn


def dev():
    """Run the FastAPI dev server with auto-reload."""
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8002,
        reload=True,
    )
