#!/usr/bin/env python3
"""
Test script to verify the new parameter mapping from CSV file
"""

import os
import pandas as pd

def test_new_parameter_mapping():
    """Test that we can load and use the new parameter mapping from CSV"""
    
    # Load parameter mapping
    mapping_file = 'code/Jorge/parameter_cd_query_fixed.csv'
    
    # Check if file exists
    if not os.path.exists(mapping_file):
        print("Parameter mapping CSV file not found")
        return False
    
    try:
        # Read the mapping file with comma delimiter
        df = pd.read_csv(mapping_file)
        
        print(f"Successfully loaded parameter mapping with {len(df)} entries")
        print("Columns:", df.columns.tolist())
        print("First few rows:")
        print(df.head())
        
        # Test specific examples from the task
        test_codes = ['00060', '00065']
        print("\nTesting specific codes:")
        for code in test_codes:
            # Find the row with this code
            matching_rows = df[df['parm_cd'] == code]
            if not matching_rows.empty:
                name = matching_rows.iloc[0]['parm_nm']
                print(f"  {code} -> {name}")
            else:
                print(f"  {code} -> Not found in mapping")
        
        return True
            
    except Exception as e:
        print(f"Error loading parameter mapping: {e}")
        return False

if __name__ == "__main__":
    test_new_parameter_mapping()
