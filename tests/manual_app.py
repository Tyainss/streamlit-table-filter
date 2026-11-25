"""Manual browser checks: uv run streamlit run tests/manual_app.py."""

from importlib.util import find_spec

import pandas as pd
import streamlit as st

from streamlit_table_filter import reset_table_filter, table_filter

st.title("Table filter - manual tests")

with st.sidebar:
    st.header("Test controls")
    scenario = st.selectbox(
        "Options",
        ["Original", "Reordered", "Single row", "Empty", "100 rows"],
    )
    update_values = st.checkbox(
        "Double item values",
        help="Values double while the items and their selections stay unchanged.",
    )
    width = st.selectbox("Width (px)", [None, 300, 500])
    height = st.selectbox("Height (px)", [None, 120, 250])
    backend = st.radio("DataFrame type", ["pandas", "Polars"])
    st.button("Reset selection", on_click=reset_table_filter, args=("manual",))

ids = {
    "Original": [1, 2, 3, 4, 5],
    "Reordered": [5, 4, 3, 2, 1],
    "Single row": [2],
    "Empty": [],
    "100 rows": list(range(1, 101)),
}[scenario]

if backend == "Polars" and find_spec("polars") is None:
    st.info("Install optional Polars support: uv sync --extra polars")
    st.stop()

# Explicit dtypes also keep the empty DataFrame schema consistent.
frame = pd.DataFrame(
    {
        "id": pd.Series(ids, dtype="int64"),
        "name": pd.Series([f"Item {i}" for i in ids], dtype="str"),
        "value": pd.Series(
            [i * (20 if update_values else 10) for i in ids], dtype="int64"
        ),
    }
)
options = frame
if backend == "Polars":
    import polars as pl

    options = pl.from_pandas(frame)

st.caption("Initial selection: IDs 2 and 4. Reset restores it for available IDs.")
selected = table_filter(
    options,
    key="manual",
    id_column="id",
    display_columns=["name", "value"],
    initial_selection=[2, 4],
    column_config={"name": "Item", "value": "Value"},
    width=width,
    height=height,
)
st.write("Selected IDs (input order):", selected)
