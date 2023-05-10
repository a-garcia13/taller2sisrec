import pandas as pd
from pathlib import Path

# Paths
yelp_path = Path("./data/")
yelp_processed_data = Path("./processed_data/")

# Ordered by size
yelp_business = Path(yelp_path, "yelp_academic_dataset_business.json")
yelp_tip = Path(yelp_path, "yelp_academic_dataset_tip.json")
yelp_checkin = Path(yelp_path, "yelp_academic_dataset_checkin.json")
yelp_user = Path(yelp_path, "yelp_academic_dataset_user.json")
yelp_review = Path(yelp_path, "yelp_academic_dataset_review.json")

# Read the business data into a pandas DataFrame
df = pd.read_json(yelp_business, lines=True)

# Create a DataFrame with unique state-city pairs
df_state_city = df[['state', 'city']].drop_duplicates()

# Save the unique state-city pairs to CSV
df_state_city.to_csv('state_city_pairs.csv', index=False)

