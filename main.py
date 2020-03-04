#==========================================================================
# (c) 2020  MCCI Interconnect Solutions
#--------------------------------------------------------------------------
# Project : UI for 3141 and 3201 interface
# File    : main.py
#--------------------------------------------------------------------------
#  Main program entry point
#==========================================================================

#==========================================================================
# IMPORTS
#==========================================================================
import os
import sys

import conexApp

def main():
    # Determine the base directory path
	base = os.path.abspath(os.path.dirname(__file__))
	
	result = conexApp.run()
	sys.exit(result)
    

if __name__ == '__main__':
	main()