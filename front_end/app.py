import streamlit as st
import pandas as pd
from pymongo import MongoClient
from streamlit_card import card
from geopy.geocoders import Nominatim
import folium

# Establish connection to MongoDB
client = MongoClient("mongodb://inst-newstic:7E69wh96tzcKjK5u3tnFHK7BwbpT2dbU61JsXxVsYdPNTuazAGNBZQPxNo6xaQcDJbxlsIKmiDrhACDbDy1fmg%3D%3D@inst-newstic.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@inst-newstic@")
db = client['yelp_database']
user_collection = db['user']
business_collection = db['business']

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
