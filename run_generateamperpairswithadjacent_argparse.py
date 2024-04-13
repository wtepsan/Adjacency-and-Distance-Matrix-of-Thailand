import numpy as np
import geopandas as gpd
from tqdm import tqdm
from itertools import product
import csv
import argparse

def getboundaryofamperfromregion(data):
    amperboundaries = {}
    for i in data.index:
        geom = data.at[i, "geometry"]
        pv_name = data.at[i, 'pv_tn']
        re_name = data.at[i, "re_royin"]
        ap_name = data.at[i, 'ap_tn'] if 'ap_tn' in data else ""

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
        amperboundaries[amperkey] = {'cor': coordinates_list, 'centroid':centroid}

    return amperboundaries

def checktwoampernexttoeachother(amper1, amper2, distance_threshold=0.05):
    centroid1 = all_amperboundaries[amper1]['centroid']
    centroid2 = all_amperboundaries[amper2]['centroid']

    centroid_distance = np.linalg.norm(np.array([centroid1.x, centroid1.y]) - np.array([centroid2.x, centroid2.y]))
    if centroid_distance < 2: 
        for cor1 in all_amperboundaries[amper1]['cor']:
            for cor2 in all_amperboundaries[amper2]['cor']:
                distance = np.linalg.norm(np.array(cor1) - np.array(cor2))
                if distance < distance_threshold:
                    return True
    
    return False

# provinces = gpd.read_file('./data/query.geojson')
# allprovinces = []
# for i in provinces.index:
#     geom = provinces.at[i, "geometry"]
#     pv_name = provinces.at[i, 'pv_tn'] 
#     allprovinces.append(pv_name)

# with open("data/allprovinces.txt", mode='w', encoding='utf-8') as file:
#     for province in allprovinces:
#         file.write(f"{province}\n")

with open('data/allprovinces.txt', 'r', encoding='utf-8') as file:
    allprovinces = []
    for line in file:
        # strip() removes any leading and trailing whitespace, including the newline character
        allprovinces.append(line.strip())

central = gpd.read_file('./data/query-2.geojson')
east = gpd.read_file('./data/query-3.geojson')
north = gpd.read_file('./data/query-4.geojson')
south = gpd.read_file('./data/query-5.geojson')
northeast = gpd.read_file('./data/query-6.geojson')
west = gpd.read_file('./data/query-7.geojson')

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

    provinces_chosen = allprovinces[begin:end]

    savefilename ="gen_data/" + str(begin)+"-"+str(end)+".csv"

    amper1list = []

    for amper1  in tqdm(allampers):
        provincename = amper1[1]
        if provincename in provinces_chosen:
            amper1list.append(amper1)

    print(f"{provinces_chosen}\nTotal District: {len(amper1list)}")
    
    with open(savefilename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Amper1', 'Amper2', 'Adjacent'])

        for amper1 in tqdm(amper1list):
            print(f"Now gen district: {amper1}")
            for amper2 in tqdm(allampers): 
                if amper1 != amper2:
                    checkvalue = checktwoampernexttoeachother(amper1, amper2)
                    if checkvalue:
                        csvwriter.writerow([amper1, amper2, 1])

## python3 run_generateamperpairswithadjacent_argparse.py 0 10
## python3 run_generateamperpairswithadjacent_argparse.py 10 20
## python3 run_generateamperpairswithadjacent_argparse.py 20 30
## python3 run_generateamperpairswithadjacent_argparse.py 30 40
## python3 run_generateamperpairswithadjacent_argparse.py 40 50
## python3 run_generateamperpairswithadjacent_argparse.py 50 60
## python3 run_generateamperpairswithadjacent_argparse.py 60 60
## python3 run_generateamperpairswithadjacent_argparse.py 70 -1