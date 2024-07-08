def creating_maps(df):

    import pandas as pd
    import folium
    import os
    from playwright.sync_api import sync_playwright
    from PIL import Image
    from io import BytesIO

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

    # Ensure the output folder exists
    output_folder = '.cache/maps'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Function to plot all markers for each Call_Sign on a single map and save it to memory
    def plot_markers_for_call_sign(call_sign_df, call_sign):
        # Calculate bounds based on the latitude and longitude values for this specific Call_Sign
        min_lat = call_sign_df[mapping.lat].min() - 0.05
        max_lat = call_sign_df[mapping.lat].max() + 0.05
        min_lon = call_sign_df[mapping.lon].min() - 0.05
        max_lon = call_sign_df[mapping.lon].max() + 0.05

        bounds = [[min_lat, min_lon], [max_lat, max_lon]]
        #print(bounds)
        #Initialize the map centered on the average location
        avg_lat = (min_lat + max_lat) / 2
        avg_lon = (min_lon + max_lon) / 2
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=10)

        # Add markers for each location
        for _, row in call_sign_df.iterrows():
            lat = row[mapping.lat]
            lon = row[mapping.lon]
            registration_number = row[mapping.reg_nb]
            folium.Marker(location=[lat, lon], popup=registration_number).add_to(m)

        # Adjust the map view to fit the bounds of the specific Call_Sign
        m.fit_bounds(bounds)

        # Save the map to an HTML file in memory
        html_str = m._repr_html_()

        # Use Playwright to capture screenshot and save to memory
        image_bytes = None
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(html_str, timeout=120000)

            # Add a delay to allow the map to load
            page.wait_for_timeout(5000)  # 5 seconds

            image_bytes = page.screenshot(full_page=True)
            browser.close()

        # Convert the PNG bytes to JPEG
        image = Image.open(BytesIO(image_bytes))
        image = image.resize((800, 484), Image.LANCZOS)
        jpeg_image_bytes = BytesIO()
        image.convert("RGB").save(jpeg_image_bytes, format="JPEG")
        jpeg_image_bytes = jpeg_image_bytes.getvalue()

        # Save the single map image to a file
        file_path_name = os.path.join(output_folder, f'{call_sign}.jpeg')
        with open(file_path_name, 'wb') as f:
            f.write(jpeg_image_bytes)

        print(f"\nMap for {call_sign} saved successfully!")

    
    # Group data by Call_Sign and create a map for each group
    call_sign_groups = df.groupby(mapping.earth_station_type)
    for call_sign, group_df in call_sign_groups:
        plot_markers_for_call_sign(group_df, call_sign)
