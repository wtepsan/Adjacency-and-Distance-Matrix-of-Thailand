import numpy as np
import networkx as nx
from utils import *
from hcgc import compute_HCGC
import os

# Set truncation radius (R=2) and (R=3)
R_list = [2, 3]

# Define the beta_c sampling range
nums = 11

folder_name = "public_data"

for R in R_list:
    # Scores comparison
    for network_name in network_names:
        print(f"R: {R}\n{network_name} Network:\n")

        if 'karate' in network_name.lower():
            G = nx.karate_club_graph()
        else:
            G = load_graph_data(folder_name, network_name)
        
        # Get beta_c
        beta_c = get_beta_c(G, len(G.nodes()))

        # Calculate HCGC scores
        HCGC_scores = compute_HCGC(G, R)

        # Kendall's Tau comparison
        X = list(HCGC_scores.values())

        # Generate beta list and tau list
        beta_list = np.linspace(0.5, 1.5, nums) * beta_c
        tau_list = np.zeros(nums)

        # Loading standard ranking
        SR = np.loadtxt("./standard_ranking_results/standard_ranking_" + network_name + ".csv", delimiter=',', dtype=np.float64)
        
        # Create output file directory if it doesn't exist
        if not os.path.exists(f"./kendall_tau_r{R}_results"):
            print(f"Creating directory: ./kendall_tau_r{R}_results")
            os.makedirs(f"./kendall_tau_r{R}_results")
        outf = open(f"./kendall_tau_r{R}_results/kendall_tau_" + network_name + ".dat", "w")
        for i, beta in enumerate(beta_list):
            SRi = SR[:, i+1]
            Y = list(SRi)
            tau_list[i] = cal_Kendall_tau_coefficient(X, Y)

            # Write to file
            outf.write(str(beta/beta_c) + " " + str(tau_list[i]) + "\n")

        outf.close()