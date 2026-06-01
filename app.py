for i, row in df.iterrows():

    member_id = str(row.iloc[4]).strip()  # COLUMN E (same as your Colab)

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

            eligibility = "ELIGIBLE" if (status == "matchFound" and tier == "Premium") else "NOT ELIGIBLE"

            results.append({
                "member_id": member_id,
                "status": status,
                "tierName": tier,
                "eligibility": eligibility
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
