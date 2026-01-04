#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: A page to add assets and view the risk metrics

"""
import datetime
import pandas as pd
import streamlit as st
from src.utils.utils import set_page_state

def var_caluation():
    pass

def cvar_caluation():
    pass

def beta_caluation():
    pass



def main():
    set_page_state("pages/tracker.py")

    title_text, save_btn, load_btn, extra_space = st.columns([0.2, .08, .08, 0.4], vertical_alignment="center")
    st.markdown("Quantitative analysis of portfolio risk and performance, including alpha and tail-risk metrics, with portfolio persistence and PDF reporting.")
    title_text.title("Portfolio Tracker")
    save_btn.button("Save", key="save")
    load_btn.button("Load", key="load")

    metric_container = st.container()

    with st.form("my_form"):
        header = st.columns([1, 2, 2])

        row1 = st.columns([1, 2, 2])
        colorA = row1[0].color_picker('Team A', '#0000FF')
        opacityA = row1[1].slider('A opacity', 20, 100, 50)
        sizeA = row1[2].slider('A size', 20, 100, 50)

        st.form_submit_button()


    data = [{
        "asset_name": "TSLA",
        "weight": 10,
        "amount": 200,
        "entry_at": datetime.date.today(),
        "enabled": True
    }]

    portfolio = pd.DataFrame(data)

    @st.dialog("Add Row")
    def add_row():
        with st.form("add_row_form", clear_on_submit=True):
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=0, step=1)
            email = st.text_input("Email")
            submitted = st.form_submit_button("Add Row")


    with st.container(height=300, border=None):
        st.data_editor(portfolio,
                       hide_index=True,
                       column_config={
                           "asset_name": st.column_config.TextColumn(
                            label="Asset Name",
                            help="The Asset Name",
                            default="",
                            max_chars=50,
                            validate=r"^st\.[a-z_]+$",
                        ),
                           "weight": st.column_config.NumberColumn(
                               label="Asset Weight",
                               help="The propuation the asset makes up of your portfolio",
                               format="%d%%",
                               min_value=0,
                               max_value=100
                           ),
                           "amount": st.column_config.NumberColumn(
                               label="Quantity",
                               help="The total amount you hold",
                           ),
                           "entry_at": st.column_config.DateColumn(
                               label="Entry Date",
                               help="When you enter the position",
                           ),
                           "enabled": st.column_config.CheckboxColumn(
                               label="Enabled",
                               help="Disabling this means it will not be included in the calculation",
                           )
                       }
                       )


    for asset in portfolio:
        pass

    with metric_container:
        col1, col2, col3 = st.columns(3)
        col1.metric("Temperature", "70 °F", "1.2 °F")
        col2.metric("Wind", "9 mph", "-8%")
        col3.metric("Humidity", "86%", "4%")





if __name__ == "__main__":
    main()
