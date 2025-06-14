import streamlit as st
from streamlit_javascript import st_javascript
from streamlit_folium import st_folium
import folium
from datetime import datetime
import sqlite3
import pandas as pd

# DB setup
DB_NAME = "customer_locations.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            type TEXT NOT NULL,
            address TEXT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            notes TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO locations 
        (name, phone, type, address, lat, lon, notes, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['name'], data['phone'], data['type'],
        data['address'], data['lat'], data['lon'],
        data['notes'], data['timestamp']
    ))
    conn.commit()
    conn.close()

def load_from_db():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM locations", conn)
    conn.close()
    return df

init_db()

st.set_page_config(page_title="Customer Network Builder", layout="wide")
st.title("🏢 Customer Network Builder")

# Step 1: Get GPS
with st.expander("📍 Step 1: Capture Current Location", expanded=True):
    location = st_javascript("""await new Promise((resolve) => {
        navigator.geolocation.getCurrentPosition(
            (pos) => resolve({
                latitude: pos.coords.latitude,
                longitude: pos.coords.longitude
            }),
            (err) => resolve(null)
        );
    })""")

    if location:
        lat = location["latitude"]
        lon = location["longitude"]
        st.success(f"Location captured: Latitude {lat:.6f}, Longitude {lon:.6f}")
        
        # Show current location on small map
        m_current = folium.Map(location=[lat, lon], zoom_start=17, tiles='Esri.WorldImagery')
        folium.Marker(
            [lat, lon], 
            tooltip="Your Location",
            icon=folium.Icon(color="blue", icon="user")
        ).add_to(m_current)
        st_folium(m_current, width=1500, height=1000)
    else:
        st.warning("Please enable GPS permissions in your browser to continue")
        st.stop()  # Stop execution if no GPS

# Step 2: Customer Form
with st.expander("📝 Step 2: Customer Information", expanded=True):
    with st.form("customer_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Customer Name*")
            phone = st.text_input("Phone Number*")
            cust_type = st.selectbox("Customer Type*", ["Prospect", "Existing", "VIP", "Repeat"])
        with col2:
            address = st.text_area("Address")
            notes = st.text_area("Visit Notes")

        submitted = st.form_submit_button("💾 Save Customer")
        if submitted:
            if not name or not phone:
                st.error("Please fill in all required fields (*)")
            else:
                save_to_db({
                    'name': name,
                    'phone': phone,
                    'type': cust_type,
                    'address': address,
                    'lat': lat,
                    'lon': lon,
                    'notes': notes,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("Customer saved successfully!")
                st.balloons()

# Step 3: Customer Map View
st.subheader("🗺️ Customer Network Map")
data = load_from_db()

if not data.empty:
    # Create map centered on average of all points
    avg_lat = data['lat'].mean()
    avg_lon = data['lon'].mean()
    
    m_all = folium.Map(location=[avg_lat, avg_lon], zoom_start=15, tiles='OpenStreetMap')
    
    # Add different markers for different customer types
    type_colors = {
        "Prospect": "orange",
        "Existing": "green",
        "VIP": "red",
        "Repeat": "blue"
    }
    
    for _, row in data.iterrows():
        folium.Marker(
            [row["lat"], row["lon"]],
            popup=f"""
                <b>{row['name']}</b><br>
                Type: {row['type']}<br>
                Phone: {row['phone']}<br>
                Last visit: {row['timestamp']}<br>
                <i>{row['notes']}</i>
            """,
            tooltip=row['name'],
            icon=folium.Icon(color=type_colors.get(row['type'], "gray"))
        ).add_to(m_all)
    
    # Add heatmap for density visualization
    from folium.plugins import HeatMap
    heat_data = [[row['lat'], row['lon']] for _, row in data.iterrows()]
    HeatMap(heat_data, radius=15).add_to(m_all)
    
    st_folium(m_all, width=1600, height=1200)
else:
    st.info("No customers in your network yet. Start by adding your first customer above.")