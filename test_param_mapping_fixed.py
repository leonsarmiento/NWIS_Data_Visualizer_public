#!/usr/bin/env python3
"""
Test script to verify parameter mapping functionality with the fixed implementation
"""

import os
import pandas as pd

def test_parameter_mapping():
    """Test that we can load and use the parameter mapping correctly"""
    
    # Load parameter mapping
    mapping_file = 'code/Jorge/parameter_cd_query.txt'
    
    # Check if file exists
    if not os.path.exists(mapping_file):
        print("Parameter mapping file not found")
        return False
    
    try:
        # Read the mapping file with tab delimiter, skip first 2 rows (header and data type rows)
        # Only read the first 3 columns as needed for display
        df = pd.read_csv(mapping_file, sep='\t', skiprows=2, header=None, usecols=[0, 1, 2])
        
        print(f"Successfully loaded parameter mapping with {len(df)} entries")
        print("First few rows (columns 0, 1, 2):")
        print(df.head())
        
        # Show first 5 mappings (code -> name)
        print("\nSample mappings (code -> name):")
        for i in range(min(5, len(df))):
            code = df.iloc[i][0]
            name = df.iloc[i][2]  # Third column is the parameter name
            print(f"  {code} -> {name}")
        
        # Test specific examples from the task
        test_codes = ['00060', '00065']
        print("\nTesting specific codes:")
        for code in test_codes:
            # Find the row with this code
            matching_rows = df[df[0] == code]
            if not matching_rows.empty:
                name = matching_rows.iloc[0][2]  # Third column is the parameter name
                print(f"  {code} -> {name}")
            else:
                print(f"  {code} -> Not found in mapping")
        
        return True
            
    except Exception as e:
        print(f"Error loading parameter mapping: {e}")
        return False

if __name__ == "__main__":
    test_parameter_mapping()
