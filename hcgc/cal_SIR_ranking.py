#### Original source code: https://github.com/chend2023/identifying_important_nodes ####
from utils import *


if __name__ == '__main__':

    nums = 11
    gamma = 1.0  # recovery rate
    tmin, tmax = 0.0, 50.0
    iterations = 1000
    report_times = np.linspace(tmin, tmax, 21)

    root_folder = "public_data"
    folder_name = root_folder

    for name in network_names:
        if 'karate' in name.lower():
            G = nx.karate_club_graph()
        else:
            G = load_graph_data(folder_name=folder_name, name=name)
        N, M = len(G.nodes()), len(G.edges())
        print(N, M)


        # epidemic threshold: beta_c
        beta_c = get_beta_c(G, N)
        print("beta_c: ", beta_c)
        beta_list = np.linspace(0.5, 1.5, nums) * beta_c  # infection probability $\beta$

        # First normalize the weights
        # H = normalize_weights(G)

        SR = np.zeros((N, nums+1)) # SIR ranking
        for j, beta in enumerate(beta_list):
            for i in G.nodes():
                obs_R = 0 * report_times
                for counter in range(iterations):

                    # Assuming your graph G has edge weights stored in the 'weight' attribute
                    t, S, I, R = EoN.fast_SIR(
                        G, 
                        beta, 
                        gamma, 
                        initial_infecteds=i, 
                        tmax=tmax,
                        transmission_weight='weight'
                    )  # Use edge weights
                    obs_R += EoN.subsample(report_times, t, R)

                SR[i, j+1] = obs_R[-1] / iterations
        SR[:,0] = np.array(list(G.nodes())) # The first column holds the node labels. Note that node labels range from 0 to N-1.
        np.savetxt(f"./sir_ranking_results/sir_ranking_" + name + ".csv", SR, delimiter=',', fmt='%f')