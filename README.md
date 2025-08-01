# NWIS Data Visualizer

Live Application
- Streamlit (production): https://nwisdatavisualizerpublic-bjvtdfp3faklsy6perofaa.streamlit.app


<img width="370" height="831" alt="Screenshot 2025-07-24 at 3 36 09 AM" src="https://github.com/user-attachments/assets/613567fe-3bf0-42f5-b74f-5f8dfae08da9" />

Web GIS application for visualizing NWIS (National Water Information System) data using Streamlit and Kepler.gl.

## Features

- Interactive map displaying station locations
- Station selection with parameter visualization
- Time series data plotting
- Data download functionality

## Requirements

### Using pip (recommended for most users)
Install the required dependencies using:
```bash
pip install -r requirements.txt
```

### Using conda
For a more controlled environment, you can create a conda environment:
```bash
conda env create -f environment.yml
conda activate nwis2
```

## Usage

1. Prepare your data directory USING NWIS DATA EXTRACTOR TOOL with:
   - Shapefile containing station locations (`Shapefile_Stations.shp`)
   - CSV files for each station's parameters

2. Activate the conda environment (if using conda):
```bash
conda activate nwis2
```

3. Run the data processing script:
```bash
python code/Jorge/data_processing.py --data-dir data/00_raw/from_NWIS_Data_Extractor --separate
```

4. Launch the Streamlit application:
```bash
streamlit run app.py --server.port=8502
```
or 
```bash
streamlit run code/Jorge/app.py --server.port=8502
``` 
to run from original path of app.py file location.

5. Access the application at: [http://localhost:8502](http://localhost:8502)

6. After using the application you can shut down the streamlit server:
```shell
pkill -f "streamlit run app.py"
```

## Data Structure

The application expects:
- Shapefile with columns: `agency_cd`, `site_no`, `station_nm`, `site_tp_cd`, `dec_lat_va`, `dec_long_v`
- CSV files named following patterns:
  - Daily values: `station_{station_id}_parameter_{parameter_id}_dv.csv`
  - Instantaneous values: `station_{station_id}_WaterQualityData_parameter_{parameter_id}_ir.csv`

## Known Issues

- Kepler.gl may have rendering issues with very large datasets
- Some browsers may have performance limitations with complex visualizations
- Initial map zoom level calculation may not be optimal for all datasets

## Development

For development, it's recommended to install:
```bash
pip install watchdog  # Improves Streamlit performance
```

## License

This project is open source. See LICENSE file for details.
