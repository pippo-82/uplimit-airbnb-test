import os
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from geopy.geocoders import Nominatim
from PIL import Image
import airbnb

################################
# FUNCTIONS
################################
def dataframe_with_selections(df):
    # given a dataframe, catches user selection
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    return edited_df[edited_df.Select].drop('Select', axis=1)

def getLocationDisplayNameByDF(selected_df):
    # initialize var
    addresses = []
    for r in np.arange(selected_df.shape[0]):
        # sample coords tuple = (52.509669, 13.376294)
        coords = (selected_df['Latitude'].tolist()[r],selected_df['Longitude'].tolist()[r])
        geolocator = Nominatim(user_agent="PP_get_location")
        location = geolocator.reverse(coords)

        listing_id = selected_df['Airbnb Listing ID'].tolist()[r]
        rating = get_airbnb_rating(listing_id)
        addresses.append([listing_id,"⭐" * rating,location.raw["display_name"]])

    return pd.DataFrame(addresses, columns=["Airbnb Listing ID","Rating","Address"])

def get_airbnb_rating(listing_id,offset=0,limit_results=20):
    # clean listing_id
    listing_id = int(str(listing_id).replace(".",""))
    # initialize Api for calls
    api = airbnb.Api()
    # get reviews for a given AirBnb listing id
    reviews = api.get_reviews(listing_id=listing_id,offset=offset,limit=limit_results)
    # display all reviews ratings
    ratings = [reviews['reviews'][r]['rating'] for r in range(len(reviews['reviews']))]
    # get average rating
    avg_rating = np.average(np.array(ratings)).astype(int)
    return avg_rating


################################
# CODE
################################


# ========================================= CREATE DATAFRAME FROM CSV  =========================================

# Read dataframe
dataframe = pd.read_csv(
    "WK1_Airbnb_Amsterdam_listings_proj_solution.csv",
    names=[
        "Airbnb Listing ID",
        "Price",
        "Latitude",
        "Longitude",
        "Dist.(m) from loc.",
        "Location",
    ],
)

# set page layout as wide
st.set_page_config(layout="wide")

# ========================================= SET UP THE WEBPAGE SIDEBAR  =========================================

# --- SET SIDEBAR COMPOSITION
with st.sidebar:
    ########################################
    # USER INPUTS
    ########################################

    st.write("FILTER THE DATA PER YOUR CHOICE")
    # Let user enter the max budget per night, default 100 pounds
    max_budget = st.number_input('Insert your max budget per night',value=100, step=5)
    # Let user enter the max distance from location, default 1000 mt
    max_distance = st.number_input('Insert the max distance from chosen location',value=1000, step=20)

    st.divider()
    st.markdown('<p class="small-font">Last Updated: 24/09/2023</p>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<p class="small-font">Coding and template by Paolo Pozzoli</p>', unsafe_allow_html=True)

    img_pp = Image.open(os.getcwd() + "/pp.jpg")

    st.image(img_pp,
            caption='Follow me on LinkedIn - https://www.linkedin.com/in/paolo-pozzoli-9bb5a183/',
            width=200)



# ========================================= SET UP THE MAIN CONTENTS FOR EACH SELECTION  =========================================

# Display title and text
col1, mid, col2 = st.columns([5,1,20])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/31/NumPy_logo_2020.svg", width=200)
with col2:
    st.title("Week 1 - Data and visualization")

# ========================================= CREATE 3 TABS TO DISPLAY DATA  ========================================================

tab1_intro, tab2_data_analysis, tab3_extras = st.tabs(["🏁 INTRO", "🔍 Data Analysis", "⭐ Extras"])

with tab1_intro:

    st.header("A walk through Amsterdam, Netherlands")
    # Display city image
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/KeizersgrachtReguliersgrachtAmsterdam.jpg/1280px-KeizersgrachtReguliersgrachtAmsterdam.jpg",\
        caption="source: https://en.wikipedia.org/wiki/Amsterdam")
    # Advices for tourists
    st.write("💡 Other amenities and activities you might like around the city")
    st.write("https://www.thetimes.co.uk/travel/destinations/europe/netherlands/amsterdam/best-things-to-do-in-amsterdam")

with tab2_data_analysis:
    # split data in 2 columns of given size (column 1 = data frame, column 2 = user selected records)
    col1_table_map, col2_selection_address = st.columns([3, 2])

    with col1_table_map:
        st.markdown("Here we can see the dataframe created during this weeks project.")
        # filter dataframe for locations with Price equal or below max_budget
        dataframe = dataframe[dataframe["Price"] <= max_budget]
        # filter dataframe for locations with distance equal or below max_distance
        dataframe = dataframe[dataframe["Dist.(m) from loc."] <= max_distance]

        # Display as integer
        dataframe["Airbnb Listing ID"] = dataframe["Airbnb Listing ID"].astype(int)
        # Round of values
        dataframe["Price"] = "£ " + dataframe["Price"].round(2).astype(str) # <--- CHANGE THIS POUND SYMBOL IF YOU CHOSE CURRENCY OTHER THAN POUND
        # Rename the number to a string
        dataframe["Location"] = dataframe["Location"].replace(
            {1.0: "To visit", 0.0: "Airbnb listing"}
        )

        selection = dataframe_with_selections(dataframe)

    st.markdown("Below is a map showing all the Airbnb listings with a red dot and the location we've chosen with a blue dot.")
    # Create the plotly express figure
    fig = px.scatter_mapbox(
        dataframe,
        lat="Latitude",
        lon="Longitude",
        color="Location",
        color_discrete_sequence=["blue", "red"],
        zoom=11,
        height=500,
        width=800,
        hover_name="Price",
        hover_data=["Dist.(m) from loc.", "Location"],
        labels={"color": "Locations"},
    )
    fig.update_geos(center=dict(lat=dataframe.iloc[0][2], lon=dataframe.iloc[0][3]))
    fig.update_layout(mapbox_style="stamen-terrain")

    with col2_selection_address:
        st.write("Your selection location:")
        if selection.shape[0] == 0:
            st.write("")
        else:
            st.write(getLocationDisplayNameByDF(selection))

    # Show the figure
    st.plotly_chart(fig, use_container_width=True)


with tab3_extras:

    with st.expander("Prettymaps picture of Amsterdam city"):
        img_ams = Image.open(os.getcwd() + "\\Amsterdam_Prettymaps_Macao.png")
        st.image(img_ams)
    with st.expander("Prettymaps picture of Amsterdam city center"):
        img_ams_center = Image.open(os.getcwd() + "\\Amsterdam_Prettymaps_Tijuca.png")
        st.image(img_ams_center)
    with st.expander("Openstreetmap picture of Amsterdam streets"):
        img_ams_streets = Image.open(os.getcwd() + "\\Amsterdam_StreetMap.png")
        st.image(img_ams_streets)

    with st.expander("List of touristic buildings in Amsterdam"):
        locations = ['150 KV PLANT SCIENCE PARK',
                    'A&O Amsterdam Zuidoost',
                    'Amstel Botel',
                    'BOAT & CO',
                    'Baksteen sculptuur en vijver',
                    'Bastion Hotel Amsterdam Noord',
                    'Best Western',
                    'Beurs van Berlage',
                    'Bilderberg Garden Hotel',
                    'Campanile',
                    'CitizenM',
                    'Conservatorium',
                    'Corendon City Hotel Amsterdam',
                    'Crowne Plaza Amsterdam-South',
                    'De Cornelia',
                    'De Gouden Spiegel en De Silveren Spiegel',
                    'De Hallen',
                    'De Looier',
                    'DoubleTree by Hilton Amsterdam Centraal Station',
                    'Drie-klimaten-kas',
                    'Dutch Design Hotel Artemis',
                    'Dutchies Hostel',
                    'EYE Filminstituut',
                    'Element Amsterdam',
                    'Felix Meritis',
                    'Fine Seasons',
                    'Fo Guang Sha He Hua Temple',
                    'Frederik Park House',
                    'Gemeenlandshuis',
                    'Generator',
                    'Haarlemmermeerstation',
                    'Haarlemmerpoort',
                    'Herberg Het Mandelahuisje',
                    'Het Huis met den Hoofden',
                    'Het Scheepvaartmuseum',
                    'Hilton Amsterdam',
                    'Holiday Inn',
                    'Holiday Inn Express Amsterdam - North Riverside',
                    'Hollandsche Manege',
                    'Hotel 83',
                    'Hotel Cosmos',
                    'Hotel The Exchange',
                    'House of Bols',
                    'Huis Bartolotti',
                    'Huis De Pinto',
                    'Huis aan 3 grachten',
                    'Ibis Amsterdam City West',
                    'Inntel Hotels Amsterdam Landmark',
                    'Joods Museum',
                    'Joy Hotel',
                    'Koninklijk Instituut voor de Tropen',
                    'Koninklijk Paleis',
                    'Leonardo Royal Hotel Amsterdam',
                    'Mansion',
                    'Molen van Sloten',
                    'Montelbaanstoren',
                    'Motel One',
                    'Munttoren',
                    'Museum Noord',
                    'Museum Perron Oost',
                    'NH Tropen Hotel',
                    'Nieuwzijds Kapel',
                    'OZO Hotels Arena Amsterdam',
                    'Oost-Indisch Huis',
                    'Oude Kerk',
                    'Pink Point',
                    'Pollux',
                    'Portugese Synagoge',
                    'Postillion',
                    'Room Mate Aitana Hotel',
                    'Rooms25',
                    'Scheepvaarthuis',
                    'Schreierstoren',
                    'Sint Nicolaaskerk',
                    'Sint Olofskapel',
                    'Stedelijk Museum Amsterdam',
                    'The Delphi - Amsterdam Townhouse - hotel',
                    'The Social Hub',
                    'Trippenhuis',
                    'Van Gogh Museum',
                    'Vlinderkas',
                    'Waag',
                    'Waldorf Astoria Amsterdam',
                    "Werf 't Kromhout",
                    'West-Indisch Pakhuis',
                    'WestCord Art Hotel',
                    'Westerkerk',
                    'Westertoren',
                    'Zuiderkerk',
                    'ibis Amsterdam Centre']
        # create bullet point from list with markdown
        st.markdown("- " + "\n- ".join(locations))
