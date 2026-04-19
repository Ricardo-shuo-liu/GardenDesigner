import abc
import json
import logging
from typing import Dict, Any, Optional,List
from pathlib import Path
from openai import OpenAI
from gardendesigner.config.prompt import Prompt


class BaseAgent(abc.ABC):
    def __init__(self,
                 agent_name: str,
                 llm_model: str = "gpt-4o",
                 llm_key:str|None = None,
                 llm_base_url:str|None = None,
                 llm_temperature: float = 0.1,
                 output_dir: str = "./logs",
                 log_level: int = logging.INFO,
                 ):
        # 设置类的参数
        self.agent_name = agent_name
        self.llm_model = llm_model
        self.llm_temperature = llm_temperature
        self.llm_key = llm_key
        self.llm_base_url = llm_base_url
        self.output_dir = Path(output_dir)

        # 调用初始化方法
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = self._init_logger(log_level)
        self.client = self._init_llm_client()
        self.base_messages: Optional[Dict[str, Any]] = self.loade_base_messages(prompt=Prompt)
        self.output_data: Optional[Dict[str, Any]] = None
        # 输入日志
        self.logger.info(f"{self.agent_name} 初始化完成")

    def _init_logger(self, log_level: int):
        """初始化日志记录器"""
        logger = logging.getLogger(self.agent_name)
        logger.setLevel(log_level)
        # 避免重复添加handler
        if not logger.handlers:

            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            # 文件handler
            log_file = self.output_dir / f"{self.agent_name}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(console_formatter)
            logger.addHandler(file_handler)
        
        return logger
    def form_sys_messages(self,
                          sys_prompt,
                          sample_inputs,
                          sample_outputs):
        sys_messages = [{"role": "system", "content": sys_prompt}]
        for i in range(len(sample_inputs)):
            sys_messages.append({"role": "user", "content": sample_inputs[i]})
            sys_messages.append({"role": "assistant", "content": sample_outputs[i]})
        return sys_messages
    def loade_base_messages(self,prompt:Prompt):
        """建立message用于client"""
        sys_prompt = getattr(prompt,f"{self.agent_name}_sys_prompt ")
        sample_inputs = [getattr(prompt,f"{self.agent_name}_sample_input{i}") for i in range(1,4)]
        sample_outputs = [getattr(prompt,f"{self.agent_name}_sample_output{i}") for i in range(1,4)]
        message = self.form_sys_messages(sys_prompt=sys_prompt,
                                         sample_inputs=sample_inputs,
                                         sample_outputs=sample_outputs)
        return message
    def _init_llm_client(self):
        """初始化LLM客户端"""
        client = OpenAI(
            api_key=self.llm_key,
            base_url=self.llm_base_url
        )
        return client
    
    @abc.abstractmethod
    def _call_llm(self):
        raise
    @abc.abstractmethod
    def _parse_llm_response(self):
        raise
    @abc.abstractmethod
    def _algorithm(self):
        raise
    @abc.abstractmethod
    def execute(self,user_promot):
        raise


class Pipeline(abc.ABC):

    def __init__(self,agents:List[BaseAgent]):
        super().__init__()
        if not agents:
            raise ValueError("agents列表不能为空")
        self.agents = agents
        self.pipeline_output: Optional[Dict[str, Any]] = None

    @abc.abstractmethod
    def run(self):
        raise