import streamlit as st
from streamlit_folium import st_folium
import folium
from datetime import datetime

st.set_page_config(page_title="Customer Map", layout="wide")  # 🔥 This enables full width

st.title("📌 Customer Network Collection")


# Create a Folium map centered at a default location
m = folium.Map(location=[11.55, 104.91], zoom_start=15, tiles='Esri.WorldImagery')  # Satellite view

# Add click handler
m.add_child(folium.LatLngPopup())

st.markdown("### 🗺️ Click on the map to capture coordinates")

# Side-by-side layout
col1, col2 = st.columns([2, 1])  # 🗺️ Map left (2x), Form right (1x)

with col1:
    map_data = st_folium(m, width=1200, height=800)

with col2:
    with st.form("customer_form"):
        st.subheader("Customer Details")
        
        # Auto-populate coordinates if clicked
        if map_data and map_data.get("last_clicked"):
            lat = st.number_input("Latitude", value=map_data["last_clicked"]["lat"], format="%.5f")
            lon = st.number_input("Longitude", value=map_data["last_clicked"]["lng"], format="%.5f")
            
            # Google Maps links
            st.markdown(f"""
            **📍 Google Maps Links:**
            - [Standard View](https://www.google.com/maps?q={lat},{lon})
            - [Satellite View](https://www.google.com/maps/@?api=1&map_action=map&basemap=satellite&zoom=15&center={lat},{lon})
            - [Street View](https://www.google.com/maps?layer=c&cbll={lat},{lon})
            """)
        else:
            lat = st.number_input("Latitude", format="%.5f")
            lon = st.number_input("Longitude", format="%.5f")

        name = st.text_input("Customer Name*")
        phone = st.text_input("Phone Number*")
        cust_type = st.selectbox("Customer Type*", ["Existing", "Prospect", "Repeat"])
        address = st.text_area("Street Address")
        notes = st.text_area("Visit Notes")

        submitted = st.form_submit_button("💾 Save Customer Location")
        if submitted:
            if not all([name, phone, cust_type]):
                st.error("Please fill all required fields (*)")
            elif not (lat and lon):
                st.error("Please select a location on the map")
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
                st.success("✅ Customer location saved!")
                st.json(new_location)  # Replace with DB or Google Sheet
