#!/usr/bin/env python3
"""
Web GIS application for NWIS Data Visualizer using Streamlit.

This application displays station locations on a map, allows users to click
on stations to view available parameters, and plots time series data.
"""

import os
import sys
import subprocess
import streamlit as st
import pickle
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_keplergl import keplergl_static

# Load parameter mapping from the query file
def load_parameter_mapping():
    """Load parameter code to name mapping from parameter_cd_query.csv"""
    mapping_file = 'code/Jorge/parameter_cd_query.csv'
    
    # Check if file exists
    if not os.path.exists(mapping_file):
        return {}
    
    try:
        # Read the mapping file with comma delimiter, skip header row
        df = pd.read_csv(mapping_file, skiprows=1)
        
        # Create mapping dictionary using parameter code as key and name as value
        # Column 0 = parameter code (parm_cd), Column 3 = parameter name (parm_nm)
        if 'parm_cd' in df.columns and 'parm_nm' in df.columns:
            mapping = dict(zip(df['parm_cd'], df['parm_nm']))
            return mapping
        else:
            # File exists but format is not as expected - return empty mapping instead of warning
            return {}
    except Exception as e:
        # File exists but can't be read properly - return empty mapping instead of warning
        return {}

# Load processed data
def load_data(data_dir, output_file):
    # Convert relative path to absolute path
    if not os.path.isabs(data_dir):
        data_dir = os.path.abspath(data_dir)

    # Use current working directory for output file
    output_path = os.path.join(os.getcwd(), output_file)
    if not os.path.exists(output_path):
        # Check if processed data file exists in data directory
        data_output_path = os.path.join(data_dir, output_file)
        if os.path.exists(data_output_path):
            # Move existing file to current directory
            os.rename(data_output_path, output_path)
        else:
            # Run data processing script
            print(f"Processing data from {data_dir}...")
            result = subprocess.run([
                sys.executable, 'data_processing.py',
                '--data-dir', data_dir,
                '--output-file', output_file
            ], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Error processing data: {result.stderr}")
                raise RuntimeError("Failed to process data")

    # Load processed data
    with open(output_path, 'rb') as f:
        return pickle.load(f)

def load_separate_data(data_dir):
    """Load both daily and instantaneous values data."""
    dv_file = 'processed_station_data_dv.pkl'
    ir_file = 'processed_station_data_ir.pkl'

    # Load daily values data
    dv_data = load_data(data_dir, dv_file)

    # Load instantaneous values data
    ir_data = load_data(data_dir, ir_file)

    return dv_data, ir_data

# Create map with station locations
def create_map(station_data, fit_bounds=False):
    from keplergl import KeplerGl
    import json

    # Prepare data for Kepler.gl
    map_data = []
    for station_id, data in station_data.items():
        lat, lon = data['location']
        map_data.append({
            'properties': {
                'station_id': station_id,
                'latitude': lat,
                'longitude': lon
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [lon, lat]
            }
        })

    # Calculate bounding box for initial map view
    lons = [feature['geometry']['coordinates'][0] for feature in map_data]
    lats = [feature['geometry']['coordinates'][1] for feature in map_data]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    # Calculate center point (average of all coordinates)
    center_lon = sum(lons) / len(lons)
    center_lat = sum(lats) / len(lats)

    # Set initial zoom level to 1
    zoom = 1

    # Calculate zoom level based on bounding box only when fit_bounds is True
    if fit_bounds:
        lon_diff = max_lon - min_lon
        lat_diff = max_lat - min_lat
        max_diff = max(lon_diff, lat_diff)

        # More accurate zoom calculation based on the extent of the data
        if max_diff < 0.05:
            zoom = 11
        elif max_diff < 0.1:
            zoom = 10
        elif max_diff < 0.5:
            zoom = 9
        elif max_diff < 1:
            zoom = 8
        elif max_diff < 2:
            zoom = 7
        elif max_diff < 5:
            zoom = 6
        else:
            zoom = 5
        # Ensure zoom level is at least 1
        zoom = max(zoom, 1)

    # Debug: Print data structure
    print("Map data structure:")
    print(f"Number of features: {len(map_data)}")
    print(f"First feature: {map_data[0]}")
    print(f"Bounding box: min_lon={min_lon}, max_lon={max_lon}, min_lat={min_lat}, max_lat={max_lat}")
    print(f"Center: lat={center_lat}, lon={center_lon}")
    print(f"Zoom level: {zoom}")

    # Create KeplerGl map object
    map_obj = KeplerGl(height=600)
    
    # Add data to the map
    geojson_data = {
        'type': 'FeatureCollection',
        'features': map_data
    }
    
    map_obj.add_data(data=geojson_data, name='stations')
    
    # Set map state and layer style after adding data
    # Note: In kepler.gl config spec, mapState belongs directly under config (not under visState)
    map_obj.config = {
        'version': 'v1',
        'config': {
            'mapState': {
                'bearing': 0,
                'dragRotate': False,
                'latitude': center_lat,
                'longitude': center_lon,
                'pitch': 0,
                'zoom': zoom,
                'isSplit': False
            },
            'visState': {
                'layers': [
                    {
                        'id': 'stations-point-layer',
                        'type': 'point',
                        'config': {
                            'dataId': 'stations',
                            'label': 'Stations',
                            'color': [255, 0, 0],
                            'columns': {
                                'lat': 'latitude',
                                'lng': 'longitude'
                            },
                            'isVisible': True,
                            'visConfig': {
                                'radius': 20,
                                'opacity': 0.8,
                                'outline': False
                            }
                        },
                        'visualChannels': {
                            'colorField': None,
                            'sizeField': None
                        }
                    }
                ]
            }
        }
    }
    
    return map_obj

# Plot time series data for daily values
def plot_time_series_dv(df, selected_column):
    fig = px.line(df, x=df.index, y=selected_column, title=f'Time Series: {selected_column}')
    fig.update_layout(
        xaxis_title='Date/Time',
        yaxis_title='Value',
        hovermode='x unified'
    )
    return fig

# Plot time series data for irregular values
def plot_time_series_ir(df):
    # For irregular data, we only use Activity_StartDate and Result_Measure
    if 'Activity_StartDate' in df.columns and 'Result_Measure' in df.columns:
        # Create a copy to avoid modifying the original data
        plot_df = df.copy()
        # Convert date column to datetime
        plot_df['Activity_StartDate'] = pd.to_datetime(plot_df['Activity_StartDate'])
        # Remove rows with NaN values in Result_Measure
        plot_df = plot_df.dropna(subset=['Result_Measure'])
        fig = px.scatter(plot_df, x='Activity_StartDate', y='Result_Measure', 
                         title='Irregular Data Time Series')
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Result Measure',
            hovermode='x unified'
        )
        return fig
    else:
        # Fallback if expected columns are not found
        fig = px.line(df, x=df.index, y=df.columns[0], title='Time Series')
        fig.update_layout(
            xaxis_title='Date/Time',
            yaxis_title='Value',
            hovermode='x unified'
        )
        return fig

# Main application
def main():
    st.title("NWIS Data Visualizer")
    
    # Permanent link to USGS parameter codes
    st.markdown("[USGS Parameter Codes Reference](https://help.waterdata.usgs.gov/codes-and-parameters/parameters)")
    
    # Load parameter mapping
    param_mapping = load_parameter_mapping()
    
    # Get data directory from user input
    st.sidebar.header("Data Configuration")
    data_dir = st.sidebar.text_input(
        "Data Directory",
        "data/00_raw/from_NWIS_Data_Extractor",
        help="Path to directory containing shapefile and CSV files"
    )

    output_file = st.sidebar.text_input(
        "Output File",
        "processed_station_data.pkl",
        help="Output file name for processed data"
    )

    # Load data
    dv_data, ir_data = load_separate_data(data_dir)

    # Data type selection
    st.sidebar.header("Data Type Selection")
    data_type = st.sidebar.radio(
        "Select data type",
        ("Daily Values (dv)", "Instantaneous Values (ir)")
    )

    # Select appropriate data based on user choice
    if data_type == "Daily Values (dv)":
        station_data = dv_data
        data_type_label = "Daily Values"
    else:
        station_data = ir_data
        data_type_label = "Instantaneous Values"

    # Display map
    st.header(f"Station Locations ({data_type_label})")
    st.write("Click on a station marker to view available parameters and data.")
    
    # Add zoom to layer button
    if 'fit_bounds' not in st.session_state:
        st.session_state.fit_bounds = False
    
    if st.button("Zoom to Stations Layer"):
        st.session_state.fit_bounds = True
    
    map_obj = create_map(station_data, fit_bounds=st.session_state.fit_bounds)
    keplergl_static(map_obj)
    
    # Reset fit_bounds after use
    if st.session_state.fit_bounds:
        st.session_state.fit_bounds = False

    # Station selection
    st.sidebar.header("Station Selection")
    station_ids = list(station_data.keys())
    selected_station = st.sidebar.selectbox("Select a station", station_ids)

    if selected_station:
        st.header(f"Station {selected_station} Data ({data_type_label})")
        station_info = station_data[selected_station]

        # Display available parameters with human-readable names
        parameters = sorted(list(station_info['parameters'].keys()))
        
        # Create a mapping from parameter codes to display names
        param_display_names = {}
        for param_code in parameters:
            if param_code in param_mapping:
                param_display_names[param_code] = f"{param_code} - {param_mapping[param_code]}"
            else:
                param_display_names[param_code] = param_code
        
        # Create a reverse mapping for selection handling
        param_reverse_mapping = {v: k for k, v in param_display_names.items()}
        
        # Display parameters with human-readable names
        display_param_list = [param_display_names[code] for code in parameters]
        st.write(f"Available parameters: {', '.join(display_param_list)}")

        # Parameter selection using display names
        selected_display_param = st.selectbox("Select a parameter to visualize", display_param_list)

        if selected_display_param:
            # Get the actual parameter code from the selection
            selected_parameter = param_reverse_mapping[selected_display_param]
            
            df = station_info['parameters'][selected_parameter]

            if data_type == "Daily Values (dv)":
                # Check if this is actually DV data (has datetimeUTC column)
                if 'datetimeUTC' in df.columns:
                    # Column selection for plotting (only for daily values)
                    columns = [col for col in df.columns if col != 'datetimeUTC']
                    if columns:
                        selected_column = st.selectbox("Select data column to plot", columns)

                        if selected_column:
                            # Convert datetime column to index
                            df['datetimeUTC'] = pd.to_datetime(df['datetimeUTC'])
                            df.set_index('datetimeUTC', inplace=True)

                            # Plot time series
                            st.header(f"Time Series: {selected_column}")
                            fig = plot_time_series_dv(df, selected_column)
                            st.plotly_chart(fig)

                            # Download option
                            st.download_button(
                                label="Download data as CSV",
                                data=df.to_csv(),
                                file_name=f"station_{selected_station}_{selected_parameter}_{selected_column}.csv",
                                mime="text/csv"
                            )
                else:
                    st.error("Selected data is not in the expected Daily Values format.")
            else:
                # For irregular data, check if it has the expected columns
                if 'Activity_StartDate' in df.columns and 'Result_Measure' in df.columns:
                    # For irregular data, we use the specific columns directly
                    st.header("Irregular Data Time Series")
                    fig = plot_time_series_ir(df)
                    st.plotly_chart(fig)

                    # Download option
                    st.download_button(
                        label="Download data as CSV",
                        data=df.to_csv(index=False),  # Keep index for irregular data
                        file_name=f"station_{selected_station}_{selected_parameter}_ir_data.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Selected data is not in the expected Irregular Values format.")

if __name__ == "__main__":
    main()
