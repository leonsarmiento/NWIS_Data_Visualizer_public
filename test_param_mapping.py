#!/usr/bin/env python3
"""
Test script to verify parameter mapping functionality
"""

import os
import pandas as pd

def test_parameter_mapping():
    """Test that we can load and use the parameter mapping"""
    
    # Load parameter mapping
    mapping_file = 'code/Jorge/parameter_cd_query.txt'
    
    # Check if file exists
    if not os.path.exists(mapping_file):
        print("Parameter mapping file not found")
        return False
    
    try:
        # Read the mapping file with tab delimiter
        df = pd.read_csv(mapping_file, sep='\t', skiprows=2, header=0)
        
        # Check if required columns exist
        if 'parm_cd' in df.columns and 'parm_nm' in df.columns:
            print(f"Successfully loaded parameter mapping with {len(df)} entries")
            print("Sample mappings:")
            
            # Show first 5 mappings
            for i, (code, name) in enumerate(zip(df['parm_cd'].head(), df['parm_nm'].head())):
                print(f"  {code} -> {name}")
            
            # Test specific examples from the task
            test_codes = ['00060', '00065']
            print("\nTesting specific codes:")
            for code in test_codes:
                if code in df['parm_cd'].values:
                    name = df[df['parm_cd'] == code]['parm_nm'].iloc[0]
                    print(f"  {code} -> {name}")
                else:
                    print(f"  {code} -> Not found in mapping")
            
            return True
        else:
            print("Required columns not found in parameter mapping file")
            return False
            
    except Exception as e:
        print(f"Error loading parameter mapping: {e}")
        return False

if __name__ == "__main__":
    test_parameter_mapping()
