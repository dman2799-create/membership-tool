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
    firstName
    lastName
    status
    tierName
    explanation
  }
}
"""

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file, engine="openpyxl")

    st.dataframe(df)

    if st.button("Run Verification"):

        results = []
        progress = st.progress(0)

        for i, row in df.iterrows():

            member_id = str(row.iloc[4]).strip()

            payload = {
                "operationName": "memberCheckForCodeV2",
                "query": QUERY,
                "variables": {"code": member_id}
            }

            try:
                response = requests.post(URL, json=payload, headers=HEADERS, timeout=20)
                result = response.json()

                member = result.get("data", {}).get("memberCheckForCodeV2")

                if member:
                    status = member.get("status", "")
                    tier = member.get("tierName", "")

                    eligibility = "ELIGIBLE" if (status == "matchFound" and tier == "Premium") else "NOT ELIGIBLE"

                    results.append({
                        "member_id": member_id,
                        "status": eligibility,
                        "firstName": member.get("firstName"),
                        "lastName": member.get("lastName"),
                        "tierName": tier
                    })

                else:
                    results.append({
                        "member_id": member_id,
                        "status": "NO DATA"
                    })

            except Exception:
                results.append({
                    "member_id": member_id,
                    "status": "ERROR"
                })

            time.sleep(0.5)
            progress.progress((i + 1) / len(df))

        output_df = pd.DataFrame(results)

        st.success("Done!")
        st.dataframe(output_df)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            output_df.to_excel(writer, index=False)

        st.download_button(
            "Download Results",
            data=output.getvalue(),
            file_name="members_checked.xlsx"
        )
