for i, row in df.iterrows():

    member_id = str(row.iloc[4]).strip()

    payload = {
        "operationName": "memberCheckForCodeV2",
        "query": QUERY,
        "variables": {"code": member_id}
    }

    try:
        response = requests.post(URL, json=payload, headers=HEADERS, timeout=20)

        # SAFETY CHECK 1: valid JSON
        try:
            result = response.json()
        except:
            df.at[i, "status"] = "INVALID RESPONSE"
            continue

        # SAFETY CHECK 2: GraphQL errors
        if "errors" in result:
            df.at[i, "status"] = "API ERROR"
            continue

        member = result.get("data", {}).get("memberCheckForCodeV2")

        if not member:
            df.at[i, "status"] = "NO DATA"
            continue

        status = member.get("status", "")
        tier = member.get("tierName", "")

        # FULL FIELD STORAGE (fix missing info issue)
        df.at[i, "status"] = (
            "ELIGIBLE" if (status == "matchFound" and tier == "Premium")
            else "NOT ELIGIBLE"
        )

        df.at[i, "tierName"] = tier
        df.at[i, "firstName"] = member.get("firstName", "")
        df.at[i, "lastName"] = member.get("lastName", "")
        df.at[i, "explanation"] = member.get("explanation", "")

    except Exception:
        df.at[i, "status"] = "ERROR"

    time.sleep(0.5)  # reduce failures vs 1 sec (important)
