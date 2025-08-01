#!/usr/bin/env python3
"""
Data processing script for NWIS Data Visualizer.

This script processes the shapefile and CSV files to create a structured dataset
for the web GIS application.
"""

import os
import argparse
import pandas as pd
import geopandas as gpd
from glob import glob

def load_shapefile(shapefile_path):
    """Load the shapefile containing station locations."""
    print(f"Loading shapefile from {shapefile_path}")
    gdf = gpd.read_file(shapefile_path)
    print(f"Shapefile columns: {gdf.columns.tolist()}")
    print(f"Number of stations: {len(gdf)}")
    return gdf

def load_csv_files(data_dir, station_id, data_type='both'):
    """Load CSV files for a specific station based on data type."""
    station_data = {}

    if data_type in ['dv', 'both']:
        # Pattern for daily values (dv) files
        dv_pattern = os.path.join(data_dir, f"station_{station_id}_parameter_*_dv.csv")
        dv_files = glob(dv_pattern)

        for csv_file in dv_files:
            print(f"Processing {os.path.basename(csv_file)}")
            df = pd.read_csv(csv_file)

            # Extract parameter ID from filename
            filename = os.path.basename(csv_file)
            parts = filename.split('_')

            if len(parts) >= 4:
                # Handle dv file naming conventions
                if 'parameter' in parts:
                    param_index = parts.index('parameter') + 1
                    if param_index < len(parts):
                        parameter_id = parts[param_index]  # Extract parameter ID
                        station_data[parameter_id] = df

    if data_type in ['ir', 'both']:
        # Pattern for instantaneous values (ir) files
        ir_pattern = os.path.join(data_dir, f"station_{station_id}_WaterQualityData_parameter_*_ir.csv")
        ir_files = glob(ir_pattern)

        for csv_file in ir_files:
            print(f"Processing {os.path.basename(csv_file)}")
            df = pd.read_csv(csv_file)

            # Extract parameter ID from filename
            filename = os.path.basename(csv_file)
            parts = filename.split('_')

            if len(parts) >= 4:
                # Handle ir file naming conventions
                if 'parameter' in parts:
                    param_index = parts.index('parameter') + 1
                    if param_index < len(parts):
                        parameter_id = parts[param_index]  # Extract parameter ID
                        station_data[parameter_id] = df

    return station_data

def match_stations_with_data(shapefile_df, data_dir, data_type='combined'):
    """Match stations from shapefile with available CSV data."""
    station_data_map = {}

    for _, station in shapefile_df.iterrows():
        station_id = station['site_no']
        print(f"Processing station {station_id}")

        # Load CSV files for this station
        if data_type == 'dv':
            station_csv_data = load_csv_files(data_dir, station_id, 'dv')
        elif data_type == 'ir':
            station_csv_data = load_csv_files(data_dir, station_id, 'ir')
        else:
            station_csv_data = load_csv_files(data_dir, station_id, 'both')

        if station_csv_data:
            station_info = {
                'location': (station['dec_lat_va'], station['dec_long_v']),
                'parameters': station_csv_data
            }
            station_data_map[station_id] = station_info

    return station_data_map

def save_processed_data_separately(shapefile_df, data_dir):
    """Save processed data separately for dv and ir files."""
    import pickle

    # Process and save daily values (dv)
    dv_data = match_stations_with_data(shapefile_df, data_dir, 'dv')
    with open('processed_station_data_dv.pkl', 'wb') as f:
        pickle.dump(dv_data, f)
    print(f"Saved daily values data to processed_station_data_dv.pkl")

    # Process and save instantaneous values (ir)
    ir_data = match_stations_with_data(shapefile_df, data_dir, 'ir')
    with open('processed_station_data_ir.pkl', 'wb') as f:
        pickle.dump(ir_data, f)
    print(f"Saved instantaneous values data to processed_station_data_ir.pkl")

def save_processed_data(data, output_file):
    """Save processed data to a pickle file."""
    import pickle
    with open(output_file, 'wb') as f:
        pickle.dump(data, f)
    print(f"Saved processed data to {output_file}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process NWIS data for visualization.')
    parser.add_argument('--data-dir', required=True, help='Path to the data directory containing shapefile and CSV files')
    parser.add_argument('--output-file', default='processed_station_data.pkl', help='Output file path for processed data')
    parser.add_argument('--separate', action='store_true', help='Save daily and instantaneous values to separate files')
    args = parser.parse_args()

    # Configuration
    data_dir = args.data_dir
    shapefile_path = os.path.join(data_dir, "Shapefile_Stations.shp")
    output_file = args.output_file

    # Check if shapefile exists, if not try alternative name
    if not os.path.exists(shapefile_path):
        alternative_path = os.path.join(data_dir, "Shapefile_Stations.shp")
        if os.path.exists(alternative_path):
            shapefile_path = alternative_path
        else:
            raise FileNotFoundError(f"Shapefile not found in {data_dir}. Looking for Shapefile_Stations.shp or Shapefile_Stations.shp")

    # Load and process data
    shapefile_df = load_shapefile(shapefile_path)

    if args.separate:
        # Save data separately for dv and ir files
        save_processed_data_separately(shapefile_df, data_dir)
    else:
        # Load and process data (combined)
        processed_data = match_stations_with_data(shapefile_df, data_dir)

        # Save results
        save_processed_data(processed_data, output_file)
        print(f"Processed {len(processed_data)} stations")

if __name__ == "__main__":
    main()
