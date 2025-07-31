import logging
import os

from flaskapp.logger import default_logger

from flaskapp import create_app, socketio

logger = default_logger("flaskapp", logging.INFO)

app = create_app()


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST")
    port = os.getenv("FLASK_RUN_PORT")
    logger.info(f"Starting app in {host}:{port}")
    socketio.run(app, host=host, port=port)
