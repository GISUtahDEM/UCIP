#!/usr/bin/env python
# coding: utf-8

# In[8]:


from arcgis.gis import GIS
from arcgis.gis import ContentManager
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

cm = ContentManager(my_agol)


# In[9]:


# The Hosted Feature Layer containing a statewide dataset (Currently UCIP_Live_Layer)
#ucip_locs = my_agol.content.get('b81c64945f004ef28e9dba448e0a677e')
#ucip_locs = my_agol.content.get('419155dca4844b94b44c68f68b4b4ccb')
ucip_locs = my_agol.content.get('f3e43dcc7fc3495ea8731597b63b690d') #UCIP_Live_Layer


ucip_locs_flc = FeatureLayerCollection.fromitem(ucip_locs)
ucip_locs_layer = ucip_locs.layers[0]
ucip_properties = ucip_locs_layer.properties
ucip_symbology = (ucip_properties["drawingInfo"])


# In[10]:


# The Hosted Feature Layer containing the regional division, counties and counties + municipalities

counties = my_agol.content.get('5d55fd5a8ad34448a32b2b5e34ce9ab9').layers[0].query() #just counties
counties_munis_gap = my_agol.content.get('c29faaea33da4cb680bf4a0e6a676732').layers[0].query() #gap in counties where municipalities are, plus municipalities
counties_munis = my_agol.content.get('6e5e56892ecb4be5990467419f69d248').layers[0].query()#counties and municipalities overlapping
counties_gaps = my_agol.content.get('f98099791f8745ae8159e27735610b3f').layers[0].query() #just counties with gaps where municipalities are

# Get the Spatial Reference
spat_ref = counties_munis.spatial_reference

'''For all items below this, switching counties with county_munis will
change the geometry to include counties and municipalities'''


# In[5]:


#ucip_properties
fields = ucip_properties.fields
fields


# In[14]:


# Loop through the regional division to create the views or update existing views for ALL JURISDICTIONS
for index, county in enumerate(counties_munis):
    county_name = counties_munis.features[index].attributes['NAME']
    print(county_name)
    view_name = 'UCIP_' + county_name + "_LIVE_View"
    print(view_name)
    # Get the geometry for the regions
    view_geom = counties_munis.features[index].geometry.get('rings')
    name_avail = cm.is_service_name_available(service_name = view_name,service_type = "featureService")
    # Check if view exists
    if  name_avail == True:
        new_view = ucip_locs_flc.manager.create_view(name=view_name)
        # Search for newly created View
        view_search = my_agol.content.search(view_name)[0]
        view_flc = FeatureLayerCollection.fromitem(view_search)

        service_layer = view_flc.layers[0]
        layerTags = [county_name,view_name,"UCIP","View Layer","Live"]


        
        # Populate the update_dict with the geometry and the spatial reference
        update_dict = {"tags":layerTags,"viewLayerDefinition":{"filter":
                                                               {"operator":"esriSpatialRelContains","value":
                                                                {"geometryType":"esriGeometryPolygon","geometry":
                                                                 {"rings": view_geom,
                                                                  "spatialReference":spat_ref}}}}}
        
        # Assign category to new view layer
        service_layer_id=view_search.id
        my_agol.content.categories.assign_to_items(items = [{service_layer_id: {
                                                     "categories": ["/Categories/UCIP"]}}])

        
        # Update the definition to include the Area of Interest
        service_layer.manager.update_definition(update_dict)
        
        
        # Move layer to UCIP live folder
        view_search.move(folder="UCIP - LIVE")

        print("Added ",view_name)
    
    else:
        print(view_name," Exists")
        
        # Search for newly View
        view_search = my_agol.content.search(view_name)[0]
        view_flc = FeatureLayerCollection.fromitem(view_search)

        service_layer = view_flc.layers[0]
        layerTags = [county_name,view_name,"UCIP","View Layer"]

        ##append any new fields from the master layer
        #url = view_search.url
        #f_lyr = arcgis.features.FeatureLayer(url, my_agol)
        #f_lyr.append(append_fields= ["asset_owner", "asset_hours","building_type","match_jurisdiction","out_of_bounds_note"])


        # Populate the update_dict with the geometry and the spatial reference
        dict_fields = [{"name":f"{f.name}","visible":True} for f in fields]
        #print(dict_fields)


        update_dict = {"tags":layerTags,"fields":dict_fields}
#                       "viewLayerDefinition":{"filter":
#                                                               {"operator":"esriSpatialRelContains","value":
#                                                                {"geometryType":"esriGeometryPolygon","geometry":
#                                                                 {"rings": view_geom,
#                                                                  "spatialReference":spat_ref}}}}}
        #print(service_layer.properties.tags)
        service_layer.manager.update_definition(update_dict)


        # Update the definition to include the tags
        view_search.update(update_dict)
        print("Updated ",view_name)

        #update_dict2 = {"drawingInfo":ucip_symbology}
        #view_search.update(update_dict2)
        #print("Applied Symbology to ",view_name)


print('Done!')


# In[9]:


# Loop through the regional division to create the views COUNTIES ONLY VIEW ONLY
for index, county in enumerate(counties):
    county_name = counties.features[index].attributes['NAME']
    print(county_name)
    view_name = 'UCIP_' + county_name + "_LIVE_ViewONLY"
    print(view_name)
    # Get the geometry for the regions
    view_geom = counties.features[index].geometry.get('rings')
    name_avail = cm.is_service_name_available(service_name = view_name,service_type = "featureService")
    # Check if view exists
    if  name_avail == True:
        new_view = ucip_locs_flc.manager.create_view(name=view_name)
        # Search for newly created View
        view_search = my_agol.content.search(view_name)[0]
        view_flc = FeatureLayerCollection.fromitem(view_search)

        service_layer = view_flc.layers[0]
        layerTags = [county_name,view_name,"UCIP","View Layer","Live"]


        
        # Populate the update_dict with the geometry and the spatial reference
        update_dict = {"tags":layerTags,"viewLayerDefinition":{"filter":
                                                               {"operator":"esriSpatialRelContains","value":
                                                                {"geometryType":"esriGeometryPolygon","geometry":
                                                                 {"rings": view_geom,
                                                                  "spatialReference":spat_ref}}}}}
        
        # Assign category to new view layer
        service_layer_id=view_search.id
        my_agol.content.categories.assign_to_items(items = [{service_layer_id: {
                                                     "categories": ["/Categories/UCIP"]}}])
        
        # Add layer to UCIP_LIVE folder
        

        # Update the definition to include the Area of Interest
        service_layer.manager.update_definition(update_dict)
        
        # Move layer to UCIP live folder
        view_search.move(folder="UCIP - LIVE")

        print("Updated ",view_name)
    else:
        view_search = my_agol.content.search(view_name)[0]
        view_flc = FeatureLayerCollection.fromitem(view_search)

        service_layer = view_flc.layers[0]
        layerTags = [county_name,view_name,"UCIP","View Layer","Live"]


        
        # Populate the update_dict with the geometry and the spatial reference
        update_dict = {"tags":layerTags,"viewLayerDefinition":{"filter":
                                                               {"operator":"esriSpatialRelContains","value":
                                                                {"geometryType":"esriGeometryPolygon","geometry":
                                                                 {"rings": view_geom,
                                                                  "spatialReference":spat_ref}}}}}
        
        # Assign category to new view layer
        service_layer_id=view_search.id
        my_agol.content.categories.assign_to_items(items = [{service_layer_id: {
                                                     "categories": ["/Categories/UCIP"]}}])
        
        # Add layer to UCIP_LIVE folder
        

        # Update the definition to include the Area of Interest
        service_layer.manager.update_definition(update_dict)
        
        # Move layer to UCIP live folder
        view_search.move(folder="UCIP - LIVE")

        print("Updated ",view_name)



print('Done!')


# In[25]:


# Loop through the regional division to create the views COUNTIES ONLY
for index, county in enumerate(counties):
    county_name = counties.features[index].attributes['NAME']
    print(county_name)
    view_name = 'UCIP_' + county_name + "_All_LIVE_View"
    print(view_name)
    # Get the geometry for the regions
    view_geom = counties.features[index].geometry.get('rings')
    name_avail = cm.is_service_name_available(service_name = view_name,service_type = "featureService")
    # Check if view exists
    if  name_avail == True:
        new_view = ucip_locs_flc.manager.create_view(name=view_name)
        # Search for newly created View
        view_search = my_agol.content.search(view_name)[0]
        view_flc = FeatureLayerCollection.fromitem(view_search)

        service_layer = view_flc.layers[0]
        layerTags = [county_name,view_name,"UCIP","View Layer","Live"]


        
        # Populate the update_dict with the geometry and the spatial reference
        update_dict = {"tags":layerTags,"viewLayerDefinition":{"filter":
                                                               {"operator":"esriSpatialRelContains","value":
                                                                {"geometryType":"esriGeometryPolygon","geometry":
                                                                 {"rings": view_geom,
                                                                  "spatialReference":spat_ref}}}}}
        
        # Assign category to new view layer
        service_layer_id=view_search.id
        my_agol.content.categories.assign_to_items(items = [{service_layer_id: {
                                                     "categories": ["/Categories/UCIP"]}}])
        
        # Add layer to UCIP_LIVE folder
        

        # Update the definition to include the Area of Interest
        service_layer.manager.update_definition(update_dict)
        
        # Move layer to UCIP live folder
        view_search.move(folder="UCIP - LIVE")

        print("Added ",view_name)
    elif view_name == "UCIP_WASHINGTON_All_LIVE_View":
        view_search = my_agol.content.search(view_name)[0]
        view_flc = FeatureLayerCollection.fromitem(view_search)

        service_layer = view_flc.layers[0]
        layerTags = [county_name,view_name,"UCIP","View Layer","Live"]
        dict_fields = [{"name":f"{f.name}","visible":True} for f in fields]



        
        # Populate the update_dict with the geometry and the spatial reference
        update_dict = {"tags":layerTags,"drawingInfo":ucip_symbology,"fields":dict_fields}
        
        # Assign category to new view layer
        service_layer_id=view_search.id
        my_agol.content.categories.assign_to_items(items = [{service_layer_id: {
                                                     "categories": ["/Categories/UCIP"]}}])
        
        # Add layer to UCIP_LIVE folder
        

        # Update the definition to include the Area of Interest
        ucip_properties2 = ucip_properties
        #del ucip_properties2['editingInfo']
        service_layer.manager.update_definition(ucip_properties2)
        
        # Move layer to UCIP live folder
        view_search.move(folder="UCIP - LIVE")

        print("Updated ",view_name)
    else:
        print("Exists")


# In[ ]:


import json

def update_layer_def(item):
    item_data = item.get_data()
    if item_data is not None:
        # Here note we are changing a specific part of the Layer Definition
        layer_def = item_data['layers'][3]['layerDefinition']
        print("*******************ORIGINAL DEFINITION*********************")
        print(json.dumps(item_data, indent=4, sort_keys=True))

        # Open JSON file containing symbology update
        with open('/path/to/drawingInfo.json') as json_data:
            data = json.load(json_data)

        # Set the drawingInfo equal to what is in JSON file
        layer_def['drawingInfo'] = data

        # Set the item_properties to include the desired update
        item_properties = {"text": json.dumps(item_data)}

        # 'Commit' the updates to the Item
        item.update(item_properties=item_properties)

        # Print item_data to see that changes are reflected
        new_item_data = item.get_data()
        print("***********************NEW DEFINITION**********************")
        print(json.dumps(new_item_data, indent=4, sort_keys=True))
    
    else:
        print("There is no Layer Definition at the moment..creating one...")
        create_layer_def(item)


# In[21]:


#Remove Editing Info from JSON

ucip_properties2 = ucip_properties
del ucip_properties2['editingInfo']
ucip_properties2


# In[27]:


# Get Master Layer Info

import arcgis
resturl=dict(ucip_locs)["url"]
layerurl=str(resturl)+"/"+str(0)
layer=arcgis.features.FeatureLayer(layerurl)

print(layerurl+"?f=pjson")
print(layer.properties)


# In[ ]:


# Print County Names

for index, county in enumerate(counties):
    ind = len(counties_munis) - index - 1
    county_name = counties_munis.features[ind].attributes['NAME']
    if county_name[-4:] == "_ALL": 
        print(county_name)


# In[ ]:


# Run this to delete all view layers 

if_delete = input("Do you want to delete all view layers?")
if if_delete == "yes":
    for index, county in enumerate(counties_munis):
        county_name = counties_munis.features[index].attributes['NAME']
        print(county_name)
        view_name = 'UCIP_' + county_name + "_LIVE_View"
        print(view_name)
        # Get the geometry for the regions
        view_geom = counties_munis.features[index].geometry.get('rings')
        name_avail = cm.is_service_name_available(service_name = view_name,service_type = "featureService")
        # Check if view exists
        if  name_avail == False:
            view_search = my_agol.content.search(view_name)[0]
            view_search.delete()
            print(view_name + " has been deleted.")


# In[ ]:


# Backup as FGDB
from datetime import datetime
from arcgis.gis import GIS 
import arcpy 
import os 
import zipfile 
import glob 
import shutil 

current_time = datetime.now()
date = current_time.strftime('%m_%d_%y')

fgdb_title = ucip_locs.title 
fgdb_title=fgdb_title.replace('_', '')
fgdb_title=fgdb_title+"_"+date
print(fgdb_title)

root = r"C:\UCIP" 
#result = ucip_locs.export(fgdb_title, "File Geodatabase")
#items = gis.content.search(nombre)
result = ucip_locs.export(fgdb_title, 'File Geodatabase', parameters=None, wait='True') 
result.download(root)

