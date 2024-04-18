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

def getboundaryofamperfromregion(data):
    amperboundaries = {}
    for i in data.index:
        geom = data.at[i, "geometry"]
        pv_name = data.at[i, 'pv_tn']
        re_name = data.at[i, "re_royin"]
        ap_name = data.at[i, 'ap_tn'] if 'ap_tn' in data else ""
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

        amperkey = (ap_name, pv_name)
        centroid = geom.centroid
        amperboundaries[amperkey] = {'cor': coordinates_list, 'centroid':centroid, 'bound': bound}

    return amperboundaries

def checktwoampernexttoeachother(amper1, amper2, distance_threshold=0.05):
    bound1 = all_amperboundaries[amper1]['bound']
    bound2 = all_amperboundaries[amper2]['bound']

    box_overlap = check_box_overlap(bound1, bound2, threshole = 0.01) 

    if box_overlap:
        for cor1 in all_amperboundaries[amper1]['cor']:
            for cor2 in all_amperboundaries[amper2]['cor']:
                distance = np.linalg.norm(np.array(cor1) - np.array(cor2))
                if distance < distance_threshold:
                    return True
    
    return False

with open('data_gen/allprovincesTH.txt', 'r', encoding='utf-8') as file:
    allprovinces = []
    for line in file:
        allprovinces.append(line.strip())

central = gpd.read_file('data_base/boundary/query-2.geojson')
east = gpd.read_file('data_base/boundary/query-3.geojson')
north = gpd.read_file('data_base/boundary/query-4.geojson')
south = gpd.read_file('data_base/boundary/query-5.geojson')
northeast = gpd.read_file('data_base/boundary/query-6.geojson')
west = gpd.read_file('data_base/boundary/query-7.geojson')

central_amperboundaries = getboundaryofamperfromregion(central)
east_amperboundaries = getboundaryofamperfromregion(east)
north_amperboundaries = getboundaryofamperfromregion(north)
south_amperboundaries = getboundaryofamperfromregion(south)
northeast_amperboundaries = getboundaryofamperfromregion(northeast)
west_amperboundaries = getboundaryofamperfromregion(west)

all_amperboundaries = {**central_amperboundaries, **east_amperboundaries, **north_amperboundaries, **south_amperboundaries, **northeast_amperboundaries, **west_amperboundaries}
allampers = list(all_amperboundaries.keys())

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('begin', type=int, help='The beginning index for slicing provinces.')
    parser.add_argument('end', type=int, help='The ending index for slicing provinces.')
    args = parser.parse_args()

    begin = int(args.begin)
    end = int(args.end)
    # allprovinces.sort()

    provinces_chosen = allprovinces[begin:end]

    province_index_now = begin
    for province in tqdm(provinces_chosen):
        province_index_now+=1
        print(f"Now gen {province}")
        amper1list = []
        for amper1 in allampers:
            provincename = amper1[1]
            if provincename == province:
                amper1list.append(amper1)

        savefolder = "data_gen_adjacency_districts/"

        file_name = str(province_index_now)+"_" +province + ".csv"

        if not os.path.exists(savefolder):
            os.makedirs(savefolder) 

        save_file_path = savefolder + file_name
        with open(save_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Amper1', 'Amper2', 'Adjacent'])

            for amper1 in tqdm(amper1list):
                for amper2 in tqdm(allampers): 
                    if amper1 != amper2:
                        checkvalue = checktwoampernexttoeachother(amper1, amper2)
                        if checkvalue:
                            csvwriter.writerow([amper1, amper2, 1])
