from pathlib import Path
from pymongo import MongoClient
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor

# Paths
yelp_path = Path("./data/")
yelp_processed_data = Path("./processed_data/")

# Ordered by size
yelp_business = Path(yelp_path, "yelp_academic_dataset_business.json")
yelp_tip = Path(yelp_path, "yelp_academic_dataset_tip.json")
yelp_checkin = Path(yelp_path, "yelp_academic_dataset_checkin.json")
yelp_user = Path(yelp_path, "yelp_academic_dataset_user.json")
yelp_review = Path(yelp_path, "yelp_academic_dataset_review.json")

# Connect to MongoDB
client = MongoClient("mongodb://inst-newstic:7E69wh96tzcKjK5u3tnFHK7BwbpT2dbU61JsXxVsYdPNTuazAGNBZQPxNo6xaQcDJbxlsIKmiDrhACDbDy1fmg%3D%3D@inst-newstic.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@inst-newstic@")

# Database
db = client['yelp_database']

# Function to load data and insert into MongoDB
def load_data(file_path, collection):
    data = pd.read_json(file_path, lines=True)
    data_dict = data.to_dict("records")
    if isinstance(data_dict, list):
        collection.insert_many(data_dict)
    else:
        collection.insert_one(data_dict)

# Loading data into collections in multiple threads
with ThreadPoolExecutor() as executor:
    executor.submit(load_data, yelp_tip, db.tip)
    executor.submit(load_data, yelp_checkin, db.checkin)
    executor.submit(load_data, yelp_user, db.user)
    executor.submit(load_data, yelp_review, db.review)

# Loading data into collections
# load_data(yelp_business, db.business)
# load_data(yelp_tip, db.tip)
# load_data(yelp_checkin, db.checkin)
# load_data(yelp_user, db.user)
# load_data(yelp_review, db.review)
