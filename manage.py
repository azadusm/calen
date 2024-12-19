from flask_migrate import Migrate
from app import app, db

if __name__ == "__main__":
    from flask.cli import main as flask_main
    flask_main()
