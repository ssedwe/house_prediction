import os
import sys
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

from src.logger import logger
from src.exception import CustomException
from src.utils.common import read_yaml_file


# Load env
load_dotenv()

# Load config once
CONFIG = read_yaml_file("config/config.yaml")


def load_data(file_path: str) -> pd.DataFrame:
    try:
        logger.info("Loading data from CSV file")

        df = pd.read_csv(file_path)

        logger.info(f"Data loaded successfully with shape: {df.shape}")
        return df

    except Exception as e:
        raise CustomException(e, sys)


def get_mongo_client():
    try:
        mongo_url = os.getenv("MONGODB_URL")

        if not mongo_url:
            raise Exception("MONGODB_URL not found in environment variables")

        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)

        logger.info("MongoDB connection established successfully")

        return client

    except Exception as e:
        raise CustomException(e, sys)


def push_data_to_mongo(df: pd.DataFrame):
    try:
        logger.info("Starting data push to MongoDB")

        db_name = CONFIG["data_ingestion"]["database_name"]
        collection_name = CONFIG["data_ingestion"]["collection_name"]

        client = get_mongo_client()

        database = client[db_name]
        collection = database[collection_name]

        # safer than drop()
        collection.delete_many({})
        logger.info(f"Cleared existing data from '{collection_name}'")

        records = df.to_dict(orient="records")

        result = collection.insert_many(records)

        logger.info(f"Inserted {len(result.inserted_ids)} records into MongoDB")

    except Exception as e:
        raise CustomException(e, sys)


if __name__ == "__main__":
    try:
        FILE_PATH = "data/houses.csv"

        df = load_data(FILE_PATH)
        push_data_to_mongo(df)

        logger.info("Data successfully uploaded to MongoDB")

    except Exception as e:
        raise CustomException(e, sys)