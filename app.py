import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# --- Data Loading --
@st.cache_data
def load_customer_data():
    return pd.DataFrame({
        'Customer_ID': ['C001', 'C002', 'C003', 'C004'],
        'Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown'],
        'Phone': ['012345678', '098765432', '011223344', '099887766'],
        'Location': ['Phnom Penh', 'Siem Reap', 'Battambang', 'Sihanoukville'],
        'Latitude': [11.5621, 13.3615, 13.0957, 10.6275],
        'Longitude': [104.9174, 103.8596, 103.2022, 103.5225],
        'Business_Type': ['Retail', 'Agriculture', 'Construction', 'Tourism'],
        'Business_Years': [5, 3, 8, 2],
        'Education': ['Bachelor', 'High School', 'Vocational', 'Master'],
        'Collateral_Type': ['Land', 'Vehicle', 'Equipment', 'House'],
        'Collateral_Value': [50000, 25000, 35000, 80000],
        'Loan_Amount': [25000, 15000, 50000, 35000],
        'Loan_Status': ['Approved', 'Pending', 'Rejected', 'Approved'],
        'Risk_Score': [65, 42, 88, 71],
        'Last_Contact': ['2023-08-15', '2023-09-02', '2023-07-20', '2023-09-10'],
        'Sales_Rep': ['Rep1', 'Rep2', 'Rep1', 'Rep3']
    })

# --- Map Visualization ---
def create_customer_map(data):
    m = folium.Map(location=[12.5657, 104.9910], zoom_start=7)  # Center on Cambodia
    
    for idx, row in data.iterrows():
        html = f"""
        <h4>{row['Name']}</h4>
        <b>Business:</b> {row['Business_Type']} ({row['Business_Years']} yrs)<br>
        <b>Loan:</b> ${row['Loan_Amount']:,} | {row['Loan_Status']}<br>
        <b>Collateral:</b> {row['Collateral_Type']} (${row['Collateral_Value']:,})<br>
        <b>Last Contact:</b> {row['Last_Contact']}
        """
        
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=folium.Popup(html, max_width=300),
            tooltip=f"{row['Name']} - {row['Loan_Status']}",
            icon=folium.Icon(
                color='green' if row['Loan_Status']=='Approved' else 
                     'orange' if row['Loan_Status']=='Pending' else 'red',
                icon='briefcase' if row['Business_Type']=='Agriculture' else
                     'shopping-cart' if row['Business_Type']=='Retail' else 'building'
            )
        ).add_to(m)
    
    return m

# --- Customer Detail View ---
def show_customer_details(row):
    with st.expander(f"🔍 {row['Name']} - {row['Customer_ID']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Personal Info")
            st.write(f"📞 **Phone:** {row['Phone']}")
            st.write(f"🎓 **Education:** {row['Education']}")
            st.write(f"📍 **Location:** {row['Location']}")
            
            st.subheader("Business Info")
            st.write(f"🏢 **Type:** {row['Business_Type']}")
            st.write(f"⏳ **Years in Business:** {row['Business_Years']}")
        
        with col2:
            st.subheader("Loan Details")
            st.write(f"💰 **Loan Amount:** ${row['Loan_Amount']:,}")
            st.write(f"🏷️ **Status:** {row['Loan_Status']}")
            st.write(f"📊 **Risk Score:** {row['Risk_Score']}")
            
            st.subheader("Collateral")
            st.write(f"🏠 **Type:** {row['Collateral_Type']}")
            st.write(f"💲 **Value:** ${row['Collateral_Value']:,}")
        
        st.write(f"👔 **Sales Rep:** {row['Sales_Rep']}")
        st.write(f"📅 **Last Contact:** {row['Last_Contact']}")

# --- Main App ---
def main():
    st.set_page_config(page_title="Sales Team Portal", layout="wide", page_icon="👔")
    
    # --- Authentication ---
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        with st.form("login"):
            st.title("Sales Team Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                if username == "sales" and password == "team123":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        return
    
    # --- Main Interface ---
    st.title("👔 Customer Loan Management Portal")
    st.markdown("**Sales Team Dashboard** | Access customer details and loan information")
    
    customer_data = load_customer_data()
    
    # --- Sidebar Filters ---
    with st.sidebar:
        st.header("Filters")
        
        selected_status = st.multiselect(
            "Loan Status",
            options=customer_data['Loan_Status'].unique(),
            default=customer_data['Loan_Status'].unique()
        )
        
        selected_business = st.multiselect(
            "Business Type",
            options=customer_data['Business_Type'].unique(),
            default=customer_data['Business_Type'].unique()
        )
        
        selected_rep = st.multiselect(
            "Sales Representative",
            options=customer_data['Sales_Rep'].unique(),
            default=customer_data['Sales_Rep'].unique()
        )
        
        loan_range = st.slider(
            "Loan Amount Range ($)",
            min_value=int(customer_data['Loan_Amount'].min()),
            max_value=int(customer_data['Loan_Amount'].max()),
            value=(0, int(customer_data['Loan_Amount'].max())))
    
    # Apply filters
    filtered_data = customer_data[
        (customer_data['Loan_Status'].isin(selected_status)) &
        (customer_data['Business_Type'].isin(selected_business)) &
        (customer_data['Sales_Rep'].isin(selected_rep)) &
        (customer_data['Loan_Amount'] >= loan_range[0]) &
        (customer_data['Loan_Amount'] <= loan_range[1])
    ]
    
    # --- Dashboard Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", len(filtered_data))
    col2.metric("Approval Rate", 
               f"{len(filtered_data[filtered_data['Loan_Status']=='Approved'])/len(filtered_data)*100:.1f}%")
    col3.metric("Avg Loan Amount", 
               f"${filtered_data['Loan_Amount'].mean():,.0f}")
    col4.metric("High Risk Customers", 
               len(filtered_data[filtered_data['Risk_Score'] > 75]))
    
    # --- Map View ---
    st.subheader("Geographic Distribution")
    st.caption("Click markers for customer details")
    customer_map = create_customer_map(filtered_data)
    st_folium(customer_map, width=1200, height=1000)
    
    # --- Customer List View ---
    st.subheader("Customer Details")
    
    search_col, sort_col = st.columns(2)
    with search_col:
        search_term = st.text_input("Search by Name or ID")
    with sort_col:
        sort_by = st.selectbox("Sort By", 
                             ['Loan Amount (High-Low)', 'Risk Score (High-Low)', 
                              'Last Contact (Recent)'])
    
    # Apply search and sort
    if search_term:
        filtered_data = filtered_data[
            filtered_data['Name'].str.contains(search_term, case=False) |
            filtered_data['Customer_ID'].str.contains(search_term, case=False)
        ]
    
    if sort_by == 'Loan Amount (High-Low)':
        filtered_data = filtered_data.sort_values('Loan_Amount', ascending=False)
    elif sort_by == 'Risk Score (High-Low)':
        filtered_data = filtered_data.sort_values('Risk_Score', ascending=False)
    else:
        filtered_data = filtered_data.sort_values('Last_Contact', ascending=False)
    
    # Display customer cards
    for _, row in filtered_data.iterrows():
        show_customer_details(row)
        st.divider()
    
    # --- Data Export ---
    st.sidebar.download_button(
        label="📥 Export Customer Data",
        data=filtered_data.to_csv(index=False),
        file_name=f"customer_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

if __name__ == "__main__":
    main()