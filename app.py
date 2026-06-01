import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO

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
    firstName
    lastName
    explanation
  }
}
"""

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:

    # LOAD EXACT SPREADSHEET (no restructuring)
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    st.write("Original file preview:")
    st.dataframe(df)

    # Ensure status column exists (like Colab behavior)
    if "status" not in df.columns:
        df["status"] = ""

    if st.button("Run Verification"):

        progress = st.progress(0)

        for i in range(len(df)):

            try:
                member_id = str(df.iloc[i, 4]).strip()  # COLUMN E (same as Colab)

                payload = {
                    "operationName": "memberCheckForCodeV2",
                    "query": QUERY,
                    "variables": {"code": member_id}
                }

                response = requests.post(URL, json=payload, headers=HEADERS, timeout=20)
                result = response.json()

                member = result.get("data", {}).get("memberCheckForCodeV2")

                # DEFAULT fallback
                status_value = "NOT ELIGIBLE"

                if member:
                    api_status = member.get("status")
                    tier = member.get("tierName")

                    if api_status == "matchFound" and tier == "Premium":
                        status_value = "ELIGIBLE"

                # WRITE BACK INTO ORIGINAL DF (KEY FIX)
                df.at[i, "status"] = status_value

            except Exception:
                df.at[i, "status"] = "ERROR"

            time.sleep(0.5)
            progress.progress((i + 1) / len(df))

        st.success("Done!")

        st.dataframe(df)

        # EXPORT EXACT SAME FORMAT AS INPUT
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        st.download_button(
            "Download Updated Excel",
            data=output.getvalue(),
            file_name="members_checked.xlsx"
        )
