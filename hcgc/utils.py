import networkx as nx
import numpy as np
from scipy.stats import kendalltau
import EoN

network_names = [
    "01_Dolphins", "02_USAir", "03_EEC", 
    "04_Email", "05_Euroroad", "06_Blogs",
    "07_Karate", "08_GDciting", "09_Celegan",
]

# Load real network data to generate the network
def load_graph_data(folder_name, name):
    if 'karate' in name.lower():
        G = nx.karate_club_graph()
    else:
        try:
            G = nx.read_edgelist(f"{folder_name}/{name}.edgelist", nodetype=np.int64)
        except:
            # edgelist contains simple weights, specify the data format explicitly
            G = nx.read_edgelist(f"{folder_name}/{name}.edgelist", nodetype=np.int64, data=(('weight', float),))
    # Identify self-loop edges
    self_loops = list(nx.selfloop_edges(G))

    # Remove all self-loop edges from the graph
    G.remove_edges_from(self_loops)
    
    N = nx.number_of_nodes(G)
    mapping = dict(zip(G, range(N)))
    G = nx.relabel_nodes(G, mapping)
    return G

def cal_Kendall_tau_coefficient(X, Y):
    tau, p_value = kendalltau(X, Y)
    return tau

# epidemic threshold: beta_c
def get_beta_c(G, N):
    k = sum([G.degree(i) for i in G.nodes()])/N
    square_k = sum([G.degree(i)**2 for i in G.nodes()])/N

    return k/(square_k-k)