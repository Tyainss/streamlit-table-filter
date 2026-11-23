from collections.abc import Hashable, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from uuid import uuid4

import pandas as pd
import streamlit as st

if TYPE_CHECKING:
    from polars import DataFrame as PolarsDataFrame


@dataclass
class _FilterState:
    option_ids: list[Hashable]
    selected_ids: set[Hashable]
    editor_key: str = ""
    editor_table: pd.DataFrame | None = None
    editor_config: dict[str, Any] | None = None


def reset_table_filter(key: str) -> None:
    """Start from the initial selection the next time the filter renders."""
    st.session_state.pop(_state_key(key), None)


def table_filter(
    options: list[Hashable] | pd.DataFrame | PolarsDataFrame,
    *,
    key: str,
    id_column: str | None = None,
    display_columns: Sequence[str] | None = None,
    label: str | None = None,
    initial_selection: Sequence[Hashable] | None = None,
    column_config: Mapping[str, Any] | None = None,
    selection_label: str = "Selected",
) -> list[Hashable]:
    """Render a checkbox table and return the selected IDs in input order."""
    option_ids, display = _prepare_options(options, id_column, display_columns)
    _validate_ids(option_ids)

    state_key = _state_key(key)
    state = st.session_state.get(state_key)
    if state is None:
        selected_ids = set(option_ids)
        if initial_selection is not None:
            selected_ids.intersection_update(initial_selection)
        state = _FilterState(option_ids, selected_ids)
        st.session_state[state_key] = state
    elif state.option_ids != option_ids:
        previous_ids = set(state.option_ids)
        state.selected_ids = {
            option_id
            for option_id in option_ids
            if option_id in state.selected_ids or option_id not in previous_ids
        }
        state.option_ids = option_ids
        state.editor_table = None

    if not option_ids:
        st.caption("No options available.")
        return []

    selected_column = "_selected"
    while selected_column in display.columns:
        selected_column = f"_{selected_column}"

    config = dict(column_config or {})
    if isinstance(options, list) and label is not None:
        config.setdefault("Value", label)
    config[selected_column] = st.column_config.CheckboxColumn(selection_label)

    if (
        state.editor_table is None
        or state.editor_key not in st.session_state
        or state.editor_config != config
        or not state.editor_table.iloc[:, 1:].equals(display)
    ):
        # Start a fresh editor when its old positional edits no longer apply.
        checked = [option_id in state.selected_ids for option_id in option_ids]
        display.insert(0, selected_column, checked)
        state.editor_table = display
        state.editor_config = config
        state.editor_key = f"streamlit_table_filter:editor:{key}:{uuid4().hex}"

    checkbox_key = f"streamlit_table_filter:select_all:{key}"
    st.session_state[checkbox_key] = len(state.selected_ids) == len(option_ids)
    st.checkbox(
        "Select all",
        key=checkbox_key,
        on_change=_toggle_all,
        args=(state_key, checkbox_key),
    )

    st.data_editor(
        state.editor_table,
        hide_index=True,
        disabled=[str(column) for column in state.editor_table.columns[1:]],
        column_config=config,
        key=state.editor_key,
        on_change=_update_selection,
        args=(state_key, state.editor_key),
    )

    selected = [
        option_id for option_id in option_ids if option_id in state.selected_ids
    ]
    return selected


def _state_key(key: str) -> str:
    state_key = f"streamlit_table_filter:state:{key}"
    return state_key


def _prepare_options(
    options: list[Hashable] | pd.DataFrame | PolarsDataFrame,
    id_column: str | None,
    display_columns: Sequence[str] | None,
) -> tuple[list[Hashable], pd.DataFrame]:
    if isinstance(options, list):
        display = pd.DataFrame({"Value": options})
        return options.copy(), display

    if not isinstance(options, pd.DataFrame):
        try:
            from polars import DataFrame as PolarsDataFrame
        except ModuleNotFoundError as error:
            if error.name != "polars":
                raise
            raise TypeError(
                "options must be a list or a pandas or Polars DataFrame."
            ) from None
        if not isinstance(options, PolarsDataFrame):
            raise TypeError("options must be a list or a pandas or Polars DataFrame.")

    columns = list(options.columns)
    if len(set(columns)) != len(columns):
        raise ValueError("DataFrame column names must be unique.")
    if id_column is None or id_column not in columns:
        raise ValueError("id_column must name a column in the options DataFrame.")

    visible_columns = columns if display_columns is None else list(display_columns)
    if len(set(visible_columns)) != len(visible_columns):
        raise ValueError("display_columns must contain unique column names.")
    if missing_columns := set(visible_columns).difference(columns):
        raise ValueError(f"Unknown display columns: {missing_columns!r}")

    if isinstance(options, pd.DataFrame):
        option_ids = options[id_column].tolist()
        display = options.loc[:, visible_columns].reset_index(drop=True)
    else:
        option_ids = options.get_column(id_column).to_list()
        if visible_columns:
            display = options.select(visible_columns).to_pandas(
                use_pyarrow_extension_array=True
            )
        else:
            display = pd.DataFrame(index=range(len(option_ids)))

    return option_ids, display


def _validate_ids(option_ids: list[Hashable]) -> None:
    if pd.Series(option_ids, dtype=object).isna().any():
        raise ValueError("Option IDs must be non-null.")
    try:
        unique_ids = set(option_ids)
    except TypeError as error:
        raise ValueError("Option IDs must be hashable.") from error
    if len(unique_ids) != len(option_ids):
        raise ValueError("Option IDs must be unique.")


def _toggle_all(state_key: str, checkbox_key: str) -> None:
    state = st.session_state[state_key]
    state.selected_ids = (
        set(state.option_ids) if st.session_state[checkbox_key] else set()
    )
    state.editor_table = None


def _update_selection(state_key: str, editor_key: str) -> None:
    state = st.session_state.get(state_key)
    if state is None or state.editor_table is None or state.editor_key != editor_key:
        return

    # Streamlit sends the cumulative edits against the table it first rendered.
    selected_column = state.editor_table.columns[0]
    checked = state.editor_table[selected_column].tolist()
    for row_index, changes in st.session_state[editor_key]["edited_rows"].items():
        if selected_column in changes:
            checked[row_index] = changes[selected_column]

    state.selected_ids = {
        option_id
        for option_id, selected in zip(state.option_ids, checked, strict=True)
        if selected
    }
