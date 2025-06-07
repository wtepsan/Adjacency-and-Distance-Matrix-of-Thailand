from utils import *
import networkx as nx
import numpy as np

# Step 3: Simulate SIR model for each node
def simulate_sir_spreading(G, node, beta, gamma, tmax, report_times, iterations):
    """Simulate SIR spreading from a single node"""
    # Initial condition: only the seed node is infected
    initial_infecteds = [node]
    
    obs_R = 0 * report_times
    for counter in range(iterations):
        # Run the simulation
        t, S, I, R = EoN.fast_SIR(G, beta, gamma, initial_infecteds=initial_infecteds, tmax=tmax)
        obs_R += EoN.subsample(report_times, t, R)
    SR = obs_R[-1] / iterations  # Average over iterations
    # Return the final size of the epidemic (R at the end)
    return SR #R[-1]

def compute_sir_scores(G, beta, iterations):
    # Parameters for SIR model
    # beta = 0.16  # infection probability (from the paper for Karate network)
    gamma = 1.0  # recovery rate
    # T = 20       # simulation time
    tmin, tmax = 0.0, 50.0
    report_times = np.linspace(tmin, tmax, 21)

    # Calculate spreading ability for each node
    sir_results = {}
    for node in G.nodes():
        # Run multiple simulations to get average spreading ability
        # spreading_ability = 0
        # num_simulations = 100  # As mentioned in the paper
        # for _ in range(num_simulations):
        #     spreading_ability += simulate_sir_spreading(G, node, beta, gamma, tmax, report_times, iterations)
        # sir_results[node] = spreading_ability / num_simulations

        sir_results[node]  = simulate_sir_spreading(G, node, beta, gamma, tmax, report_times, iterations)

    return sir_results

if __name__ == '__main__':

    folder_name = "public_data"

    for name in network_names:
        if 'karate' in name.lower():
            G = nx.karate_club_graph()
        else:
            G = load_graph_data(folder_name, name)
        N, M = len(G.nodes()), len(G.edges())
        print(N, M)
        
        # Setting parameters for SIR model
        gamma = 1.0  # recovery rate
        tmin, tmax = 0.0, 50.0
        report_times = np.linspace(tmin, tmax, 21)
        iterations = 20
        #iterations = 100
        beta = get_beta_c(G, N)
        print("beta_c: ", beta)

        SR = np.zeros((N, 2)) # standard ranking
        for node in G.nodes():
            SR[node, 1]  = simulate_sir_spreading(G, node, beta, gamma, tmax, report_times, iterations)
        
        SR[:,0] = np.array(list(G.nodes())) # The first column holds the node labels. Note that node labels range from 0 to N-1.
        #print("SIR results: ", SR)
        np.savetxt(f"./standard_ranking_iter{str(iterations)}/standard_ranking_iter{str(iterations)}_" + name + ".csv", SR, delimiter=',', fmt='%f')