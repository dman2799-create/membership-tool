import streamlit as st
import pandas as pd

st.title("Membership Tool")

uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])

if uploaded_file:

    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        st.success("Excel loaded successfully")
    except Exception as e:
        st.error(f"Failed to read Excel: {e}")
        st.stop()

    st.dataframe(df)

    if st.button("Run Verification"):

        results = []

        for i, row in df.iterrows():

            try:
                member_id = str(row.iloc[4]).strip()
            except Exception as e:
                st.error(f"Row error: {e}")
                continue

            results.append({
                "member_id": member_id
            })

        st.success("Done")
        st.dataframe(pd.DataFrame(results))
