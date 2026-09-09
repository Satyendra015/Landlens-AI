import os
import sys
import uvicorn

# Add workspace directory to python search path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f">> Starting LandLens AI on http://localhost:{port}")
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=True)
