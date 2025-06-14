import streamlit as st
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval

st.title("📍 Customer Visit Location Uploader")

# Get location using JavaScript (works on mobile)
location = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition",
                             key="get_location")

with st.form("customer_form"):
    st.subheader("Customer Details")

    # Fill lat/lon if detected from browser
    if location and 'coords' in location:
        lat = location['coords']['latitude']
        lon = location['coords']['longitude']
        st.success(f"📌 Your location detected: ({lat:.5f}, {lon:.5f})")
    else:
        lat = st.number_input("Latitude", format="%.5f")
        lon = st.number_input("Longitude", format="%.5f")

    # Customer details
    name = st.text_input("Customer Name*")
    phone = st.text_input("Phone Number*")
    cust_type = st.selectbox("Customer Type*", ["Existing", "Prospect", "Repeat"])
    address = st.text_area("Street Address")
    notes = st.text_area("Visit Notes")

    # Submit
    submitted = st.form_submit_button("💾 Save Customer Visit")
    if submitted:
        if not all([name, phone, cust_type]):
            st.error("Please fill all required fields (*)")
        elif not (lat and lon):
            st.error("Location not available – please enable location services or input manually")
        else:
            new_location = {
                'name': name,
                'phone': phone,
                'type': cust_type,
                'address': address,
                'lat': lat,
                'lon': lon,
                'notes': notes,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.success("✅ Customer visit saved!")
            st.json(new_location)  # You can replace this with saving to DB or Google Sheets
