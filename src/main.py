##############################################################################
# 
# Module: main.py
#
# Description:
#     Main program entry point
#
# Copyright notice:
#     This file copyright (c) 2020 by
#
#         MCCI Corporation
#         3520 Krums Corners Road
#         Ithaca, NY  14850
#
#     Released under the MCCI Corporation.
#
# Author:
#     Seenivasan V, MCCI Corporation Mar 2020
#
# Revision history:
#     V2.4.0 Wed July 14 2021 15:20:05   Seenivasan V
#       Module created
##############################################################################
# Built-in imports
import os

# Own modules
import uiMainApp

__author__ = 'Seenivasan V'
__contact__ = 'seenivasanv@mcci.com'
__credits__ = ['Terry Moore', 'Velmurugan Selvaraj']
__date__ = '2021/07/12'
__maintainer__ = ['Seenivasan V', 'Vinay N']
__status__ = 'Production'
__version__ = '2.3.14'
##############################################################################
# Utilities
##############################################################################
def main ():
    """
    Main program entry point
    Args:
        No argument
    Return:
        None
    """
    # Determine the base directory path
    base = os.path.abspath(os.path.dirname(__file__))

    # If this file is within an archive, get its parent directory
    if not os.path.isdir(base):
        base = os.path.dirname(base)

    # Since this file lives in lib/, get the parent directory
    base = os.path.dirname(base)

    # Run the application
    uiMainApp.run()

# python program to use
# main for function call.
if __name__ == '__main__':
    main()