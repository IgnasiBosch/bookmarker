import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# inside of a "create the database" script, first create
# tables:
from src.db import metadata, engine
import src.bookmarks.tables
import src.auth.tables
metadata.create_all(engine)

# then, load the Alembic configuration and generate the
# version table, "stamping" it with the most recent rev:
from alembic.config import Config
from alembic import command


alembic_cfg = Config(os.path.join(BASE_DIR, "alembic.ini"))
command.stamp(alembic_cfg, "head")
