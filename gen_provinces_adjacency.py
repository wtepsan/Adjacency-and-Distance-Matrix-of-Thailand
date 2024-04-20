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

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('begin', type=int, help='The beginning index for slicing provinces.')
    parser.add_argument('end', type=int, help='The ending index for slicing provinces.')
    args = parser.parse_args()

    begin = int(args.begin)
    end = int(args.end)
    
    province1lists = all_provinces[begin:end]
    
    savefolder = "gen_data_adjacency_provinces_update/"
    if not os.path.exists(savefolder):
        os.makedirs(savefolder) 

    province_index_now = begin 
    for province1 in tqdm(province1lists):
        print(f"NOW GEN {province1}")
        file_name = str(province_index_now)+"_adjacency_province_" + province1 + ".csv"
        save_file_path = savefolder + file_name
        with open(save_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['province1', 'province2', 'Adjacent'])
        
            for province2 in tqdm(all_provinces): 
                if province1 != province2:
                    checkvalue = checktwoprovincenexttoeachother(province1, province2)
                    if checkvalue:
                        csvwriter.writerow([province1, province2, 1])


# python3 gen_adjacency_provinces2.py 0 5
# python3 gen_adjacency_provinces2.py 5 10
# python3 gen_adjacency_provinces2.py 10 15
# python3 gen_adjacency_provinces2.py 15 20
# python3 gen_adjacency_provinces2.py 20 25
# python3 gen_adjacency_provinces2.py 25 30
# python3 gen_adjacency_provinces2.py 30 35
# python3 gen_adjacency_provinces2.py 35 40
# python3 gen_adjacency_provinces2.py 40 45
# python3 gen_adjacency_provinces2.py 45 50
# python3 gen_adjacency_provinces2.py 50 55
# python3 gen_adjacency_provinces2.py 55 60
# python3 gen_adjacency_provinces2.py 60 65
# python3 gen_adjacency_provinces2.py 65 70
# python3 gen_adjacency_provinces2.py 70 75
# python3 gen_adjacency_provinces2.py 75 80



