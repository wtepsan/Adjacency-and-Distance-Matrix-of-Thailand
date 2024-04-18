### GENERATE DISTANCE MATRIX
import pandas as pd
import googlemaps
from itertools import tee
import numpy as np
from tqdm import tqdm
import argparse
import ast

df = pd.read_csv("data_gen/allampers_collected.csv")
df.head()

amperin = []
ampernotin = []
allampers_collected_tuples = []

for i in range(len(df)):
    amper = df.iloc[i]['Amper TH']
    province = df.iloc[i]['Province TH']
    lat = df.iloc[i]['Lat']
    lon = df.iloc[i]['Lon']

    amper_tuple = (amper, province)
    lat_lon = (lat, lon)

    allampers_collected_tuples.append(amper_tuple)

allampers = pd.read_csv("data_gen/allampers.csv")
API_key = 'AIzaSyAwhv0CadDKHu6PJWf1eOxoGDJvwNwnqq8'
gmaps = googlemaps.Client(key=API_key)

allampers_df = pd.read_csv("data_gen/allampers_collected.csv")

def distancebetween(amper1_tuple, amper2_tuple):
    amper1 = amper1_tuple[0]
    province1 = amper1_tuple[1]
    origin_df = allampers_df[(allampers_df['Amper TH'] == amper1) & (allampers_df['Province TH'] == province1)]
    original_lat = origin_df['Lat']
    original_lon = origin_df['Lon']
    origin_location = (original_lat, original_lon)

    amper2 = amper2_tuple[0]
    province2 = amper2_tuple[1]
    destination_df = allampers_df[(allampers_df['Amper TH'] == amper2) & (allampers_df['Province TH'] == province2)]
    destination_lat = destination_df['Lat']
    destination_lon = destination_df['Lon']
    destination_location = (destination_lat, destination_lon)
     

    try: 
        if (amper1_tuple in allampers_collected_tuples) and (amper2_tuple in allampers_collected_tuples):
            result = gmaps.distance_matrix(origin_location, destination_location, mode = 'driving')
        else: 
            result['original'] = amper1
            result['original_tuple'] = (amper1, province1)
            result['destination'] =  amper2
            result['destination_tuple'] = (amper2, province2)
            result['original address'] = "else no address"
            result['destination address'] = "else no address"
            result['distance'] = -8888.88
            result['time'] = -8888.88
    except:
        result['original'] = amper1
        result['original_tuple'] = (amper1, province1)
        result['destination'] =  amper2
        result['destination_tuple'] = (amper2, province2)
        result['original address'] = "except no address"
        result['destination address'] = "except no address"
        result['distance'] = -9999.99
        result['time'] = -9999.99
            
    return result