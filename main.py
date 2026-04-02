import uvicorn

from src.api.app import create_app
from src.config import config

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host=config.web.host, port=config.web.port)
