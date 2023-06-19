import pandas as pd
import streamlit as st
from geopy.geocoders import Nominatim

# Function to process the uploaded CSV file
def process_csv(file):
    df = pd.read_csv(file)
    df['State'] = df['siteaddress'].str.split(",", expand=True)[1].str.split(" ", expand=True)[1]
    df['zipcode'] = df['siteaddress'].str.split(",", expand=True)[1].str.split(" ", expand=True)[2]

    county_info = []
    geolocator = Nominatim(user_agent="your_app_name")

    for i, state in zip(list(df.zipcode), list(df.State)):
        if state == 'VT':
            location = geolocator.geocode(i)
            location_info = str(location)
            components = location_info.split(", ")
            county = components[1]
        else:
            county = 'NA'
        county_info.append(county)

    df['county'] = county_info

    df['date'] = pd.to_datetime(df['completeddate'])
    df['week'] = df['date'].dt.isocalendar().week
    return df

def pivot_summary_nh(data):
    data['date'] = pd.to_datetime(data['completeddate'])
    data['week'] = data['date'].dt.isocalendar().week

    pivot_table = data.pivot_table(values='materialquantity', index='week', columns='itemnum', aggfunc='sum')

    # Add the date next to the week number in the pivot table
    week_dates = pd.Series(pd.to_datetime(data.groupby('week')['date'].min()))
    week_dates = week_dates.dt.strftime('%Y-%m-%d')
    pivot_table.insert(0, 'Date', week_dates)

    return pivot_table

def pivot_summary_vt(data):
    data['date'] = pd.to_datetime(data['completeddate'])
    data['week'] = data['date'].dt.isocalendar().week

    pivot_table = data.pivot_table(values='materialquantity', index='week', columns='county', aggfunc='sum')

    # Add the date next to the week number in the pivot table
    week_dates = pd.Series(pd.to_datetime(data.groupby('week')['date'].min()))
    week_dates = week_dates.dt.strftime('%Y-%m-%d')
    pivot_table.insert(0, 'Date', week_dates)

    return pivot_table

# Streamlit app
def main():
    st.title("CSV Analysis")
    st.sidebar.title("Options")

    # Display requirements page
    if st.sidebar.checkbox("View Requirements"):
        st.subheader("Requirements")
        st.markdown("""
        - CSV file with the following columns: `siteaddress`, `completeddate`, `materialquantity`, `itemnum`.
        - The `siteaddress` column should contain the address information.
        - The `completeddate` column should contain the completion date in a valid date format.
        - The `materialquantity` column should contain the quantity of material.
        - The `itemnum` column should contain the item number.
        """)

    # Allow file upload
    file = st.file_uploader("Upload CSV", type=["csv"])

    if file is not None:
        # Process the uploaded CSV file
        df = process_csv(file)

        # Display pivot table for all states
        st.subheader("Pivot Table for All States")
        pivot_table = df.pivot_table(values='materialquantity', index='week', columns='itemnum', aggfunc='sum')
        st.write(pivot_table)

        # Download CSV for pivot table of all states
        csv_all_states = pivot_table.to_csv(index=True)
        st.download_button("Download CSV (All States)", data=csv_all_states, file_name="pivot_table_all_states.csv")

        # Filter data for NH
        data_nh = df[df['State'] == 'NH']

        # Display pivot table for NH
        st.subheader("Pivot Table for NH")
        pivot_table_nh = pivot_summary_nh(data_nh)
        st.write(pivot_table_nh)

        # Download CSV for pivot table of NH
        csv_nh = pivot_table_nh.to_csv(index=True)
        st.download_button("Download CSV (NH)", data=csv_nh, file_name="pivot_table_nh.csv")

        # Filter data for VT
        data_vt = df[df['State'] == 'VT']

        # Display pivot table for VT
        st.subheader("Pivot Table for VT")
        pivot_table_vt = pivot_summary_vt(data_vt)
        st.write(pivot_table_vt)

        # Download CSV for pivot table of VT
        csv_vt = pivot_table_vt.to_csv(index=True)
        st.download_button("Download CSV (VT)", data=csv_vt, file_name="pivot_table_vt.csv")

if __name__ == '__main__':
    main()
