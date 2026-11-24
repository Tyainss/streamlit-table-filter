import importlib.util
import json

import pytest
from streamlit.testing.v1 import AppTest

APP_START_TIMEOUT = 10


def test_bulk_selection_reset_and_dynamic_options():
    app = AppTest.from_string("""
import streamlit as st
from streamlit_table_filter import reset_table_filter, table_filter

mode = st.selectbox("Options", ["original", "changed", "empty"])
options = {"original": ["DE", "PT"], "changed": ["PT", "FR"], "empty": []}
st.button("Reset", on_click=reset_table_filter, args=("countries",))
selected = table_filter(options[mode], key="countries", initial_selection=["DE"])
st.text(str(selected))
st.text(str(table_filter(["rock"], key="genres")))
""").run(timeout=APP_START_TIMEOUT)

    assert_selection(app, "['DE']", "['rock']")
    assert_selection(app.checkbox[0].check().run(), "['DE', 'PT']", "['rock']")
    assert_selection(app.checkbox[0].uncheck().run(), "[]", "['rock']")
    assert_selection(app.selectbox[0].select("changed").run(), "['FR']", "['rock']")
    assert_selection(app.button[0].click().run(), "[]", "['rock']")
    assert_selection(app.selectbox[0].select("empty").run(), "[]", "['rock']")
    assert app.caption[0].value == "No options available."
    assert_selection(
        app.selectbox[0].select("original").run(), "['DE', 'PT']", "['rock']"
    )


def test_row_edits_revert_and_follow_ids_when_display_changes():
    app = AppTest.from_string("""
import pandas as pd
import streamlit as st
from streamlit_table_filter import table_filter

changed = st.checkbox("Reorder and rename")
frame = pd.DataFrame({"id": [2, 1], "label": ["Rock", "Soul"]})
if changed:
    frame = frame.iloc[::-1].assign(label=["Soul (updated)", "Rock"])
selected = table_filter(frame, key="genres", id_column="id", display_columns=["label"])
st.text(str(selected))
""").run(timeout=APP_START_TIMEOUT)

    assert_selection(app, "[2, 1]")
    assert app.dataframe[0].value.columns[1:].tolist() == ["label"]
    edit_first_table(app, {0: False})
    assert_selection(app, "[1]")
    edit_first_table(app, {})
    assert_selection(app, "[2, 1]")
    edit_first_table(app, {0: False})
    assert_selection(app.checkbox[0].check().run(), "[1]")
    assert app.dataframe[0].value.iloc[:, 0].tolist() == [True, False]
    assert app.dataframe[0].value["label"].tolist() == ["Soul (updated)", "Rock"]


def test_dimensions_and_selection_count():
    app = AppTest.from_string("""
import streamlit as st
from streamlit_table_filter import table_filter

larger = st.checkbox("Larger table")
selected = table_filter(
    ["DE", "PT"], key="countries", width=300, height=250 if larger else 150
)
st.text(str(selected))
""").run(timeout=APP_START_TIMEOUT)
    assert_selection(app, "['DE', 'PT']")
    assert app.caption[0].value == "2 of 2 selected"
    edit_first_table(app, {0: False})
    assert_selection(app, "['PT']")
    assert app.caption[0].value == "1 of 2 selected"
    assert_selection(app.checkbox[0].check().run(), "['PT']")
    assert app.dataframe[0].value.iloc[:, 0].tolist() == [False, True]
    assert_selection(app.checkbox[1].check().run(), "['DE', 'PT']")
    assert app.caption[0].value == "2 of 2 selected"
    assert_selection(app.checkbox[1].uncheck().run(), "[]")
    assert app.caption[0].value == "0 of 2 selected"


@pytest.mark.skipif(
    importlib.util.find_spec("polars") is None, reason="Polars is optional"
)
def test_polars_returns_raw_ids():
    app = AppTest.from_string("""
import polars as pl
import streamlit as st
from streamlit_table_filter import table_filter

frame = pl.DataFrame({"id": [7, 2], "label": ["Pop", "Jazz"], "plays": [42, None]})
selected = table_filter(
    frame, key="genres", id_column="id", display_columns=["label", "plays"],
    initial_selection=[],
)
st.text(str(selected))
""").run(timeout=APP_START_TIMEOUT)
    assert_selection(app, "[]")
    edit_first_table(app, {1: True})
    assert_selection(app, "[2]")


def assert_selection(app, *expected):
    assert not app.exception
    assert [element.value for element in app.text] == list(expected)


def edit_first_table(app, edits):
    # AppTest cannot edit table cells directly. Send the browser widget state.
    editor = app.dataframe[0]
    selection_column = editor.value.columns[0]
    states = app._tree.get_widget_states()
    state = states.widgets.add(id=editor.proto.id)
    state.string_value = json.dumps(
        {
            "edited_rows": {
                row: {selection_column: value} for row, value in edits.items()
            },
            "added_rows": [],
            "deleted_rows": [],
        }
    )
    app._run(states)
