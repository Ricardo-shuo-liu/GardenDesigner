# 设置环境变量文件 读取环境变量数据 定义constant

import pathlib
from dotenv import load_dotenv
import os
from typing import Annotated

class EnvFiler():
    def __init__(self):
        # 获取用户的家目录
        self.config_dir = pathlib.Path.home() / ".gardendesigner"
        self.config_path = self.config_dir / ".env.local"

    def make(self,key,model=None,base_url=None):
        # 设置环境变量到指定位置
        self.config_dir.mkdir(exist_ok=True)
        content = []
        content.append("API_KEY="+key+"\n")
        if model:
            content.append("MODEL_NAME="+model+"\n")
        else:
            content.append("MODEL_NAME="+"gpt-4o"+"\n")
        if base_url:
            content.append("BASE_URL="+base_url+"\n")
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.writelines(content)

    def get_config_path(self):
        # 返回配置文件路径
        return self.config_path
    
class GetEnvParam():
    def __init__(self,config_path):
        # 初始化
        self.config_path = config_path
        load_dotenv(self.config_path)
    def get_key(self):
        # 获得API_KEY
        API_KEY = os.getenv(key="API_KEY")
        if API_KEY:
            return API_KEY
    def get_model_name(self):
        # 获得模型名称
        MODEL_NAME = os.getenv(key="MODEL_NAME")
        if MODEL_NAME:
            return MODEL_NAME
    def get_base_url(self):
        # 获得base_url
        BASE_URL = os.getenv(key="BASE_URL")
        if BASE_URL:
            return BASE_URL
class BaseParam():
    MAX_GENERATION:Annotated[int,"最多进化多少代"] = 100
    MUTATION_RATE:Annotated[float,"变异概率"]= 0.7
    CROSSOVER_RATE:Annotated[float,"杂交概率"] = 0.9
    POPULATION_SIZE:Annotated[int,"种群数量"] = 100
    def __init__(self, **kwargs):
        # 初始化
        for key, val in kwargs.items():
            if hasattr(self, key):
                if isinstance(val, type(getattr(self, key))):
                    setattr(self, key, val)
                else:
                    raise TypeError(f"Wrong type for {key} - {val}")
            else:
                raise ValueError(f"{key} is not configurable")

    def set(self, **kwargs) -> None:
        # 修改全局数据
        for key, val in kwargs.items():
            if hasattr(BaseParam, key):
                if isinstance(val, type(getattr(BaseParam, key))):
                    setattr(BaseParam, key, val)
                else:
                    raise TypeError(f"Wrong type for {key} - {val}")
            else:
                raise ValueError(f"{key} is not configurable")

    def overwrite(self, **kwargs) -> "BaseParam":
        # 临时启用数据
        ret = BaseParam(**kwargs)
        return ret