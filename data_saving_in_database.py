def saving_data_in_database(df_path):
    import sqlite3
    import pandas as pd

    # Connect to SQLite database to clear
    conn = sqlite3.connect('earth_stations.db')
    cursor = conn.cursor()
    delete_query = 'DELETE FROM earth_stations'
    cursor.execute(delete_query)
    #print("\nAll data has been cleared from the table.")


    # Load the dataset
    df = pd.read_csv(df_path)
    df.columns = (df.columns.str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace(',', '').str.replace('/', '_'))
    # Create a table with corrected column names
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS earth_stations (
        Registration_Number TEXT,
        Location_Status TEXT,
        Licensee_Name TEXT,
        Call_Sign TEXT,
        Earth_Station_Latitude_DMS TEXT,
        Earth_Station_Longitude_DMS TEXT,
        Earth_Station_Latitude_Decimal REAL,
        Earth_Station_Longitude_Decimal REAL,
        Lower_Frequency_MHz REAL,
        Upper_Frequency_MHz REAL,
        Pointing_Azimuth_degrees REAL,
        Pointing_Elevation_Angle_degrees REAL,
        Antenna_Gain_dBi REAL,
        Earth_Station_Site_Elevation_meters REAL,
        Earth_Station_Height_AGL_meters REAL,
        Earth_Station_Height_AMSL_meters REAL,
        GSO_Satellite_Longitude_Decimal_Degrees REAL,
        Use_for_Tracking_Telemetry_and_Command TEXT,
        Certification_Date TEXT,
        Registration_Last_Updated TEXT,
        Call_Sign_Last_Updated TEXT
    )
    '''

    cursor.execute(create_table_query)

    # Insert data into the table
    df.to_sql('earth_stations', conn, if_exists='append', index=False)

    # Commit and close connection
    conn.commit()
    conn.close()
    print("Successfully send the data in to SQL Database\n")


df_path = 'Protected_FSS_Earth_Station_Registration__Complete_Dataset_.csv'
saving_data_in_database(df_path)
