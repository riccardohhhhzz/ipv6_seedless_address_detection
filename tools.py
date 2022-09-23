from copy import deepcopy
import math
import random
import re
import ipaddress
import pickle

def stdIPv6(addr:str):
    return ipaddress.ip_address(addr)

def listReverse(A):
    return list(map(list, zip(*A)))

def numConversion(a:list):
    baseMap = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15}
    result = []
    for item in a:
        result.append(baseMap[item])
    return result

def hex2ten(a:str):
    baseMap = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15}
    return baseMap[a]

def ten2hex(a:int):
    baseMap = {0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'a', 11:'b', 12:'c', 13:'d', 14:'e', 15:'f'}
    return baseMap[a]

def prefixlen(prefix:str):
    tmp = prefix.split('/')
    prefixLen = int(tmp[1])
    return prefixLen

def getStdprefix(prefix:str):
    tmp = prefix.split('/')
    prefixLen = int(tmp[1])
    prefix = tmp[0]
    a = prefix.split(':')
    for i in range(len(a)):
        if len(a[i])==4 :continue
        if len(a[i]) < 4 and len(a[i])>0:
            zero = "0"*(4 - len(a[i]))
            a[i] = zero + a[i]
        if len(a[i])==0 and i!=len(a)-1:  #中间补零
            a[i] = math.ceil((prefixLen - (len(a)-1)*16)/4)*'0'
    a = "".join(a)
    nyble_prefixLen = math.ceil(prefixLen/4)
    if len(a) < nyble_prefixLen: #末尾补零
        a = a+ (nyble_prefixLen-len(a))*'0'
    if len(a) > nyble_prefixLen: #末尾去零
        a = a[:nyble_prefixLen]
    if prefixLen%4==0: return a
    else:
        num = int(prefixLen / 4)
        left = prefixLen % 4 
        a = a[:num]+"[{},{}]".format(a[num],ten2hex(hex2ten(a[num])+int(math.pow(2,4-left))-1))

    return a

def genList(a:str, b:str):
    """
    生成十六进制字符a到b的连续列表
    """
    res = []
    for i in range(hex2ten(a),hex2ten(b)+1):
        res.append(ten2hex(i))
    return res

def str2ipv6(a:str):
    """
    IPv6地址加冒号变成标准IPv6地址
    """
    pattern = re.compile('.{4}')
    addr = ':'.join(pattern.findall(a))
    return str(stdIPv6(addr))

def gentotalPattern(prefix):
    stdPrefix = getStdprefix(prefix)
    pattern = ""
    pattern += stdPrefix
    pattern += int((128-prefixlen(prefix))/4)*'*' 
    return pattern

def spaceNum(pattern):
    margin = 0
    if '[' in pattern:
        li_l = pattern.index('[')
        li_r = pattern.index(']')
        li = genList(pattern[li_l+1],pattern[li_r-1])
        margin = int(math.pow(16,pattern.count('*')))*len(li)
    else:
        margin = int(math.pow(16,pattern.count('*')))
    return margin

def genAddrByPattern(pattern:str, start, num):
    """
    按照模式顺序生成地址
    Args:
        pattern:  地址模式
        start: 之前该模式生成了多少数量
        num: 此次生成的最大数量,等于min(margin,budget)
    Return:
        target: 目标地址集合
    """
    target = set()
    if '[' in pattern:
        li_l = pattern.index('[')
        li_r = pattern.index(']')
        li = genList(pattern[li_l+1],pattern[li_r-1])
        freeNum = pattern.count('*') + 1
        for i in range(start,num+start):
            Hex = (freeNum - len(hex(i)[2:]))*'0' + hex(i)[2:]
            tmp = deepcopy(pattern)
            addr = tmp[:li_l] + li[int(Hex[0])]
            for ch in Hex[1:]:
                tmp = tmp.replace('*',ch,1)
            addr += tmp[li_r+1:]
            addr = str2ipv6(addr)
            target.add(addr)
    else:
        freeNum = pattern.count('*')
        for i in range(start,num+start):
            Hex = (freeNum - len(hex(i)[2:]))*'0' + hex(i)[2:]
            tmp = deepcopy(pattern)
            for ch in Hex:
                tmp = tmp.replace('*',ch,1)
            target.add(str2ipv6(tmp))
    return target
