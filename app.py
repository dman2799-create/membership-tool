import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO

st.title("Membership Tool")

# ==========================================
# SETTINGS
# ==========================================

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
    firstName
    lastName
    explanation
  }
}
"""

# ==========================================
# UPLOAD FILE
# ==========================================

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file, engine="openpyxl")

    st.write("Preview:")
    st.dataframe(df)

    # Ensure column exists
    if df.shape[1] < 5:
        st.error("Your file must have member IDs in column E (5th column).")
        st.stop()

    # Add status column (like your original spreadsheet)
    if "status" not in df.columns:
        df["status"] = ""

    if st.button("Run Verification"):

        progress = st.progress(0)

        for i, row in df.iterrows():

            member_id = str(row.iloc[4]).strip()  # COLUMN E (same as Colab)

            payload = {
                "operationName": "memberCheckForCodeV2",
                "query": QUERY,
                "variables": {"code": member_id}
            }

            try:
                response = requests.post(URL, json=payload, headers=HEADERS, timeout=20)
                data = response.json()["data"]["memberCheckForCodeV2"]

                if data:
                    status = data.get("status", "")
                    tier = data.get("tierName", "")

                    # YOUR ORIGINAL LOGIC
                    if status == "matchFound" and tier == "Premium":
                        df.at[i, "status"] = "ELIGIBLE"
                    else:
                        df.at[i, "status"] = "NOT ELIGIBLE"
                else:
                    df.at[i, "status"] = "NO RESPONSE"

            except Exception as e:
                df.at[i, "status"] = f"ERROR"

            time.sleep(1)
            progress.progress((i + 1) / len(df))

        st.success("Done!")

        st.dataframe(df)

        # ==========================================
        # DOWNLOAD UPDATED FILE
        # ==========================================

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        st.download_button(
            "Download Updated Excel",
            data=output.getvalue(),
            file_name="members_checked.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
