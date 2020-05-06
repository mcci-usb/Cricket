#======================================================================
# (c) 2020  MCCI, Inc.
#----------------------------------------------------------------------
# Project : UI3141/3201 GUI Application
# File    : main.py
#----------------------------------------------------------------------
# Main program entry point
#======================================================================

#======================================================================
# IMPORTS
#======================================================================
import os

import uiMainApp

#======================================================================
# MAIN PROGRAM
#======================================================================
def main ():
    # Determine the base directory path
    base = os.path.abspath(os.path.dirname(__file__))

    # If this file is within an archive, get its parent directory
    if not os.path.isdir(base):
        base = os.path.dirname(base)

    # Since this file lives in lib/, get the parent directory
    base = os.path.dirname(base)

    # Run the application
    uiMainApp.run()


if __name__ == '__main__':
    main()