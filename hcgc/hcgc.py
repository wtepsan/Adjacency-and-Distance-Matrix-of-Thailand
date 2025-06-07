import math
import networkx as nx
import community
import igraph as ig

def _compute_local_modularity(G, degrees):
    # Community detection (expensive operation, do once)
    communities = community.best_partition(G)

    # Calculate local modularity
    local_modularity = {}
    for node in G.nodes():
        community_id = communities[node]
        internal_edges = sum(1 for neighbor in G.neighbors(node) 
                            if communities.get(neighbor) == community_id)
        total_edges = degrees[node]
        local_modularity[node] = internal_edges / total_edges if total_edges > 0 else 0
    return local_modularity

def _compute_dc_and(G, degrees):
    # Calculate DC_plus
    av_nei_deg = nx.average_neighbor_degree(G)
    dc_and = {i: degrees[i] * av_nei_deg[i] for i in G.nodes()}

    return dc_and

def compute_HCGC(G, R):

    DC = dict(G.degree())
    N = G.number_of_nodes()
    
    DC_AND = _compute_dc_and(G, DC)
    K_SHELL = nx.core_number(G)
    Local_Modularity = _compute_local_modularity(G, DC)

    # Compute Hybrid Community-based Gravity Centrality (HCGC)
    cLS_DCPlus_KSHELL_exLocalN = {
        node: math.exp(Local_Modularity[node]/N) * (DC_AND[node] * K_SHELL[node]) 
        for node in G.nodes()
    }

    # Convert to igraph
    g = ig.Graph.from_networkx(G)

    HCGC = {}
    for i in G.nodes():
        s0 = 0
        ball_i_R = set(g.neighborhood(i, order=R))
        ball_i_R.remove(i)
        for j in ball_i_R:
            dij = g.distances(i, j)[0][0]
            if dij > 0:
                s0 += (cLS_DCPlus_KSHELL_exLocalN[i] * cLS_DCPlus_KSHELL_exLocalN[j]) / (dij ** 2)
        HCGC[i] = s0

    return HCGC