"""
别名前缀检测
"""
from tqdm import tqdm
from tools import getStdprefix, gentotalPattern, genAddrByPattern, spaceNum
import time
import subprocess

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

bgp_n = {}
gen_num = 128
selected_bgp = []
total_target = []

# 获取前缀
with open('BGP/BGP-N','r') as f:
    for line in f.readlines():
        line = line.strip()
        bgp_n[line] = set()

# 生成地址
with tqdm(total=len(bgp_n)) as pbar:
    for bgp in bgp_n:
        pattern = gentotalPattern(bgp)
        spacenum = spaceNum(pattern)
        target_num = min(spacenum,gen_num)
        bgp_n[bgp] = genAddrByPattern(pattern,0,target_num)
        total_target.extend(list(bgp_n[bgp]))
        pbar.update(1)
        
# 扫描地址将结果匹配
active = Scan(set(total_target),"2001:da8:ff:212::10:3",'./',0)
for bgp in bgp_n:
    if len(bgp_n[bgp] & active) / gen_num < 0.9:
        selected_bgp.append(bgp)


with open('BGP/BGP-N-removeAliasPrefix','w') as f:
    for bgp in selected_bgp:
        f.write(bgp)
        f.write('\n')