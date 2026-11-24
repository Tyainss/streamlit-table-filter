# streamlit-table-filter

A table-based alternative to Streamlit's multiselect widget.

I like building dashboards in Streamlit, but I've never been a big fan of using dropdowns as filters, especially when there are a lot of options to go through.

With `streamlit-table-filter`, you can see your options in a table, select or deselect them with checkboxes, and display extra information alongside each option (e.g. the number of orders per country or plays per artist).

## Installation

```bash
pip install streamlit-table-filter
```

## Getting started

```python
import streamlit as st
from streamlit_table_filter import table_filter

countries = table_filter(
    ["Germany", "France", "Portugal", "Spain"],
    key="countries",
    label="Country",
)

st.write(countries)
```

That's it. You get back a list of the selected values, which you can use to filter your data just as you would with `st.multiselect`.

All options are selected by default. You can select or deselect all of them at once, and your selections are kept across reruns.

## Using a DataFrame

Sometimes it's useful to give users a bit more context before they select an option. For example, when filtering by music genre, you might want to show how many times each genre was played.

```python
import pandas as pd
from streamlit_table_filter import table_filter

genres = pd.DataFrame({
    "genre": ["Rock", "Jazz", "Soul"],
    "plays": [120, 85, 42],
})

selected_genres = table_filter(
    genres,
    key="genres",
    id_column="genre",
    column_config={"genre": "Genre", "plays": "Plays"},
)
```

The filter displays both columns but only returns the values from `id_column`. You can also use a separate ID column and hide it with `display_columns`.

Polars DataFrames work the same way. To install Polars with the package, run `pip install "streamlit-table-filter[polars]"`.

## Using it in a dashboard

Put the filter in the sidebar and use its output to filter your data:

```python
import pandas as pd
import streamlit as st
from streamlit_table_filter import table_filter

sales = pd.DataFrame({
    "country": ["Germany", "France", "Portugal", "Spain"],
    "revenue": [1200, 850, 620, 940],
})

with st.sidebar:
    countries = table_filter(
        sales["country"].unique().tolist(),
        key="countries",
        label="Country",
    )

filtered_sales = sales[sales["country"].isin(countries)]

st.metric("Total revenue", f"€{filtered_sales['revenue'].sum():,.0f}")
st.dataframe(filtered_sales)
```

You can use as many filters as you need. Just give each one a different `key`.

## Customization

Most of the time, you'll only need `options` and `key`. Here are the other options available:

| Parameter | What it does |
| --- | --- |
| `options` | A list of unique, non-null, hashable values, a pandas DataFrame or a Polars DataFrame. |
| `key` | A unique name for the filter (required). |
| `label` | The column heading when passing a list. |
| `id_column` | The column to return values from (required for DataFrames). IDs must be unique, non-null and hashable. |
| `display_columns` | Choose which DataFrame columns to show and in which order. Defaults to all columns. |
| `initial_selection` | Values selected on first render or reset. Defaults to all options. Pass `[]` to start with none. |
| `column_config` | Rename or format columns using Streamlit's column configuration. |
| `selection_label` | Heading of the checkbox column. Defaults to `"Selected"`. |
| `width`, `height` | Table dimensions in pixels. Defaults to Streamlit's sizing behavior. |

If you change the available options, the filter keeps the existing selections that are still available and selects any newly available options. It returns the selected values in the order you supplied them. If nothing is selected, it returns `[]`.

### Resetting a filter

If your dashboard has a reset button, you can restore a filter's initial selection using `reset_table_filter`:

```python
from streamlit_table_filter import reset_table_filter

st.button("Reset countries", on_click=reset_table_filter, args=("countries",))
```

Use this with the filter's key. The reset takes effect the next time the filter is rendered.

## Try it out

The repository includes a small interactive dashboard in `examples/demo.py`. From the repository directory, run:

```bash
pip install .
streamlit run examples/demo.py
```

Requires Python 3.10+ and Streamlit 1.40+. The filter works in sidebars and expanders, but not inside `st.form`.

## License

MIT
