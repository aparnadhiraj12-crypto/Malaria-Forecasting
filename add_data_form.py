import streamlit as st
import pandas as pd
from datetime import date
from malaria_db import (
    init_db,
    list_states,
    get_state_data,
    add_or_update_value,
    bulk_add_dataframe,
)


def render_add_data_form():
    st.subheader("Add / Update Malaria Data")

    existing_states = list_states()

    tab_single, tab_bulk = st.tabs(["Add a single value", "Bulk upload CSV"])

    # ---------- Tab 1: add/update a single (state, month) value ----------
    with tab_single:
        col1, col2 = st.columns(2)

        with col1:
            state_choice = st.radio(
                "State", ["Choose existing state", "Add a new state"], horizontal=True
            )
            if state_choice == "Choose existing state":
                if not existing_states:
                    st.info("No states in the database yet. Add a new state instead.")
                    state = None
                else:
                    state = st.selectbox("Select state", existing_states)
            else:
                state = st.text_input("New state name (e.g. 'kerala')")

        with col2:
            month_date = st.date_input("Month", value=date.today())
            log_cases = st.number_input("LogCases value", format="%.6f")

        if st.button("Save value", type="primary"):
            if not state:
                st.error("Please choose or enter a state name.")
            else:
                month_str = month_date.strftime("%d-%m-%Y")
                add_or_update_value(state, month_str, log_cases)
                st.success(f"Saved: {state} / {month_str} = {log_cases}")
                st.rerun()

        # Show current data for the selected state, if any
        if state and state.strip().lower() in existing_states:
            st.markdown(f"**Current data for `{state}`:**")
            st.dataframe(get_state_data(state), use_container_width=True, height=250)

    # ---------- Tab 2: bulk upload a CSV for a state ----------
    with tab_bulk:
        st.caption("CSV must have columns: `Month` (DD-MM-YYYY) and `LogCases`.")
        bulk_state = st.text_input(
            "State this CSV belongs to", key="bulk_state_input"
        )
        uploaded = st.file_uploader("Upload CSV", type=["csv"])

        if uploaded is not None and bulk_state:
            df = pd.read_csv(uploaded)
            df.columns = df.columns.str.strip()
            if not {"Month", "LogCases"}.issubset(df.columns):
                st.error("CSV must contain 'Month' and 'LogCases' columns.")
            else:
                st.dataframe(df.head(), use_container_width=True)
                if st.button("Import this CSV"):
                    bulk_add_dataframe(bulk_state, df)
                    st.success(
                        f"Imported {len(df)} rows for state '{bulk_state.strip().lower()}'."
                    )
                    st.rerun()


# Allows `streamlit run add_data_form.py` to work standalone for testing
if __name__ == "__main__":
    init_db()
    st.title("Malaria Data Entry")
    render_add_data_form()
