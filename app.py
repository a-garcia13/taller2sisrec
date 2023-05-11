import streamlit as st
import pandas as pd
from pymongo import MongoClient
from streamlit_card import card
from pathlib import Path
import pickle
from geopy.geocoders import Nominatim
import folium
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split
from surprise import Dataset, Reader

# Establish connection to MongoDB
client = MongoClient(
    "mongodb://inst-newstic:7E69wh96tzcKjK5u3tnFHK7BwbpT2dbU61JsXxVsYdPNTuazAGNBZQPxNo6xaQcDJbxlsIKmiDrhACDbDy1fmg%3D%3D@inst-newstic.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@inst-newstic@")
db = client['yelp_database']
user_collection = db['user']
business_collection = db['business']
review_collection = db['review']

# Paths
yelp_path = Path("./data/")
yelp_processed_data = Path("./processed_data/")

# Ordered by size
yelp_business = Path(yelp_path, "yelp_academic_dataset_business.json")
yelp_tip = Path(yelp_path, "yelp_academic_dataset_tip.json")
yelp_checkin = Path(yelp_path, "yelp_academic_dataset_checkin.json")
yelp_user = Path(yelp_path, "yelp_academic_dataset_user.json")
yelp_review = Path(yelp_path, "yelp_academic_dataset_review.json")


# Function to load data and insert into MongoDB
def read_data(file_path):
    return pd.read_json(file_path, lines=True)

business_data = read_data(yelp_business)
print("business_data loaded")
review_data = read_data(yelp_review)
print("review loaded", review_data.shape[0])
# Load the trained model
best_model = pickle.load(open('models/model_SVD.pkl', 'rb'))
df_train, df_temp = train_test_split(review_data, test_size=0.2, random_state=42)
# The columns must correspond to user id, item id and ratings (in that order).
# Se establece el rango en el cual se aceptaran los ratings
reader = Reader( rating_scale = ( 1, 5 ) )
data_train = Dataset.load_from_df(df_train[['user_id', 'business_id', 'stars']], reader)
train_data = data_train.build_full_trainset()
best_model.fit(train_data)

def get_reviews(user_info):
    # Filter the review_data DataFrame for rows where the user_id matches user_info
    latest_review = review_data[review_data['user_id'] == user_info]
    # Sort the DataFrame by date in descending order and return the top 5 rows
    return latest_review.head(5)


def get_all_predictions(user_id):
    # Get a list of all item ids
    iids = business_data['business_id'].unique()

    # Get a list of ids that the user has rated
    iids_user_rated = review_data.loc[review_data['user_id'] == user_id, 'business_id'].values

    # Remove the ids that the user has rated from the list of all item ids
    iids_to_pred = np.setdiff1d(iids, iids_user_rated)

    # Predict the rating for all items that the user hasn't rated yet
    predictions = [best_model.predict(user_id, iid) for iid in iids_to_pred]

    # return predictions in form of dataframe
    return pd.DataFrame(predictions).head(10)


def get_top_n_similar(n, item_id, item_factors):
    # Fit nearest neighbors
    knn = NearestNeighbors(n_neighbors=n + 1)  # +1 because the item is most similar to itself
    knn.fit(item_factors)

    # Get neighbors indices
    distances, indices = knn.kneighbors(item_factors[item_id].reshape(1, -1))

    # Exclude the item itself
    return indices[0][1:]


def get_top_n_similar_users(n, user_id, user_factors):
    # Fit nearest neighbors
    knn = NearestNeighbors(n_neighbors=n + 1)  # +1 because the user is most similar to himself/herself
    knn.fit(user_factors)

    # Get neighbors indices
    distances, indices = knn.kneighbors(user_factors[user_id].reshape(1, -1))

    # Exclude the user itself
    return indices[0][1:]


def get_recomendations_by_item(outer_item_id):
    # Assume best_model is your trained SVD model
    item_factors = best_model.qi

    item_id = train_data.to_inner_iid(outer_item_id)

    # Get top 5 similar items for item with ID 10
    similar_items = get_top_n_similar(5, item_id, item_factors)
    # Transform inner item IDs to raw item IDs
    similar_items_raw = [train_data.to_raw_iid(i) for i in similar_items]
    return similar_items_raw

def get_recomendations_by_user(user_id):
    # Assume best_model is your trained SVD model
    user_factors = best_model.pu

    user_id = train_data.to_inner_uid(user_id)

    # Get top 5 similar users for user with ID 20
    similar_users = get_top_n_similar_users(5, user_id, user_factors)
    # Transform inner user IDs to raw user IDs
    similar_users_raw = [train_data.to_raw_uid(i) for i in similar_users]
    return similar_users_raw


def show_user_info(user_name):
    user_info = user_collection.find_one({"user_id": user_name})

    if user_info:
        st.header(f"Welcome: {user_info['name']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Profile information:")
            st.write("User since:", user_info['yelping_since'])
            st.write("Number of friends:", len(user_info['friends']))
            st.write("Fans:", user_info['fans'])
            st.write("You give an average of ", user_info['average_stars'], "stars")

        with col2:
            st.subheader("Reviews:")
            st.write("Number of reviews:", user_info['review_count'])
            st.write("Useful reviews:", user_info['useful'])
            st.write("Funny reviews:", user_info['funny'])
            st.write("Cool reviews:", user_info['cool'])
            st.write('Your latest reviews:')
            reviews_by_user = get_reviews(user_name)
            st.write(reviews_by_user)

        with col3:
            st.subheader("Compliments:")
            st.write("Hot:", user_info['compliment_hot'])
            st.write("More:", user_info['compliment_more'])
            st.write("Profile:", user_info['compliment_profile'])
            st.write("Cute:", user_info['compliment_cute'])
            st.write("List:", user_info['compliment_list'])
            st.write("Note:", user_info['compliment_note'])
            st.write("Plain:", user_info['compliment_plain'])
            st.write("Cool:", user_info['compliment_cool'])
            st.write("Funny:", user_info['compliment_funny'])
            st.write("Writer:", user_info['compliment_writer'])
            st.write("Photos:", user_info['compliment_photos'])

        st.header("Recommendations based on your reviews:")
        col4, col5, col6 = st.columns(3)

        with col4:
            st.subheader('Based on your prior recommendations:')
            top_recommendations = get_all_predictions(user_name)
            st.write(top_recommendations)

        with col5:
            latest_review = business_collection.find_one({'business_id': reviews_by_user.iloc[0]['business_id']})
            st.subheader(f'Because you reviewed', latest_review['name'])
            recommendations_by_item = get_recomendations_by_item(latest_review['business_id'])
            for items in recommendations_by_item:
                item = business_collection.find_one({'business_id': items})
                if item:
                    st.write(item)

        with col6:
            recommendations_by_user = get_recomendations_by_user(user_name)
            st.subheader('Because', recommendations_by_user[0], 'likes similar things to you:')
            reviews_by_similar_user = get_all_predictions(recommendations_by_user[0])
            st.write(reviews_by_similar_user)
    else:
        st.write("User not found. Please enter a valid user id.")


def show_city_locations(city, state):
    query = {'city': city, 'state': state}

    nearby_locations = business_collection.find(query)

    # Create DataFrame from MongoDB query
    df = pd.DataFrame(list(nearby_locations))

    # Rename latitude and longitude columns
    df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})

    if not df.empty:
        st.map(df)
        return df
    else:
        st.write("No business found on", city, ",", state)
        return None


def search_by_attribute(city, state, attribute):
    query = {'city': city, 'state': state, 'attribute': {f'{attribute}': True}}

    nearby_locations = business_collection.find(query)

    # Create DataFrame from MongoDB query
    df = pd.DataFrame(list(nearby_locations))

    # Rename latitude and longitude columns
    df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})

    if not df.empty:
        return df
    else:
        return None


def main():
    st.title("Business finder App")

    # Load state and city pairs from CSV
    df_state_city = pd.read_csv('state_city_pairs.csv')
    states = df_state_city['state'].unique().tolist()
    states.sort()

    st.header("Enter User id")
    user_name = st.text_input("User id")

    if user_name:
        show_user_info(user_name)

        st.header("Search Business by city and state")
        selected_state = st.selectbox("State", states)
        if selected_state:
            cities = df_state_city[df_state_city['state'] == selected_state]['city'].unique().tolist()
            cities.sort()
            selected_city = st.selectbox("City", cities)

            if selected_city:
                business_df = show_city_locations(selected_city, selected_state)
                if business_df is not None:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Recommended by starts:")
                        # Sort DataFrame by 'stars' in descending order
                        df_sorted = business_df.sort_values(by='stars', ascending=False)
                        # Get the top 5
                        top_5 = df_sorted.head(3)
                        for index, row in top_5.iterrows():
                            card(
                                title=row['name'],
                                text=f"stars:{row['stars']}\n address:{row['address']}\n",
                                image="http://placekitten.com/200/300"
                            )

                    with col2:
                        st.subheader("Recommended by reviews:")
                        # Sort DataFrame by 'stars' in descending order
                        df_sorted = business_df.sort_values(by='review_count', ascending=False)
                        # Get the top 5
                        top_5 = df_sorted.head(3)
                        for index, row in top_5.iterrows():
                            card(
                                title=row['name'],
                                text=f"Review count:{row['review_count']}\n address:{row['address']}\n",
                                image="http://placekitten.com/200/300"
                            )


if __name__ == "__main__":
    main()
