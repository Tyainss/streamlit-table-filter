import pandas as pd
import streamlit as st

from streamlit_table_filter import reset_table_filter, table_filter

st.title("Streamlit table filter")

with st.sidebar:
    st.header("Countries")
    more_countries = st.checkbox("Include Spain")
    country_options = ["DE", "FR", "PT"]
    if more_countries:
        country_options.append("ES")

    selected_countries = table_filter(
        country_options, key="countries", label="Country", initial_selection=["PT"]
    )
    st.button("Reset countries", on_click=reset_table_filter, args=("countries",))
    st.write("Selected country codes", selected_countries)

st.header("Genres")
genres = pd.DataFrame(
    {"genre_id": [1, 2, 3], "genre": ["Jazz", "Rock", "Soul"], "plays": [12, 28, 9]}
)
selected_genres = table_filter(
    genres,
    key="genres",
    id_column="genre_id",
    display_columns=["genre", "plays"],
    column_config={"genre": "Genre", "plays": "Plays"},
)
st.write("Selected genre IDs", selected_genres)
