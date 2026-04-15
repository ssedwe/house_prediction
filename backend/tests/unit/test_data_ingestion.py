import os
import pytest
import pandas as pd
from pymongo import MongoClient
from backend.src.components.data_ingestion import DataIngestion
from backend.src.entity.config_entity import DataIngestionConfig

# ==============================================================
# ARRANGE: THE MONGODB FIXTURE
# ==============================================================
@pytest.fixture
def setup_ingestion_environment():
    """
    Creates a temporary MongoDB connection, injects 5 realistic fake houses 
    matching your houses.csv schema, and sets up dummy file paths.
    """
    # 1. Force the environment variable to point to a local test database
    # Your code uses os.getenv("MONGODB_URL"), so we override it here safely
    test_mongo_url = "mongodb://localhost:27017"
    os.environ["MONGODB_URL"] = test_mongo_url
    
    # 2. Connect to the test database
    client = MongoClient(test_mongo_url)
    db_name = "test_house_database"
    col_name = "test_house_collection"
    
    db = client[db_name]
    collection = db[col_name]
    
    # Clear the collection just in case a previous test crashed
    collection.delete_many({})
    
    # 3. Inject 5 fake rows of data matching your exact houses.csv schema
    fake_data = [
        {'bedrooms': 3, 'bathrooms': 1.0, 'sqft_living': 1180, 'sqft_lot': 5650, 'floors': 1.0, 'waterfront': 0, 'view': 0, 'condition': 3, 'grade': 7, 'sqft_above': 1180, 'sqft_basement': 0, 'yr_built': 1955, 'yr_renovated': 0, 'zipcode': 98178, 'lat': 47.5112, 'long': -122.257, 'sqft_living15': 1340, 'price': 22.19},
        {'bedrooms': 3, 'bathrooms': 2.25, 'sqft_living': 2570, 'sqft_lot': 7242, 'floors': 2.0, 'waterfront': 0, 'view': 0, 'condition': 3, 'grade': 7, 'sqft_above': 2170, 'sqft_basement': 400, 'yr_built': 1951, 'yr_renovated': 1991, 'zipcode': 98125, 'lat': 47.721, 'long': -122.319, 'sqft_living15': 1690, 'price': 53.8},
        {'bedrooms': 2, 'bathrooms': 1.0, 'sqft_living': 770, 'sqft_lot': 10000, 'floors': 1.0, 'waterfront': 0, 'view': 0, 'condition': 3, 'grade': 6, 'sqft_above': 770, 'sqft_basement': 0, 'yr_built': 1933, 'yr_renovated': 0, 'zipcode': 98028, 'lat': 47.7379, 'long': -122.233, 'sqft_living15': 2720, 'price': 18.0},
        {'bedrooms': 4, 'bathrooms': 3.0, 'sqft_living': 1960, 'sqft_lot': 5000, 'floors': 1.0, 'waterfront': 0, 'view': 0, 'condition': 5, 'grade': 7, 'sqft_above': 1050, 'sqft_basement': 910, 'yr_built': 1965, 'yr_renovated': 0, 'zipcode': 98136, 'lat': 47.5208, 'long': -122.393, 'sqft_living15': 1360, 'price': 60.4},
        {'bedrooms': 3, 'bathrooms': 2.0, 'sqft_living': 1680, 'sqft_lot': 8080, 'floors': 1.0, 'waterfront': 0, 'view': 0, 'condition': 3, 'grade': 8, 'sqft_above': 1680, 'sqft_basement': 0, 'yr_built': 1987, 'yr_renovated': 0, 'zipcode': 98074, 'lat': 47.6168, 'long': -122.045, 'sqft_living15': 1800, 'price': 51.0}
    ]
    collection.insert_many(fake_data)
    
    # 4. Create the dummy Config Entity matching your exact attributes
    # We use a temporary "tests/dummy_artifacts" folder
    os.makedirs("tests/dummy_artifacts", exist_ok=True)
    
    config = DataIngestionConfig(
        artifact_dir="tests/dummy_artifacts",
        database_name=db_name,
        collection_name=col_name,
        raw_data_path="tests/dummy_artifacts/raw.csv",
        train_data_path="tests/dummy_artifacts/train.csv",
        test_data_path="tests/dummy_artifacts/test.csv",
        test_size=0.2 # 20% of 5 rows = 1 test row, 4 train rows
    )
    
    yield config
    
    # ==============================================================
    # TEARDOWN: CLEANUP AFTER THE TEST
    # ==============================================================
    # Drop the fake database
    client.drop_database(db_name)
    client.close()
    
    # Delete the generated CSV files
    for file in [config.raw_data_path, config.train_data_path, config.test_data_path]:
        if os.path.exists(file):
            os.remove(file)
            
    # Remove the dummy folder
    if os.path.exists("tests/dummy_artifacts"):
        os.rmdir("tests/dummy_artifacts")


# ==============================================================
# ACT & ASSERT: THE ACTUAL TESTS
# ==============================================================
def test_data_ingestion_creates_files(setup_ingestion_environment):
    """
    Tests if the DataIngestion component successfully pulls from MongoDB,
    splits the data, and saves all 3 CSV files to the hard drive.
    """
    config = setup_ingestion_environment
    ingestion = DataIngestion(config=config)
    
    # ACT: Run your code!
    ingestion.initiate_data_ingestion()
    
    # ASSERT 1: Did it create all the files?
    assert os.path.exists(config.raw_data_path) == True
    assert os.path.exists(config.train_data_path) == True
    assert os.path.exists(config.test_data_path) == True
    
    # ASSERT 2: Is the math for the Train/Test split correct?
    train_df = pd.read_csv(config.train_data_path)
    test_df = pd.read_csv(config.test_data_path)
    raw_df = pd.read_csv(config.raw_data_path)
    
    # 5 rows total -> 4 train, 1 test (because test_size is 0.2)
    assert len(raw_df) == 5
    assert len(train_df) == 4
    assert len(test_df) == 1
    
    # ASSERT 3: Did MongoDB accidentally include the '_id' column?
    # Your code explicitly excludes it: list(collection.find({}, {"_id": 0}))
    assert "_id" not in raw_df.columns