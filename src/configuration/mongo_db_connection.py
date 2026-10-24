import os
import sys
import pymongo
import certifi

from pathlib import Path
from dotenv import load_dotenv

from src.exception import MyException
from src.logger import logging
from src.constants import DATABASE_NAME, MONGODB_URL_KEY


# ============================================================
# LOAD .ENV
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = ROOT_DIR / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# MONGODB CERTIFICATE
# ============================================================

ca = certifi.where()


class MongoDBClient:

    client = None

    def __init__(self, database_name: str = DATABASE_NAME) -> None:

        try:

            if MongoDBClient.client is None:

                mongo_db_url = os.getenv(MONGODB_URL_KEY)

                if not mongo_db_url:
                    raise Exception(
                        f"Environment variable '{MONGODB_URL_KEY}' is not set."
                    )

                MongoDBClient.client = pymongo.MongoClient(
                    mongo_db_url,
                    tlsCAFile=ca
                )

            self.client = MongoDBClient.client
            self.database = self.client[database_name]
            self.database_name = database_name

            logging.info("MongoDB connection successful.")

        except Exception as e:
            raise MyException(e, sys) from e