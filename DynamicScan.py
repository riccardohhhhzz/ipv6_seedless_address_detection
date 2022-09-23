from select import select
import time
import subprocess
import heapq
import os
from rangeCluster import *
from convert import convert
from tools import gentotalPattern, prefixlen, spaceNum
def writeFile(target:list, active:list, targetfile, activefile):
    """
    将每一次批量探测到的结果实时记录到文件中
    Args:
        target: 目标地址集
        active: 活跃地址集
    """
    with open(targetfile,'a+') as f:
        for addr in target:
            f.write(addr+'\n')
    
    with open(activefile,'a+') as f:
        for addr in active:
            f.write(addr+'\n')

def Scan(addr_set, source_ip, output_file, tid):
    """
    运用扫描工具检测addr_set地址集中的活跃地址

    Args:
        addr_set:待扫描的地址集合
        source_ip
        output_file
        tid:扫描的线程id

    Return:
        active_addrs:活跃地址集合
    """

    scan_input = output_file + '/zmap/scan_input_{}.txt'.format(tid)
    scan_output = output_file + '/zmap/scan_output_{}.txt'.format(tid)

    with open(scan_input, 'w', encoding = 'utf-8') as f:
        for addr in addr_set:
            f.write(addr + '\n')

    active_addrs = set()
    command = 'sudo zmap --ipv6-source-ip={} --ipv6-target-file={} -M icmp6_echoscan -p 80 -q -o {}'\
    .format(source_ip, scan_input, scan_output)
    print('[+]Scanning {} addresses...'.format(len(addr_set)))
    t_start = time.time()
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # ret = p.poll()
    while p.poll() == None:
        pass

    if p.poll() is 0:
        # with open(output_file, 'a', encoding='utf-8') as f:
        # time.sleep(1)
        for line in open(scan_output):
            if line != '':
                active_addrs.add(line[0:len(line) - 1])
                    # f.write(line)
            
    print('[+]Over! Scanning duration:{} s'.format(time.time() - t_start))
    print('[+]{} active addresses detected!'
        .format(len(active_addrs)))
    return active_addrs

#小批量探测是不可行的，耗费时间
#先进行生成，将每个节点的cache合并为一个target，探测出总的active，再去更新hitrate
def preScan(nodes, ipv6, preScan_num, miniBudget=1,targetfile='',activefile=''):
    """
    预探测(将前缀进行替换, 按照命中率初步进行排序)
    Args:
        nodes: 模式节点列表
        ipv6: 本机IPv6地址
        miniBudget: 每个模式生成的地址个数
    Return:
        nodes_heapq: 模式节点优先级队列
        target: 已探测过的目标地址集合
        pre_target_num: 预扫描的目标地址数量
        pre_active_num : 预扫描得到的活跃地址数量
    """
    nodes_heapq = []
    target = []  #已探测过的目标地址集合
    #生成地址
    print('[+]Generate addresses..')
    random.shuffle(nodes)
    with tqdm(total=preScan_num) as pbar:
        for node in nodes[:preScan_num]:
            cache = node.genAddr(miniBudget,True)
            target.extend(list(cache))
            pbar.update(1)
    
    for node in nodes[preScan_num:]:
        node.genAddr(0,True)
    
    #探测
    active = Scan(set(target),ipv6,'./',0)
    #更新hitrate
    for node in nodes:
        if node.margin > 0:
            cache_size = len(node.cache)
            if cache_size==0: node.hitrate = 0
            else: 
                tmp = active.intersection(node.cache)
                node.active_num += len(tmp)
                node.hitrate = len(tmp) / cache_size
            heapq.heappush(nodes_heapq,node)
    #写入结果
    writeFile(list(target),list(active),targetfile,activefile)
    return nodes_heapq, len(target), len(active)

def preprocess(nodes:list, prefix:str):
    """
    数据清洗，删除掉替换前缀后相同模式的节点
    Args:
        nodes: 地址模式节点
        prefix: 替换的地址前缀
    Return:
        new_nodes: 替换后的地址模式节点
    """
    for node in nodes:
        node.prefixReplace(prefix)
    new_nodes = set()
    for node in nodes:
        new_nodes.add(node)
    return list(new_nodes)


def scan_feedback2(nodes, ipv6:str, batch_size=100000,epoch=10,targetfile='',activefile=''):
    """
    反馈式扫描
    每次选取rank靠前的节点生成地址, 直至耗尽预算, 剔除掉余量为0的节点, 计算hitrate, 重新排序
    Args:
        nodes: 地址模式节点
        ipv6: 本机IPv6地址
        batch_size: 每一轮次分配的预算大小
        epoch: 扫描轮数
    Return:
        target_num: 探测的地址总量
        active_num: 发现的活跃地址总量
    """
    active_num = 0
    target_num = 0
    for i in range(epoch):
        target = []
        select_num = 0  #本轮有多少节点参与生成
        batch_size_copy = batch_size
        #生成目标地址
        print('epoch={}, Generate addresses..'.format(i+1))
        print('the number of nodes:',len(nodes))
        with tqdm(total=batch_size) as pbar:
            for node in nodes:
                cache = node.genAddr(batch_size_copy,prescan=False)
                batch_size_copy -= len(cache)
                target.extend(list(cache))
                select_num += 1
                pbar.update(len(cache))
                if batch_size_copy<=0 : break
        #探测
        active = Scan(set(target),ipv6,'./',0)
        active_num += len(active)
        target_num += len(target)
        #更新hitrate
        for i in range(select_num):
            node = heapq.heappop(nodes)
            cache_size = len(node.cache)
            if cache_size > 0: 
                tmp = active.intersection(node.cache)
                node.active_num += len(tmp)
                node.hitrate = node.active_num / len(node.target)
            if node.margin > 0: heapq.heappush(nodes,node)
        #写入结果
        writeFile(list(target),list(active),targetfile,activefile)
    
    return target_num, active_num

def scan_feedback(nodes, p, prefix, targetSet:set, ipv6, batch_size=100000, epoch=30):
    """
    反馈式扫描
    每次选取一定数量的节点生成地址,并剔除掉余量为0的节点,计算hitrate,重新排序
    Args:
        nodes: 地址模式节点
        p: 每次选取前p%个节点进行生成
        prefix: 无种子地址BGP前缀
        targetSet: 总的目标地址集合
        ipv6: 本机IPv6地址
        batch_size: 每一轮次分配的预算大小
        epoch: 扫描轮数
    Return:
        target_num: 探测的地址总量
        active_num: 发现的活跃地址总量
    """
    active_num = 0
    for i in range(epoch):
        select_num, miniBudgets = preprocess(nodes,p,batch_size)
        target = set()
        #生成目标地址
        print('epoch={}, Generate addresses..'.format(i+1))
        with tqdm(total=select_num) as pbar:
            for i in range(select_num):
                target = target | nodes[i].genAddr(miniBudgets[i],targetSet,prefix,replace=False) #不需要替换
                pbar.update(1)
        #探测
        active = Scan(target,ipv6,'./',0)
        active_num += len(active)
        #更新hitrate
        for i in range(select_num):
            node = heapq.heappop(nodes)
            cache_size = len(node.cache)
            if cache_size > 0: 
                tmp = active.intersection(node.cache)
                node.active_num += len(tmp)
                node.hitrate = node.active_num / len(node.target)
            heapq.heappush(nodes,node)
        #写入结果
        writeFile(list(target),list(active))
    
    target_num = len(targetSet)

    return target_num, active_num

if __name__ == "__main__":
    input_path = "data/seeds.txt"
    ipv6 = "2001:da8:ff:212::10:3"
    budget = 500000
    miniBudget = 2
    preScan_num = int(0.1*budget)
    epoch = 10
    delta = 64
    p = 0.3
    prefixs = []
    activefile = 'result/active_epoch{}budget{}.txt'.format(epoch,budget)
    targetfile = 'result/target_epoch{}budget{}.txt'.format(epoch,budget)
    logfile = 'result/epoch{}budget{}.log'.format(epoch,budget)
    with open('data/BGP.txt','r') as f:
        for line in f.readlines():
            prefixs.append(line.strip())
    # #将ipv6地址转换为需要的格式，例如2a0206b80c0401a80000060490942804
    # seeds = convert(input_path)
    # #区域聚合，挖掘高密度区域
    # print('Region Cluster..')
    # Leaves = Region_cluster(seeds, delta)
    # for leaf in Leaves:
    #     leaf.w = ["".join(leaf.w[i]) for i in range(leaf.size)]
    
    # #去除游离点，形成更高密度区域
    # new_Leaves = []
    # with tqdm(total=len(Leaves)) as pbar:
    #     for leaf in Leaves:
    #         if leaf.size==1:
    #             pbar.update(1)
    #             continue
    #         new_Leaves.extend(rmOutliers(leaf,3))
    #         pbar.update(1)
    # write_pattern(new_Leaves)
    with open('pk_data/nodes','rb') as f:
        new_Leaves = pickle.load(f)
    #预探测：前缀替换，按照命中率排序返回一个优先级队列
    if os.path.exists(activefile): os.remove(activefile)
    if os.path.exists(targetfile): os.remove(targetfile)
    if os.path.exists(logfile): os.remove(logfile)
    for prefix in prefixs:
        start = time.time()
        print('BGP prefix:{}'.format(prefix))
        totalpattern = gentotalPattern(prefix)
        if totalpattern.count('*') < 4:
            target = genAddrByPattern(totalpattern,0,spaceNum(totalpattern))
            active = Scan(target,ipv6,'./',1)
            end = time.time()
            with open(logfile,'a+') as f:
                f.write("\n#{},budget:{}\n".format(prefix,budget))
                f.write('target:{},active:{},hitrate:{},duration:{}\n'.format(len(target),len(active),len(active)/len(target),end-start))
        else:
            new_nodes = preprocess(new_Leaves,prefix)
            print(len(new_nodes))
            batchsize = int((budget-preScan_num*miniBudget) / epoch)
            nodes_heapq, pre_target_num, pre_active_num = preScan(new_nodes,ipv6, preScan_num = preScan_num, miniBudget=miniBudget,activefile=activefile,targetfile=targetfile)
            # with open('pk_data/nodes_heapq','wb') as f:
            #     pickle.dump(nodes_heapq,f)
            # with open('pk_data/nodes_heapq','rb') as f:
            #     nodes_heapq = pickle.load(f)
            target_num, active_num = scan_feedback2(nodes_heapq,ipv6,batch_size=batchsize,epoch=epoch,targetfile=targetfile,activefile=activefile)
            hitrate = (active_num+pre_active_num) / (target_num+pre_target_num)
            end = time.time()
            with open(logfile,'a+') as f:
                f.write("\n#{},budget:{}\n".format(prefix,budget))
                f.write('target:{},active:{},hitrate:{},duration:{}\n'.format(target_num+pre_target_num,active_num+pre_active_num,hitrate,end-start))
            print(nodes_heapq[0].new_pattern, nodes_heapq[0].hitrate)
