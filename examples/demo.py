import pandas as pd
import streamlit as st

from streamlit_table_filter import reset_table_filter, table_filter

st.title("Dunder Mifflin Sales Dashboard")
st.write("The People Person's Paper People.")

sales = pd.DataFrame(
    [
        ("Scranton", "Dwight", 85000),
        ("Scranton", "Jim", 72000),
        ("Scranton", "Stanley", 54000),
        ("Scranton", "Phyllis", 48000),
        ("Scranton", "Andy", 12000),
        ("Stamford", "Jim", 32000),
        ("Stamford", "Andy", 8000),
        ("Stamford", "Karen", 42000),
        ("Utica", "Karen", 58000),
        ("Nashua", "A.J.", 36000),
    ],
    columns=["branch", "employee", "revenue"],
)

employees = sales.groupby("employee", as_index=False)["revenue"].sum()

with st.sidebar:
    st.header("Filters")
    st.subheader("Branches")
    branches = table_filter(
        sales["branch"].unique().tolist(),
        key="branches",
        label="Branch",
    )
    st.button("Reset branches", on_click=reset_table_filter, args=("branches",))

    st.subheader("Salespeople")
    selected_employees = table_filter(
        employees,
        key="employees",
        id_column="employee",
        column_config={
            "employee": "Employee",
            "revenue": st.column_config.NumberColumn("Revenue ($)", format="%.0f"),
        },
    )

filtered_sales = sales[
    sales["branch"].isin(branches) & sales["employee"].isin(selected_employees)
]

st.metric("Total revenue", f"${filtered_sales['revenue'].sum():,.0f}")

if filtered_sales.empty:
    st.info("Select a branch and employee to see sales data.")
else:
    st.bar_chart(filtered_sales.groupby("branch")["revenue"].sum())

st.dataframe(filtered_sales, hide_index=True)
st.caption("Fictional sales data inspired by The Office.")
