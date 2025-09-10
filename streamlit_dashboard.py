import streamlit as st
import requests
import json
from streamlit_autorefresh import st_autorefresh

# --- Settings ---
server = st.text_input("Server URL", "http://em-flaut:57080")

# --- Define the tags you want to monitor/control ---
tags = {
    "RPM": "Hitec_OPC_DA20_Server->AUTOSAMPLER:AUTOSAM1.ST_RPM",
    "Valve_set": "Hitec_OPC_DA20_Server->AUTOSAMPLER:AUTOSAM1.VALV_ON",
    "Stirrer_on_off": "Hitec_OPC_DA20_Server->AUTOSAMPLER:AUTOSAM1.ST_ON"
}

# --- Functions ---
def read_value(server, tag):
    try:
        url = f"{server}/read?item={tag}"
        response = requests.get(url, verify=False, timeout=2)
        response.raise_for_status()  # close the co
        json_object = response.json()
        data = json_object.get("data", [])
        if not data:
            return None, None
        value = data[0]["Properties"]["Value"]
        timestamp = data[0]["Properties"]["SourceTimestamp"]
        return value, timestamp
    except Exception as e:
        print("Error while reading", e)
        return None, None
    
def write_on_change(name, tag):
    value = st.session_state[name]
    write_value(server, tag, value)
    st.success(f"{name} updated to {value}")

def write_value(server, tag, value):
    try:
        url = f"{server}/write?item={tag}&value={value}"
        response = requests.get(url, verify=False, timeout=2)
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}

# --- Auto-refresh every 1 second ---
st_autorefresh(interval=1000, key="datarefresh")

# --- Display current values ---
st.subheader("Current Values")
current_values = {}
for name, tag in tags.items():
    value, timestamp = read_value(server, tag)
    current_values[name] = value
    st.write(f"{name}: {value} (Timestamp: {timestamp})")

st.subheader("Set New Values")
for name, tag in tags.items():
    if name not in st.session_state:
        st.session_state[name] = current_values[name] if current_values[name] is not None else 0

    st.number_input(
        label=name,
        value=st.session_state[name],
        step=1,
        key=name,
        on_change=write_on_change,
        args=(name, tag)
    )