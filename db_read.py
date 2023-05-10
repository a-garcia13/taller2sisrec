from pymongo import MongoClient
import pandas as pd

# Connect to MongoDB
client = MongoClient("mongodb://inst-newstic:7E69wh96tzcKjK5u3tnFHK7BwbpT2dbU61JsXxVsYdPNTuazAGNBZQPxNo6xaQcDJbxlsIKmiDrhACDbDy1fmg%3D%3D@inst-newstic.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@inst-newstic@")

# Database
db = client['yelp_database']

# Load data from MongoDB into DataFrames
df_business = pd.DataFrame(list(db.business.find()))
df_tip = pd.DataFrame(list(db.tip.find()))
df_checkin = pd.DataFrame(list(db.checkin.find()))
df_user = pd.DataFrame(list(db.user.find()))
df_review = pd.DataFrame(list(db.review.find()))

# Now you have the data in pandas dataframes and you can start working with it
print(df_business.head())
print(df_tip.head())
print(df_checkin.head())
print(df_user.head())
print(df_review.head())


