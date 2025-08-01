#!/usr/bin/env python3
"""
Streamlit entrypoint for Streamlit Community Cloud.

This wrapper ensures the app can be launched from the repository root.
It imports and runs the main() function from code/Jorge/app.py.
"""

import os
import sys

# Ensure project root and code directory are on sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.join(ROOT_DIR, "code")
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

# Import and run the app
from Jorge.app import main

if __name__ == "__main__":
    main()
