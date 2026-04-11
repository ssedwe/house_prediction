import os
import sys
import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

from backend.src.logger import logger
from backend.src.exception import CustomException
from backend.src.entity.config_entity import DataIngestionConfig

# Load env variables (for MONGODB_URL)
load_dotenv()

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        """Pulls data from MongoDB and converts to Pandas DataFrame."""
        try:
            logger.info(f"Connecting to MongoDB: {self.config.database_name} -> {self.config.collection_name}")
            
            mongo_url = os.getenv("MONGODB_URL")
            client = MongoClient(mongo_url)
            collection = client[self.config.database_name][self.config.collection_name]

            # Pull data, exclude the MongoDB specific '_id' column
            df = pd.DataFrame(list(collection.find({}, {"_id": 0})))
            
            if df.empty:
                raise Exception("MongoDB collection is empty. Please check your database.")
                
            logger.info(f"Successfully pulled data. Shape: {df.shape}")
            return df
            
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_ingestion(self):
        """Executes the ingestion and splitting process."""
        try:
            logger.info("Starting Data Ingestion Method")
            
            # 1. Get the data
            df = self.export_collection_as_dataframe()

            # 2. Save the raw data
            raw_path = self.config.raw_data_path
            df.to_csv(raw_path, index=False, header=True)
            logger.info(f"Saved raw data to {raw_path}")

            # 3. Train-Test Split
            logger.info("Performing Train-Test Split")
            train_set, test_set = train_test_split(df, test_size=self.config.test_size, random_state=42)

            # 4. Save train and test data
            train_set.to_csv(self.config.train_data_path, index=False, header=True)
            test_set.to_csv(self.config.test_data_path, index=False, header=True)
            
            logger.info(f"Saved train data to {self.config.train_data_path}")
            logger.info(f"Saved test data to {self.config.test_data_path}")

            logger.info("Data Ingestion completed successfully.")
            
        except Exception as e:
            raise CustomException(e, sys)