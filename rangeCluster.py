import pickle
from Definations import *
from queue import Queue
import math
import os
from tools import listReverse
from rmOutliers import rmOutliers
from tqdm import tqdm

# def dataloader(input_path):
#     seeds = []
#     with open(input_path, 'r') as f:
#         for line in f.readlines():
#             line = line.strip()
#             seeds.append(list(line))
#     return seeds

    
def Region_cluster(seeds, delta):
    root = Node(seeds)
    Leaves = set()
    DQ = Queue()
    DQ.put(root)

    while not DQ.empty():
        cur = DQ.get()
        if cur.size <= delta:
            Leaves.add(cur)
            continue
        children = Split(cur)
        for child in children:
            DQ.put(child)
    
    return list(Leaves)
        
def Split(node:Node):
    S = node.w
    RS = listReverse(S)
    children = set()

    free_dim = dict()
    for dim in range(32):
        entropy = Statistics.entropy(RS[dim])
        if entropy == 0: continue
        else:free_dim[dim] = entropy

    if len(free_dim)==0 : return []

    sorted_freedim = sorted(free_dim.items(), key = lambda x:x[1])
    min_entropy = sorted_freedim[0][1]

    for i in range(len(sorted_freedim)):
        if sorted_freedim[i][1] > min_entropy:break
        clusters = dict()
        dim = sorted_freedim[i][0]
        for addr in S:
            ch = addr[dim]
            if ch not in clusters: clusters[ch] = [addr]
            else:
                clusters[ch].append(addr)
        for key in clusters:
            children.add(Node(clusters[key]))

    return list(children)

def write_pattern(Leafs):
    with open("pk_data/patterns.txt", 'w') as f:
        for i in range(len(Leafs)):
            f.write("No.{} address pattern|size:{}\n".format(i,Leafs[i].size))
            f.write(Leafs[i].pattern+"\n")
            f.write("-"*32+"\n")
            for addr in Leafs[i].w:
                f.write("\""+addr+"\","+"\n")
            f.write("\n")

    with open("pk_data/nodes",'wb') as f:
        pickle.dump(Leafs,f)

if __name__ == "__main__":
    delta = 64

    # input_path = "seeds"
    # output_path = "patterns"
    # seeds = dataloader(input_path)
    # Leaves = Region_cluster(seeds, delta)
    # new_Leaves = []
    # for leaf in Leaves:
    #     leaf.w = ["".join(leaf.w[i]) for i in range(leaf.size())]
    
    # with tqdm(total=len(Leaves)) as pbar:
    #     for leaf in Leaves:
    #         if leaf.size()==1:
    #             pbar.update(1)
    #             continue
    #         new_Leaves.extend(rmOutliers(leaf,3))
    #         pbar.update(1)
    # write_pattern(output_path, Leaves)
    # write_pattern("patterns_rm",new_Leaves)

