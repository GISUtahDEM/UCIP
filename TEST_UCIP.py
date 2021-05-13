# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 13:14:40 2021

@author: jsurkis
"""

## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
## Script: agol_define_areas_of_interest_on_hosted_feature_layer_views.py
## Goal: to define an area of interest on multiple hosted feature layer views using input geometry
## Author: Egge-Jan Polle - Tensing GIS Consultancy
## Date: March 27, 2019
## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# This script should be run within a specific ArcGIS/Python environment using the batch file below
# (This batch file comes with the installation of ArcGIS Pro)
# "C:\Program Files\ArcGIS\Pro\bin\Python\scripts\propy.bat" agol_define_areas_of_interest_on_hosted_feature_layer_views.py

from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
# import os, sys
# import time
import getpass
# import requests
# import random
import arcpy
# import pandas as pd
# import numpy as np
# import datetime as dt
# from provide_credentials import provide_credentials

# username, password = provide_credentials()

# Set variables, get AGOL username and password
portal_url = arcpy.GetActivePortalURL()
print(portal_url)

user = getpass.getpass(prompt='    Enter arcgis.com username:\n')
pw = getpass.getpass(prompt='    Enter arcgis.com password:\n')
arcpy.SignInToPortal(portal_url, user, pw)

my_agol = GIS(portal_url, user, pw)

del pw

# The Hosted Feature Layer containing a countrywide dataset 
ucip_locs = my_agol.content.get('b7b6a64765e64753af7d84ca0377e3ef')
# ucip_locs= r'https://services6.arcgis.com/KaHXE9OkiB9e63uE/arcgis/rest/services/survey123_e50a93b1f8904908b4297f24a3b44666/FeatureServer/0'
#'b7b6a64765e64753af7d84ca0377e3ef'

ucip_locs_flc = FeatureLayerCollection.fromitem(ucip_locs)




# The Hosted Feature Layer containing the regional division
counties = my_agol.content.get('5d55fd5a8ad34448a32b2b5e34ce9ab9').layers[0].query()
#counties = r'https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/UtahCountyBoundaries/FeatureServer/0'
# '5d55fd5a8ad34448a32b2b5e34ce9ab9'

# Get the Spatial Reference
spat_ref = counties.spatial_reference

# Loop through the regional division to create the views
for index, county in enumerate(counties):
    county_name = counties.features[index].attributes['NAME']
    print(county_name)
    view_name = '4UCIP' + "_" + county_name + "_County_View"
    print(view_name)
    # Get the geometry for the regions
    view_geom = counties.features[index].geometry.get('rings')
    new_view = ucip_locs_flc.manager.create_view(name=view_name)

    # Search for newly created View
    view_search = my_agol.content.search(view_name)[0]
    view_flc = FeatureLayerCollection.fromitem(view_search)

    service_layer = view_flc.layers[0]

    # Populate the update_dict with the geometry and the spatial reference
    update_dict = {"viewLayerDefinition":{"filter":   
    {"operator":"esriSpatialRelContains","value":
    {"geometryType":"esriGeometryPolygon","geometry":
    {"rings": view_geom,
    "spatialReference":spat_ref}}}}}

    # Update the definition to include the Area of Interest
    service_layer.manager.update_definition(update_dict)

print('Done!')