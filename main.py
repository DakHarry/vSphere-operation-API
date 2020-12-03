"""
vSphere operation api
"""
import uvicorn
from fastapi import FastAPI

from src.router.router import router as api_router # pylint: disable=E0401

def get_application() -> FastAPI:
    """Initialize Application"""
    application = FastAPI()
    application.include_router(api_router)
    return application

app = get_application()


#uvicorn main:app --reload


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
