'''
DynWalks
STEP1: prepare data
STEP2: learn node embeddings
STEP3: downstream tasks evaluation

DynWalks hyper-parameters:
scheme=3,                             # the final version of DynWalks presented and tested in our paper
limit=0.1, local-global=0.5           # DynWalks key hyper-parameters
                                      # NOTE: limit i.e. $\alpha$, local_global i.e. $\beta$ in our paper
num_walks=20, walk_length=80,         # random walk hyper-parameters
window=10, negative=5,                # Skig-Gram hyper-parameters
seed=2019, workers=20,                # others

--------------------------------------------------------------------------------------
NB: You may ignore other static network embedding methods: DeepWalk, GraRep, HOPE.
    Our method DynWalks is independent from them.

    For other compared dynamic network embedding methods, please see:
    BCGD:        https://github.com/linhongseba/Temporal-Network-Embedding
    DynGEM:      https://github.com/palash1992/DynamicGEM
    DynTriad:    https://github.com/luckiezhou/DynamicTriad
--------------------------------------------------------------------------------------

by Chengbin Hou
'''

import warnings
warnings.filterwarnings("ignore")
# warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import time
import numpy as np
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import networkx as nx
from libne.utils import load_any_obj_pkl, save_any_obj_pkl


def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, conflict_handler='resolve')
    # -----------------------------------------------general settings--------------------------------------------------
    parser.add_argument('--graph', default='data/cora/cora_dyn_graphs.pkl',
                        help='graph/network')
    parser.add_argument('--label', default='data/cora/cora_node_label_dict.pkl',
                        help='node label')
    parser.add_argument('--emb-dim', default=128, type=int,
                        help='node embeddings dimensions')
    parser.add_argument('--task', default='all', choices=['lp', 'gr', 'nc', 'all', 'save'],
                        help='choices of downstream tasks: lp, gr, nc, all, save')
    parser.add_argument('--emb-file', default='output/cora_DynWalks_128_embs.pkl',
                        help='node embeddings; suggest: data_method_dim_embs.pkl')
    # -------------------------------------------------method settings-----------------------------------------------------------
    parser.add_argument('--method', default='DynWalks', choices=['DynWalks', 'DeepWalk', 'GraRep', 'HOPE'],
                        help='choices of Network Embedding methods')
    parser.add_argument('--limit', default=0.1, type=float,
                        help='the limit of nodes to be updated at each time step i.e. $\alpha$ in our paper')
    parser.add_argument('--local-global', default=0.5, type=float,
                        help='balancing factor for local changes and global topology; raning [0.0, 1.0] i.e. $\beta$ in our paper')
    parser.add_argument('--scheme', default=3, type=int,
                        help='scheme 1: new + most affected; scheme 2: new + random; scheme 3: new + most affected + random')
    # walk based methods
    parser.add_argument('--num-walks', default=20, type=int,
                        help='# of random walks of each node')
    parser.add_argument('--walk-length', default=80, type=int,
                        help='length of each random walk')
    # gensim word2vec parameters
    parser.add_argument('--window', default=10, type=int,
                        help='window size of SGNS model')
    parser.add_argument('--negative', default=5, type=int,
                        help='negative samples of SGNS model')
    parser.add_argument('--workers', default=24, type=int,
                        help='# of parallel processes.')
    parser.add_argument('--seed', default=2019, type=int,
                        help='random seed')
    # other methods
    parser.add_argument('--Kstep', default=4, type=int,
                        help='Kstep used in GraRep model, error if not emb_dim % Kstep == 0')
    args = parser.parse_args()
    return args


def main(args):
    # logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    print(f'Summary of all settings: {args}')

    # ----------------------------------------STEP1: prepare data-------------------------------------------------------
    print('\nSTEP1: start loading data......')
    t1 = time.time()
    G_dynamic = load_any_obj_pkl(args.graph)
    t2 = time.time()
    print(f'STEP1: end loading data; time cost: {(t2-t1):.2f}s')

    # -----------------------------------STEP2: upstream embedding task-------------------------------------------------
    print('\nSTEP2: start learning embeddings......')
    print(f'The model used: {args.method} -------------------- \
            \nThe # of dynamic graphs: {len(G_dynamic)}; \
            \nThe # of nodes @t_init: {nx.number_of_nodes(G_dynamic[0])}, and @t_last {nx.number_of_nodes(G_dynamic[-1])} \
            \nThe # of edges @t_init: {nx.number_of_edges(G_dynamic[0])}, and @t_last {nx.number_of_edges(G_dynamic[-1])}')
    t1 = time.time()
    model = None
    if args.method == 'DynWalks':
        from libne import DynWalks  
        model = DynWalks.DynWalks(G_dynamic=G_dynamic, limit=args.limit, local_global = args.local_global,
                                    num_walks=args.num_walks, walk_length=args.walk_length, window=args.window,
                                    emb_dim=args.emb_dim, negative=args.negative, workers=args.workers, seed=args.seed, scheme=args.scheme)
        model.sampling_traning()
    elif args.method == 'DeepWalk':
        from libne import DeepWalk 
        model = DeepWalk.DeepWalk(G_dynamic=G_dynamic, num_walks=args.num_walks, walk_length=args.walk_length, window=args.window,
                                    negative=args.negative, emb_dim=args.emb_dim, workers=args.workers, seed=args.seed)
        model.sampling_traning()
    elif args.method == 'GraRep':
        from libne import GraRep
        model = GraRep.GraRep(G_dynamic=G_dynamic, emb_dim=args.emb_dim, Kstep=args.Kstep)
        model.traning()
    elif args.method == 'HOPE':
        from libne import HOPE
        model = HOPE.HOPE(G_dynamic=G_dynamic, emb_dim=args.emb_dim)
        model.traning()
    else:
        print('method not found...')
        exit(0)
    t2 = time.time()
    print(f'STEP3: end learning embeddings; time cost: {(t2-t1):.2f}s')

    # ---------------------------------------STEP3: downstream task-----------------------------------------------
    print('\nSTEP3: start evaluating ......: ')
    t1 = time.time()
    emb_dicts = model.emb_dicts
    if args.task == 'save':
        save_any_obj_pkl(obj=emb_dicts, path=args.emb_file)
        print(f'Save node embeddings in file: {args.emb_file}')
        print(f'No downsateam task; exit... ')
    del model  # to save memory

    print(f'--- start link prediction task --> use current emb @t to predict **future** changed links @t+1 ...: ')
    if args.task == 'lp_changed' or args.task == 'all':   # for this task, we may need a big diff between two time steps --> more testing data --> more stable result
        from libne.downstream import lpClassifier, gen_test_edge_wrt_changes
        for t in range(len(emb_dicts)-1):
            print(f'Current time step @t: {t}')
            print(f'Changed Link Prediction task by AUC score')
            pos_edges_with_label, neg_edges_with_label = gen_test_edge_wrt_changes(G_dynamic[t],G_dynamic[t+1]) # use current emb @t predict topology @t+1
            test_edges = [e[:2] for e in pos_edges_with_label] + [e[:2] for e in neg_edges_with_label]
            test_label = [e[2] for e in pos_edges_with_label] + [e[2] for e in neg_edges_with_label]
            ds_task = lpClassifier(emb_dict=emb_dicts[t])  # use current emb @t
            ds_task.evaluate_auc(test_edges, test_label)
    
    print(f'--- start graph/link reconstraction task --> use current emb @t to reconstruct **current** graph @t...: ')
    if args.task == 'gr' or args.task == 'all':
        from libne.downstream import grClassifier, gen_test_node_wrt_changes
        for t in range(len(emb_dicts)-1):
            print(f'Current time step @t: {t}')
            ds_task = grClassifier(emb_dict=emb_dicts[t], rc_graph=G_dynamic[t]) # use current emb @t reconstruct graph t
            changed_nodes = gen_test_node_wrt_changes(G_dynamic[t],G_dynamic[t+1])                 # CGR testing nodes
            print('# of changed_nodes for testing: ', len(changed_nodes))  
            all_nodes = list(G_dynamic[t].nodes())
            random_nodes = list(np.random.choice(all_nodes, int(len(all_nodes)*0.25), replace=False))   # GR testing nodes
            print('# of random_nodes for testing: ', len(random_nodes))                                 
            # ------------------------- @10 ----------------------
            precision_at_k = 10
            print(f'Changed Graph Reconstruction by AP @{precision_at_k}')
            ds_task.evaluate_precision_k(top_k=precision_at_k, node_list=changed_nodes)             # CGR AP
            print(f'Graph Reconstruction by AP @{precision_at_k}')
            ds_task.evaluate_precision_k(top_k=precision_at_k, node_list=random_nodes)              # GR AP
            print(f'Changed Graph Reconstruction by MAP @{precision_at_k}')
            ds_task.evaluate_average_precision_k(top_k=precision_at_k, node_list=changed_nodes)     # CGR MAP
            print(f'Graph Reconstruction by MAP @{precision_at_k}')
            ds_task.evaluate_average_precision_k(top_k=precision_at_k, node_list=random_nodes)      # GR AMP
            # ------------------------- @100 ---------------------
            precision_at_k = 100
            print(f'Changed Graph Reconstruction by AP @{precision_at_k}')
            ds_task.evaluate_precision_k(top_k=precision_at_k, node_list=changed_nodes)             # CGR AP
            print(f'Graph Reconstruction by AP @{precision_at_k}')
            ds_task.evaluate_precision_k(top_k=precision_at_k, node_list=random_nodes)              # GR AP
            print(f'Changed Graph Reconstruction by MAP @{precision_at_k}')
            ds_task.evaluate_average_precision_k(top_k=precision_at_k, node_list=changed_nodes)     # CGR MAP
            print(f'Graph Reconstruction by MAP @{precision_at_k}')
            ds_task.evaluate_average_precision_k(top_k=precision_at_k, node_list=random_nodes)      # GR AMP
            # NOTE: if memory error, try grClassifier_batch (see dowmstream.py) which is slow but greatly reduce ROM

    t2 = time.time()
    print(f'STEP3: end evaluating; time cost: {(t2-t1):.2f}s')


if __name__ == '__main__':
    print(f'------ START @ {time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())} ------')
    main(parse_args())
    print(f'------ END @ {time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())} ------')
