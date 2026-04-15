# GardenDesigner

## 项目简介
本项目是对论文[GardenDesigner: Encoding Aesthetic Principles into Jiangnan Garden Construction via a Chain of Agents](https://arxiv.org/abs/2604.01777)的复现 


## 原始论文的部分相关链接  
[arXiv](https://arxiv.org/abs/2604.01777 "论文链接")  
[Github](https://github.com/Monad-Cube/Garden-Designer "原始代码")



## 项目与免责声明
    1.本项目代码与官方代码存在部分差异，请以官方代码为准。
    2.如本项目存在任何侵权行为，请通过我的个人主页联系我删除该项目。

## 致谢

感谢原论文所有作者的开源贡献，本项目仅用于学术学习与研究。

---
### 如何开始

1. **克隆仓库**

```bash
git clone <repository-url>
cd GardenDesigner
```

2. **创建虚拟环境**
```bash
# 创建python环境
conda create -n gardendesigner python=3.8.20
# 激活python环境
conda activate gardendesigner

# 注意这里推荐使用minconda来创建环境
# 当然你也可以选择uv或者其他方案 但是确保python的版本
```

3. **下载开发依赖**
```bash
pip install -e .
# 会下载pyproject.toml说明的相关依赖
```