import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO

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
    sector
    status
    tierName
    product
  }
}
"""

# ==========================================
# UPLOAD FILE
# ==========================================

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    st.write("Preview:")
    st.dataframe(df.head())

    if st.button("Run Verification"):

        results = []

        progress = st.progress(0)

        for i, row in df.iterrows():

            member_id = str(row["member_id"]).strip()
            st.write(f"Checking {member_id}...")

            payload = {
                "operationName": "memberCheckForCodeV2",
                "query": QUERY,
                "variables": {"code": member_id}
            }

            try:
                response = requests.post(URL, json=payload, headers=HEADERS, timeout=20)
                data = response.json()["data"]["memberCheckForCodeV2"]

                if data:
                    results.append({
                        "member_id": member_id,
                        "status": data.get("status"),
                        "tierName": data.get("tierName"),
                        "firstName": data.get("firstName"),
                        "lastName": data.get("lastName"),
                        "explanation": data.get("explanation")
                    })
                else:
                    results.append({
                        "member_id": member_id,
                        "status": "NO RESPONSE"
                    })

            except Exception as e:
                results.append({
                    "member_id": member_id,
                    "status": f"ERROR: {str(e)}"
                })

            time.sleep(1)
            progress.progress((i + 1) / len(df))

        result_df = pd.DataFrame(results)

        st.success("Done!")

        st.dataframe(result_df)

        # ==========================================
        # DOWNLOAD BUTTON
        # ==========================================

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            result_df.to_excel(writer, index=False)

        st.download_button(
            "Download Results",
            data=output.getvalue(),
            file_name="members_checked.xlsx"
        )
