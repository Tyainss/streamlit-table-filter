import pandas as pd
import streamlit as st

from streamlit_table_filter import reset_table_filter, table_filter

st.title("Sales dashboard")
st.write("Use the filters in the sidebar to explore the sales data.")

sales = pd.DataFrame(
    [
        ("Germany", "Electronics", 1200),
        ("Germany", "Clothing", 850),
        ("France", "Electronics", 950),
        ("France", "Home", 700),
        ("Portugal", "Clothing", 620),
        ("Portugal", "Home", 480),
        ("Spain", "Electronics", 1100),
        ("Spain", "Clothing", 940),
    ],
    columns=["country", "category", "revenue"],
)

categories = sales.groupby("category", as_index=False)["revenue"].sum()

with st.sidebar:
    st.header("Filters")
    st.subheader("Countries")
    countries = table_filter(
        sales["country"].unique().tolist(), key="countries", label="Country"
    )
    st.button("Reset countries", on_click=reset_table_filter, args=("countries",))

    st.subheader("Categories")
    selected_categories = table_filter(
        categories,
        key="categories",
        id_column="category",
        column_config={
            "category": "Category",
            "revenue": st.column_config.NumberColumn("Revenue (€)", format="%.0f"),
        },
    )

filtered_sales = sales[
    sales["country"].isin(countries) & sales["category"].isin(selected_categories)
]

st.metric("Total revenue", f"€{filtered_sales['revenue'].sum():,.0f}")
if filtered_sales.empty:
    st.info("Select a country and category to see sales data.")
else:
    st.bar_chart(filtered_sales.groupby("country")["revenue"].sum())
st.dataframe(filtered_sales, hide_index=True)
