# ipv6_seedless_address_detection

##	安装依赖

* python 3.9.7

* tqdm
* subprocess
* pyasn
* pickle

## 文件说明

### 数据集

由于数据集太大，无法上传至git，仅上传了一些批量样本，可以从服务器端下载数据集

### 功能入口

* `aliasPrefixDetection.py`

  别名前缀检测

* `convert.py`

  ip地址标准化

* `Definations.py`

  模式节点抽象模型

* `DynamicScan.py`

  主入口，包括预扫描、动态扫描

* `partition.py`

  将所有BGP划分为三类，其中BGP-N表示无种子地址前缀

* `rangeCluster.py`

  区域聚合算法

* `rmOutliers.py`

  去除游离点算法

* `tools.py`

  一些会用到的功能函数

