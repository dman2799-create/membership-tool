response = requests.post(URL, json=payload, headers=HEADERS, timeout=20)

st.write("STATUS CODE:", response.status_code)
st.write("RESPONSE TEXT:", response.text[:300])
st.stop()
