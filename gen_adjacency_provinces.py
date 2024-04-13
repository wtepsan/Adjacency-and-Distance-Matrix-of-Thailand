import numpy as np
import geopandas as gpd
from tqdm import tqdm
from itertools import product
import csv
import argparse
import os

def check_box_overlap(bound1, bound2, threshole = 0.01):
    min_lon1, min_lat1, max_lon1, max_lat1 = bound1[0], bound1[1], bound1[2], bound1[3]
    min_lon2, min_lat2, max_lon2, max_lat2 = bound2[0], bound2[1], bound2[2], bound2[3]

    # Check for overlap in latitude and longitude
    lat_overlap = max_lat1+threshole >= min_lat2-threshole and max_lat2+threshole >= min_lat1-threshole
    lon_overlap = max_lon1+threshole >= min_lon2-threshole and max_lon2+threshole >= min_lon1-threshole
    
    return lat_overlap and lon_overlap

def getboundaryofprovincefromregion(data):
    provinceboundaries = {}
    for i in data.index:
        geom = data.at[i, "geometry"]
        pv_name = data.at[i, 'pv_tn']
        re_name = data.at[i, "re_royin"]
        bound = geom.bounds

        if geom.geom_type == 'Polygon':
            # print("This geometry is a Polygon")
            coordinates_list = list(geom.exterior.coords)
            coordinates_list = [list(coordinate) for coordinate in coordinates_list]

        elif geom.geom_type == 'MultiPolygon':
            # print("This geometry is a MultiPolygon")
            polygon_list = list(geom.geoms)  
            coordinates_list = []
            for polygon in polygon_list:
                polygon_coordinates_list = list(polygon.exterior.coords)
                coordinates_list += [list(coordinate) for coordinate in polygon_coordinates_list]

        provincekey = pv_name
        centroid = geom.centroid
        provinceboundaries[provincekey] = {'cor': coordinates_list, 'centroid':centroid, 'bound': bound}

    return provinceboundaries

def checktwoprovincenexttoeachother(province1, province2, distance_threshold=0.05):
    bound1 = all_provinceboundaries[province1]['bound']
    bound2 = all_provinceboundaries[province2]['bound']

    box_overlap = check_box_overlap(bound1, bound2, threshole = 0.01) 

    if box_overlap:
        for cor1 in all_provinceboundaries[province1]['cor']:
            for cor2 in all_provinceboundaries[province2]['cor']:
                distance = np.linalg.norm(np.array(cor1) - np.array(cor2))
                if distance < distance_threshold:
                    return True
    
    return False

with open('data/allprovinces.txt', 'r', encoding='utf-8') as file:
    allprovinces = []
    for line in file:
        allprovinces.append(line.strip())

provinces = gpd.read_file('./data/query.geojson') 

provinces_provinceboundaries = getboundaryofprovincefromregion(provinces) 
all_provinceboundaries = {**provinces_provinceboundaries}
all_provinces = list(provinces_provinceboundaries.keys())

if __name__ == "__main__":

    savefolder = "gen_data_adjacency_provinces2/"
    if not os.path.exists(savefolder):
        os.makedirs(savefolder) 

    save_file_path = savefolder+"adjacency_provinces.csv"

    with open(save_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['province1', 'province2', 'Adjacent'])

        for province1 in tqdm(all_provinces):
            for province2 in tqdm(all_provinces): 
                if province1 != province2:
                    checkvalue = checktwoprovincenexttoeachother(province1, province2)
                    if checkvalue:
                        csvwriter.writerow([province1, province2, 1])