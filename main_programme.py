import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import win32com.client as win32
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from random import randint
import folium
import base64
from io import BytesIO
from PIL import Image
import os


class mapping:
        reg_nb = 'Registration_Number'
        location_status = 'Location_Status'
        call_sign = 'Call_Sign'
        lat = 'Earth_Station_Latitude_Decimal'
        lon = 'Earth_Station_Longitude_Decimal'
        lower_frequency = 'Lower_Frequency_MHz'
        upper_frequency = 'Upper_Frequency_MHz'
        antenna_gain = 'Antenna_Gain_dBi'
        certification_date = 'Certification_Date'
        bandwidth ='Bandwidth_MHz'
        earth_station_type = 'Earth Station Type'
  
def classify_call_sign(call_sign):
    if call_sign.startswith('E'):
        return 'GB Station'
    elif call_sign.startswith('KA'):
        return 'FSS-ES'
    else:
        return 'Other'

def color_adding(val,threshold):
    try:
        value = float(val)
        return '#90EE90' if value > threshold else '#FF7F7F'
    except ValueError:
        return '#FFFFFF'

print("\nConnected to database & Query execution completed...")
# df_path = 'Protected_FSS_Earth_Station_Registration__Complete_Dataset_.csv'
# import data_saving_in_database as database
# database.saving_data_in_database(df_path)

# Connect to SQLite database to Query
conn = sqlite3.connect('earth_stations.db')
cursor = conn.cursor()
query = '''
SELECT * FROM earth_stations

'''
cursor.execute(query)
earth_stations = cursor.fetchall()
df_earth_stations = pd.read_sql_query(query, conn)
#print('\nQuery execution completed...')
conn.close()
df = df_earth_stations.copy()

#df[column_name] = pd.to_numeric(df[column_name].str.replace('[^\d.]', '', regex=True), errors='coerce').astype(float)
df[mapping.lower_frequency] = pd.to_numeric(df[mapping.lower_frequency].str.replace('[^\d.]', '', regex=True), errors='coerce').astype(float)
df[mapping.upper_frequency] = pd.to_numeric(df[mapping.upper_frequency].str.replace('[^\d.]', '', regex=True), errors='coerce').astype(float)

df[mapping.bandwidth] = df[mapping.upper_frequency] - df[mapping.lower_frequency]

# Define columns to coerce
columns_to_coerce = [mapping.lat, mapping.lon, mapping.antenna_gain]
for col in columns_to_coerce:
     df[col] = pd.to_numeric(df[col], errors='coerce')

df[mapping.certification_date] = pd.to_datetime(df[mapping.certification_date], errors='coerce')

# Define the timeframe for "newly registered"
timeframe_days = 218
cutoff_date = datetime.now() - timedelta(days=timeframe_days)

new_stations_df = df[df[mapping.certification_date] >= cutoff_date]

#earth stattion type column
#new_stations_df[mapping.earth_station_type] = new_stations_df[mapping.call_sign].apply(classify_call_sign)
# Assuming 'mapping' contains your column mappings or constants
new_stations_df = new_stations_df.copy()
new_stations_df.loc[:, mapping.earth_station_type] = new_stations_df[mapping.call_sign].apply(classify_call_sign)

#drop inactive columns
new_stations_df = new_stations_df[new_stations_df[mapping.location_status] != 'Inactive']
new_stations_df

new_stations_df.to_csv("new_stations_df.csv" , index= False)
print("\nCreating the earth station distribution maps...")
import maps
maps.creating_maps(new_stations_df)

#Send an mail using outlook
print("\nSending email...")
email_receiver = ['kaveeshasew123@outlook.com']
email_cc = ['Ayesha.Ilangaweeera-intern@dialog.lk']

# # Read the earth station dataset from a CSV file
earth_station_dataset = new_stations_df.copy()
columns_to_include = [mapping.reg_nb, mapping.call_sign, mapping.antenna_gain, mapping.bandwidth, mapping.earth_station_type]

def dataframe_to_html_with_styles(df):
    header = """
    <table style="width: 75%; border-collapse: collapse; font-family: Calibri;">
    <thead>
        <tr>
        <th style="border: 1px solid black; padding: 8px 2px; text-align: center;">Registration Number</th>
        <th style="border: 1px solid black; padding: 8px 2px; text-align: center;">Call Sign</th>
        <th style="border: 1px solid black; padding: 8px 2px; text-align: center;">Antenna Gain (dBi)</th>
        <th style="border: 1px solid black; padding: 8px 2px; text-align: center;">Bandwidth (MHz)</th>
        <th style="border: 1px solid black; padding: 8px 2px; text-align: center;">Earth Station</th>
        </tr>
    </thead>
    <tbody>
    """
    rows = []
    for index, row in df.iterrows():
        row_html = f"""
        <tr>
        <td style="border: 1px solid black; padding: 8px 2px; text-align: center;">{row[mapping.reg_nb]}</td>
        <td style="border: 1px solid black; padding: 8px 2px; text-align: center;">{row[mapping.call_sign]}</td> 
        <td style="border: 1px solid black; padding: 8px 2px; text-align: center;background-color: {color_adding(row[mapping.antenna_gain],50)};">{row[mapping.antenna_gain]}</td>
        <td style="border: 1px solid black; padding: 8px 2px; text-align: center;;background-color: {color_adding(row[mapping.bandwidth],100)};">{row[mapping.bandwidth]}</td>
                <td style="border: 1px solid black; padding: 8px 2px; text-align: center;">{row[mapping.earth_station_type]}</td>
        </tr>
        """
        rows.append(row_html)
    
    table_html = header + "\n".join(rows) + "\n</tbody>\n</table>"
    return table_html

# Convert styled DataFrame to HTML
html_table = dataframe_to_html_with_styles(earth_station_dataset[columns_to_include])

# Function to send email with the table
def send_email(table_html):
    outlook = win32.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)

    # Configure email details
    mail.Subject = 'New Earth Stations Data Notification'
    mail.To = '; '.join(email_receiver)
    mail.Cc = '; '.join(email_cc)

    map_image_path = r'E:\Earth_station_project\.cache\maps'
    images_html = ""
    try:
        for file_name in os.listdir(map_image_path):
            file_path = os.path.join(map_image_path, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # Remove file extension
                sation_type = os.path.splitext(file_name)[0]
                # if cluster_name in clusters_to_include:
                with open(file_path, 'rb') as f:
                    image = f.read()
                encoded_image = base64.b64encode(image).decode('utf-8')

                # Append each image with its cluster name
                images_html += f"""
                <h3 style="color: black; font-size: 14px; font-family: Calibri;">{sation_type}</h3>
                <img src="data:image/jpeg;base64,{encoded_image}" alt="{sation_type}">
                """
    except Exception as e:
        print(f"Error reading image files: {e}")
                
    

    # Compose the HTML email body
    body = f"""
    <html>
        <head></head>
        <body style="color: black; font-size: 14px; font-family: Calibri;">
            <p>Dear All,<br><br>
            Here is the latest earth station data for the month Dec -2023.Please find the KPI performances and earth station distribution maps below.</p>
            <p style="font-size:14px; font-weight:bold; font-style:italic;">Earth Station Data:</p>
            {table_html}
            <p style="font-size:14px; font-weight:bold; font-style:italic;">Earth Stations Distribution :</p>
            {images_html}
            <br>
            <p style="font-size:14px; font-weight:bold;">Thank You,<br>
            Operating Team</p>
        </body>
    </html>
    """

    # Set the HTML body of the email
    mail.HTMLBody = body

    # Send the email
    mail.Send()

    print("\nSent the email successfully\n")

send_email(html_table)