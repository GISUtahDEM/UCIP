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

from arcgis.gis import GIS, ContentManager
from arcgis.features import FeatureLayerCollection
import getpass
import arcpy


# Set variables, get AGOL username and password
portal_url = arcpy.GetActivePortalURL()
print(portal_url)

user = getpass.getpass(prompt='    Enter arcgis.com username:\n')
pw = getpass.getpass(prompt='    Enter arcgis.com password:\n')
arcpy.SignInToPortal(portal_url, user, pw)

my_agol = GIS(portal_url, user, pw)

del pw

# Set instance of Content Manager
cm = ContentManager(my_agol)

# The Hosted Feature Layer containing a countrywide dataset, currently UCIP_Survey_211129_Final
ucip_locs = my_agol.content.get('419155dca4844b94b44c68f68b4b4ccb')

ucip_locs_flc = FeatureLayerCollection.fromitem(ucip_locs)



# The Hosted Feature Layer containing the regional division
# Just counties: 
# counties = my_agol.content.get('5d55fd5a8ad34448a32b2b5e34ce9ab9').layers[0].query()
# Counties and Municipalities:
counties_munis = my_agol.content.get('c29faaea33da4cb680bf4a0e6a676732').layers[0].query()

# Get the Spatial Reference
spat_ref = counties_munis.spatial_reference

# Loop through the regional divisions to create the views
for index, county in enumerate(counties_munis):
    county_name = counties_munis.features[index].attributes['NAME']
    print(county_name)
    view_name = 'UCIP_' + "_" + county_name + "_View"
    print(view_name)
    
    # Get the geometry for the regions
    view_geom = counties_munis.features[index].geometry.get('rings')
    
    # Check if view has already been created using ContentManager Instance
    name_avail = cm.is_service_name_available(service_name = view_name,service_type = "featureService")
    
    if name_avail == True:
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
        print("Added ",view_name)
        
    else:
        print(view_name, " Exists")

print('Done!')
