from Definations import Node
from queue import Queue
from copy import deepcopy

def rmOutliers(node:Node, xi:int):
    """
    去除游离点(贪心策略剪枝, 找寻第一个聚合密度极值点, 从而保证聚合后区域密度更大)
    Args:
        node: 待去除游离点的区域节点
        xi: 若区域节点个数小于此值，则不进行去除操作
    Return:
        去除后的更高密度(相比未去除的)区域节点列表
    """
    if node.size <= xi:return []
    res = set()  #存储结果
    RQ = Queue()
    for addr in node.w:
        RQ.put(Node([addr]))

    while not RQ.empty():
        cur = RQ.get()
        max_node, max_density = group(cur, node.w, res)
        if max_density > cur.pdensity2():
            RQ.put(max_node)
        elif cur!=node:
            res.add(cur)
            # if max_density > node.density(): new_nodes.add(max_node)

    return list(res)
    
def group(node:Node, seeds, nodes:set):
    cur_addr = set(node.w)
    max_density = node.pdensity2()
    max_node = node
    for addr in seeds:
        if addr in cur_addr:continue
        new_node = deepcopy(node)
        new_node.addSeed(addr)
        if new_node in nodes: continue   #新加，减少树的规模，避免扩展重复节点
        if new_node.pdensity2() > max_density:
            max_density = new_node.pdensity2()
            max_node = new_node

    return max_node, max_density



if __name__ == "__main__":
    #6Graph的例子
    # "240e03690a663800021132fffea8d651",
    # "240e036910ee1400021132fffec9c076",
    # "240e03698c9b3400021132fffe6446e8",
    # "240e03990411ae010000000000000001",
    # "240e03993e1775010000000000000001",
    # "240e03690e581af0c0b47d364e1f0006",
    # "240e03994e04d9004e8120fffe3a30de",
    seeds = [
        "200119f0159514030000000000001096",
        "200119f0159514030000000000001101",
        "200119f0159514030000000000001088",
        "200119f0159514030000000000001082",
        "2a0101b0799904020000000000001007",
        "2a0101b0799904020000000000001150",
        "24062000009808020000000000001000",
    ]
    node = Node(seeds)
    # targetSet = set()
    # for item in node.genAddr(10,targetSet,"2001:16a2:c1ea::/47",True):
    #     print(item)
    # print(node.npdensity())
    # print(node.new_pattern)

    print(node.pattern,node.pdensity(),node.size)
    new_nodes = rmOutliers(node,3)
    for item in new_nodes:
        print(item.pattern, item.pdensity(),item.size)
    
    seeds = [
        "200119f0159514030000000000001096",
        "200119f0159514030000000000001101",
        "200119f0159514030000000000001088",
        "200119f0159514030000000000001082",
        "2a0101b0799904020000000000001007",
        "2a0101b0799904020000000000001150",
        "24062000009808020000000000001000",
    ]
    node = Node(seeds)
    print(node.pattern,node.pdensity2())