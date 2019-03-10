"""
Format	Undirected: Edges are undirected Undirected
Edge weights	Unweighted: Simple edges Unweighted
Metadata	Timestamps:  Edges are annotated with a timestamps TimestampsIncomplete:   not all edges or nodes from the original dataset are included Incomplete
Size	63,731 vertices (users)
Volume	817,035 edges (friendships)
Average degree	25.640 edges / vertex

Data source	http://socialnetworks.mpi-sws.org/data-wosn2009.html

We equally divide it into 100 time steps and then choose the last 15 time steps

@ graph 0 # of nodes 59102 # of edges 702760
@ graph 1 # of nodes 59363 # of edges 710385
@ graph 2 # of nodes 59585 # of edges 717906
@ graph 3 # of nodes 59860 # of edges 725955
@ graph 4 # of nodes 60163 # of edges 734712
@ graph 5 # of nodes 60446 # of edges 743118
@ graph 6 # of nodes 60765 # of edges 751408
@ graph 7 # of nodes 61185 # of edges 761767
@ graph 8 # of nodes 61569 # of edges 771521
@ graph 9 # of nodes 62025 # of edges 781482
@ graph 10 # of nodes 62449 # of edges 792530
@ graph 11 # of nodes 62978 # of edges 803719
@ graph 12 # of nodes 63550 # of edges 814306
@ graph 13 # of nodes 63731 # of edges 817031
@ graph 14 # of nodes 63731 # of edges 817035

"""

import numpy as np
import networkx as nx
import pickle


def read_txt_file():
    #read the txt file
    lines = np.genfromtxt("out.facebook-wosn-links.txt", dtype= int)
    return lines

def save_nx_graph(nx_graph, path='nx_graph_temp.data'):
    with open(path, 'wb') as f:
        pickle.dump(nx_graph, f, protocol=pickle.HIGHEST_PROTOCOL)  # the higher protocol, the smaller file
    with open(path, 'rb') as f:
        nx_graph_reload = pickle.load(f)

    try:
        print('Check if it is correctly dumped and loaded: ', nx_graph_reload.edges() == nx_graph.edges(),
              ' It contains only ONE graph')
    except:
        for i in range(len(nx_graph)):
            print('Check if it is correctly dumped and loaded: ', nx_graph_reload[i].edges() == nx_graph[i].edges(),
                  ' for Graph ', i)

def generate_dynamic_graph(time_step_number = 100):
    lines = read_txt_file()
    """
    min_mum_non_zero_time = 1232231923
    max_mum_time = 0
    for i in range(len(lines)):
        time_tag = lines[i][3]
        if time_tag > 0:
            if time_tag < min_mum_non_zero_time:
                min_mum_non_zero_time = time_tag
            if time_tag > max_mum_time:
                max_mum_time = time_tag

    print(min_mum_non_zero_time)
    print(max_mum_time)
    """
    min_time = float(1157454929)
    max_time = float(1232231923)
    diff = (max_time - min_time)/float(time_step_number)
    time_slot = []

    for i in range(time_step_number-1):
        time_slot.append(min_time + diff*(1+i))
    time_slot.append(max_time+1)
    print(time_slot)
    graphs = []
    for i in range(time_step_number):
        graphs.append(nx.Graph())

    for i in range(len(lines)):
        time_tag = lines[i][3]
        showed_up_time_slot = 0
        for j in range(len(time_slot)):
            if time_tag < time_slot[j]:
                showed_up_time_slot = j
                break
        for j in range(showed_up_time_slot, len(graphs)):
            graphs[j].add_edge(str(lines[i][0]),str(lines[i][1]))

    for i in range(len(graphs)):
        print(len(graphs[i].edges), " graph:",i)
        print(len(graphs[i].nodes), " nodes:",i)

    return graphs






if __name__ == '__main__':

    graphs = generate_dynamic_graph()
    save_nx_graph(nx_graph=graphs[-15:], path='facebook_dynamic_graphs.data')

    graphs = graphs[-15:]
    for i in range(len(graphs)):
        print('@ graph', i, '# of nodes', len(graphs[i].nodes()), '# of edges', len(graphs[i].edges()))