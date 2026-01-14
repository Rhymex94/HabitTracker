import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("ENVIRONMENT") != "production"
    app.run(debug=debug, host="0.0.0.0")