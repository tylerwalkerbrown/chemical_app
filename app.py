import pandas as pd
import streamlit as st
from geopy.geocoders import Nominatim

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

def pivot_summary_vt(data):
    data['date'] = pd.to_datetime(data['completeddate'])
    data['week'] = data['date'].dt.isocalendar().week

    pivot_table = data.pivot_table(values='materialquantity', index='week', columns='county', aggfunc='sum')

    # Add the date next to the week number in the pivot table
    week_dates = pd.Series(pd.to_datetime(data.groupby('week')['date'].min()))
    week_dates = week_dates.dt.strftime('%Y-%m-%d')
    pivot_table.insert(0, 'Date', week_dates)

    if not pivot_table.empty:
        # Calculate Square Footage by multiplying the sum of material quantity by 5000
        pivot_table['Square Footage'] = data.groupby('week')['materialquantity'].sum() * 5000

    return pivot_table


def pivot_summary_nh(data):
    data['date'] = pd.to_datetime(data['completeddate'])
    data['week'] = data['date'].dt.isocalendar().week

    pivot_table = data.pivot_table(values='materialquantity', index='week', columns='itemnum', aggfunc='sum')

    # Apply multipliers to specific columns
    multipliers = {
        'Essentria IC3': 2,
        'Cyzmic': 0.8,
        'Pivot10': 4,
        'Stryker': 10,
        'Surf-AC': 4,
        'Tekko Pro': 1,
        'DuraFlex ZC': 1.5,
        'STB - 6 oz': 4,
        'STB - 4 oz': 4
    }

    for column, multiplier in multipliers.items():
        if column in pivot_table.columns:
            pivot_table[column] *= multiplier

    # Add the date next to the week number in the pivot table
    week_dates = pd.Series(pd.to_datetime(data.groupby('week')['date'].min()))
    week_dates = week_dates.dt.strftime('%Y-%m-%d')
    pivot_table.insert(0, 'Date', week_dates)

    if not pivot_table.empty:
        # Calculate Square Footage by multiplying the sum of material quantity by 5000
        pivot_table['Square Footage'] = data.groupby('week')['materialquantity'].sum() * 5000

    return pivot_table


def main():
    st.title("CSV Analysis")
    st.sidebar.title("Options")

    if st.sidebar.checkbox("View Requirements"):
        st.subheader("Requirements")
        st.markdown("""
        - CSV file with the following columns: `siteaddress`, `completeddate`, `materialquantity`, `itemnum`.
        - The `siteaddress` column should contain the address information.
        - The `completeddate` column should contain the completion date in a valid date format.
        - The `materialquantity` column should contain the quantity of material.
        - The `itemnum` column should contain the item number.
        """)

    file = st.file_uploader("Upload CSV", type=["csv"])

    if file is not None:
        df = process_csv(file)
        data_nh = df[df['State'] == 'NH']

        st.subheader("Pivot Table for NH")
        pivot_table_nh = pivot_summary_nh(data_nh)
        st.write(pivot_table_nh)

        csv_nh = pivot_table_nh.to_csv(index=True)
        st.download_button("Download CSV (NH)", data=csv_nh, file_name="pivot_table_nh.csv")

        data_vt = df[df['State'] == 'VT']

        st.subheader("Pivot Table for VT")
        pivot_table_vt = pivot_summary_vt(data_vt)
        st.write(pivot_table_vt)

        csv_vt = pivot_table_vt.to_csv(index=True)
        st.download_button("Download CSV (VT)", data=csv_vt, file_name="pivot_table_vt.csv")

if __name__ == '__main__':
    main()
