import streamlit as st
import pandas as pd
import requests
import time

st.title("Membership Tool")

URL = "https://www.partneroptumfitness.com/graphql/pass-edge"

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://www.partneroptumfitness.com",
    "Referer": "https://www.partneroptumfitness.com/",
    "User-Agent": "Mozilla/5.0"
}

QUERY = """
query memberCheckForCodeV2($code: String) {
  memberCheckForCodeV2(code: $code) {
    status
    tierName
  }
}
"""

uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file, engine="openpyxl")

    st.dataframe(df)

    if st.button("Run"):

        for i, row in df.iterrows():

            member_id = str(row.iloc[4]).strip()

            payload = {
                "operationName": "memberCheckForCodeV2",
                "query": QUERY,
                "variables": {"code": member_id}
            }

            response = requests.post(URL, json=payload, headers=HEADERS, timeout=20)

            st.write(response.status_code)
            st.write(response.text[:200])
            break
