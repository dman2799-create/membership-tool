import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO

st.set_page_config(page_title="Membership Checker", layout="wide")

st.title("Membership Verification Tool")

# ==========================================
# SETTINGS (same as your Colab)
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
    firstName
    lastName
    code
    explanation
    status
    tierName
  }
}
"""

# ==========================================
# FILE UPLOAD
# ==========================================

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file, engine="openpyxl")

    st.write("Preview of uploaded file:")
    st.dataframe(df)

    # ==========================================
    # AUTO-DETECT MEMBER ID COLUMN (IMPORTANT FIX)
    # ==========================================

    df.columns = df.columns.str.strip().str.lower()

    if "member_id" in df.columns:
        id_col = "member_id"
    elif "member id" in df.columns:
        id_col = "member id"
    elif "id" in df.columns:
        id_col = "id"
    else:
        st.error("No valid member ID column found. Please include 'member_id' column.")
        st.stop()

    # ==========================================
    # RUN BUTTON
    # ==========================================

    if st.button("Run Verification"):

        results = []
        progress = st.progress(0)

        for i, row in df.iterrows():

            member_id = str(row[id_col]).strip()

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

                    # Your original logic equivalent
                    if status == "matchFound" and tier == "Premium":
                        eligibility = "ELIGIBLE"
                    else:
                        eligibility = "NOT ELIGIBLE"

                    results.append({
                        "member_id": member_id,
                        "firstName": data.get("firstName"),
                        "lastName": data.get("lastName"),
                        "status": status,
                        "tierName": tier,
                        "eligibility": eligibility,
                        "explanation": data.get("explanation")
                    })

                else:
                    results.append({
                        "member_id": member_id,
                        "eligibility": "NO RESPONSE"
                    })

            except Exception as e:
                results.append({
                    "member_id": member_id,
                    "eligibility": f"ERROR: {str(e)}"
                })

            time.sleep(1)
            progress.progress((i + 1) / len(df))

        result_df = pd.DataFrame(results)

        st.success("Done processing!")

        st.dataframe(result_df)

        # ==========================================
        # DOWNLOAD EXCEL
        # ==========================================

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            result_df.to_excel(writer, index=False)

        st.download_button(
            "Download Results",
            data=output.getvalue(),
            file_name="members_checked.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
