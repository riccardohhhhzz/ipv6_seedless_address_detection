"""
评测指标:

1.总体上的：
    1.有活跃地址的BGP数量
    2.探测到的活跃地址总量
    3.平均的活跃地址命中率
    4.单位时间发现活跃地址的数量

2.分布上的：
    1.前缀活跃地址数量分布(直方图)
    2.前缀探测命中率分布(直方图)


数据表示:
{
    "2600:8807:bb4::/47": {
        "target":xxx,
        "active":xxx,
        "hitrate":xxx,
        "duration":xxx,
    }
}
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import mlab
from matplotlib import rcParams

def dataloader(path):
    data = dict()
    with open(path,'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].strip()
            if lines[i] == "": continue
            if lines[i].startswith('#'):
                prefix = lines[i].split(',')[0][1:]
                content = lines[i+1].strip().split(',')
                target = int(content[0].split(':')[1])
                active = int(content[1].split(':')[1])
                hitrate = float(content[2].split(':')[1])
                duration = float(content[3].split(':')[1])
                data[prefix] = dict()
                data[prefix]['target'] = target
                data[prefix]['active'] = active
                data[prefix]['hitrate'] = hitrate
                data[prefix]['duration'] = duration
    return data

def active_BGP_num(data):
    active_num = 0
    for bgp in data:
        if data[bgp]['active'] > 0 : active_num+=1
    return active_num

def active_addr_num(data):
    active_num = 0
    for bgp in data:
        active_num += data[bgp]['active']
    return active_num

def avg_hitrate(data):
    target_num = 0
    active_num = 0
    for bgp in data:
        target_num += data[bgp]['target']
        active_num += data[bgp]['active']
    return active_num / target_num

def total_time(data):
    time = 0
    for bgp in data:
        time += data[bgp]['duration']
    return time

def get_active_num(data):
    sample_active_num = []
    active_num_dist = dict()
    for bgp in data:
        sample_active_num.append(data[bgp]['active'])
    # samples = list(range(1,1001))
    active_num_dist['(0,1e2]'] = 0
    active_num_dist['(1e2,1e3]'] = 0
    active_num_dist['(1e3,1e4]'] = 0
    active_num_dist['(1e4,1e5]'] = 0
    active_num_dist['(1e5,1e6]'] = 0
    active_num_dist['(1e6,5e6]'] = 0
    for num in sample_active_num:
        if num>0 and num <=100 : active_num_dist['(0,1e2]'] += 1
        if num>100 and num <=1000 : active_num_dist['(1e2,1e3]'] += 1
        if num>1000 and num <=10000 : active_num_dist['(1e3,1e4]'] += 1
        if num>10000 and num <=100000 : active_num_dist['(1e4,1e5]'] += 1
        if num>100000 and num <=1000000 : active_num_dist['(1e5,1e6]'] += 1
        if num>1000000 and num <=5000000 : active_num_dist['(1e6,5e6]'] += 1

    x_groups = list(active_num_dist.keys())
    y_groups = [active_num_dist[x_groups[i]] for i in range(len(x_groups))]
    return x_groups, y_groups

def plot_active_num(DHC,Addr):
    DHC_x_groups, DHC_y_groups = get_active_num(DHC)
    Addr_x_groups, Addr_y_groups = get_active_num(Addr)
    
    bar_width = 0.2

    bar_1 = list(range(len(DHC_x_groups)))
    bar_2 = [i+bar_width for i in bar_1]
    mid = [(bar_1[i]+bar_2[i])/2 for i in range(len(bar_1))]

    #设置图片尺寸与清晰度
    plt.figure(figsize=(12, 8), dpi=600)

    #导入数据，绘制条形图
    plt.bar(bar_1, DHC_y_groups, width=bar_width, label='DHC')
    plt.bar(bar_2, Addr_y_groups, width=bar_width, label='AddrMiner')

    for a,b in zip(bar_1, DHC_y_groups):
        plt.text(a, b+1, b, ha='center', va='bottom')
    for a,b in zip(bar_2, Addr_y_groups):
        plt.text(a, b+1, b, ha='center', va='bottom')
    #添加标题
    plt.title('Distribution of the number of active addresses', size=12)
    #添加xy轴
    plt.xlabel('Number of active addresses',size=10)
    plt.ylabel('Number of BGP prefixes',size=10)
    #x轴刻度
    plt.xticks(mid, DHC_x_groups)
    plt.legend()

    #保存结果
    plt.savefig("active_num.jpg")


def get_hitrate(data):
    sample_hitrate = []
    hitrate_dist = dict()
    for bgp in data:
        sample_hitrate.append(data[bgp]['hitrate'])
    # samples = list(range(1,1001))
    hitrate_dist['(0,0.5%]'] = 0
    hitrate_dist['(0.5%,5%]'] = 0
    hitrate_dist['(5%,20%]'] = 0
    hitrate_dist['(20%,50%]'] = 0
    hitrate_dist['(50%,80%]'] = 0
    hitrate_dist['(80%,90%]'] = 0
    hitrate_dist['(90%,95%]'] = 0
    hitrate_dist['(95%,100%]'] = 0
    for num in sample_hitrate:
        if num>0 and num <=0.5*(1e-2) : hitrate_dist['(0,0.5%]'] += 1
        if num>0.5*(1e-2) and num <=5*(1e-2) : hitrate_dist['(0.5%,5%]'] += 1
        if num>5*(1e-2) and num <=20*(1e-2) : hitrate_dist['(5%,20%]'] += 1
        if num>20*(1e-2) and num <=50*(1e-2) : hitrate_dist['(20%,50%]'] += 1
        if num>50*(1e-2) and num <=80*(1e-2) : hitrate_dist['(50%,80%]'] += 1
        if num>80*(1e-2) and num <=90*(1e-2) : hitrate_dist['(80%,90%]'] += 1
        if num>90*(1e-2) and num <=95*(1e-2) : hitrate_dist['(90%,95%]'] += 1
        if num>95*(1e-2) and num <=1 : hitrate_dist['(95%,100%]'] += 1

    
    x_groups = list(hitrate_dist.keys())
    y_groups = [hitrate_dist[x_groups[i]] for i in range(len(x_groups))]

    return x_groups, y_groups

def plot_hitrate(DHC,Addr):
    DHC_x_groups, DHC_y_groups = get_hitrate(DHC)
    Addr_x_groups, Addr_y_groups = get_hitrate(Addr)
    
    bar_width = 0.2

    bar_1 = list(range(len(DHC_x_groups)))
    bar_2 = [i+bar_width for i in bar_1]
    mid = [(bar_1[i]+bar_2[i])/2 for i in range(len(bar_1))]

    #设置图片尺寸与清晰度
    plt.figure(figsize=(12, 8), dpi=600)

    #导入数据，绘制条形图
    plt.bar(bar_1, DHC_y_groups, width=bar_width, label='DHC')
    plt.bar(bar_2, Addr_y_groups, width=bar_width, label='AddrMiner')

    for a,b in zip(bar_1, DHC_y_groups):
        plt.text(a, b+1, b, ha='center', va='bottom')
    for a,b in zip(bar_2, Addr_y_groups):
        plt.text(a, b+1, b, ha='center', va='bottom')
    #添加标题
    plt.title('Distribution of hitrate', size=12)
    #添加xy轴
    plt.xlabel('Hitrate',size=10)
    plt.ylabel('Number of BGP prefixes',size=10)
    #x轴刻度
    plt.xticks(mid, DHC_x_groups)
    plt.legend()

    #保存结果
    plt.savefig('hitrate.jpg')


if __name__ == "__main__":
    DHC_data =  dataloader('DHC_epoch10budget5000000.log')
    Addr_data = dataloader('Addr_epoch10budget5000000.log')

    #有活跃地址的BGP数量
    print("--有活跃地址的BGP数量--")
    DHC_active_BGP_num = active_BGP_num(DHC_data)
    Addr_active_BGP_num = active_BGP_num(Addr_data)
    print("DHC-FIFO:",DHC_active_BGP_num)
    print("AddrsMiner:",Addr_active_BGP_num)

    #探测到的活跃地址总量
    print("--探测到的活跃地址总量--")
    DHC_active_addr_num = active_addr_num(DHC_data)
    Addr_active_addr_num = active_addr_num(Addr_data)
    print("DHC-FIFO:",DHC_active_addr_num)
    print("AddrsMiner:",Addr_active_addr_num)

    #平均的活跃地址命中率
    print("--平均的活跃地址命中率--")
    DHC_avg_hitrate = avg_hitrate(DHC_data)
    Addr_avg_hitrate = avg_hitrate(Addr_data)
    print("DHC-FIFO:",DHC_avg_hitrate)
    print("AddrsMiner:",Addr_avg_hitrate)

    #单位时间发现活跃地址数量
    print("--单位时间发现活跃地址数量--")
    DHC_speed = DHC_active_addr_num / total_time(DHC_data)
    Addr_speed = Addr_active_addr_num / total_time(Addr_data)
    print("DHC-FIFO:",DHC_speed)
    print("AddrsMiner:",Addr_speed)

    #前缀活跃地址数量分布(直方图)
    plot_active_num(DHC_data,Addr_data)

    #前缀探测命中率分布(直方图)
    plot_hitrate(DHC_data,Addr_data)

