import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO

st.title("Membership Tool")

uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])

if uploaded_file:

    # 1. LOAD DATA FIRST
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    st.write("Preview")
    st.dataframe(df)

    # 2. ONLY RUN WHEN BUTTON IS CLICKED
    if st.button("Run Verification"):

        results = []

        # 3. NOW SAFE TO LOOP
        for i, row in df.iterrows():

            member_id = str(row.iloc[4]).strip()  # column E

            # API call here...
            results.append({
                "member_id": member_id
            })

        st.success("Done")
        st.dataframe(pd.DataFrame(results))
