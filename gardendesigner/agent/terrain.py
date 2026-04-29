from gardendesigner.agent import BaseAgent
import logging
import json
from typing import List,Tuple,Callable
class TerrainGenerationAgent(BaseAgent):
    def __init__(self, agent_name="terrain",
                 llm_model = "gpt-4o",
                 llm_key = None,
                 llm_base_url = None,
                 llm_temperature = 0.1,
                 output_dir = "./logs",
                 log_level = logging.INFO):
        super().__init__(agent_name,
                         llm_model,
                         llm_key,
                         llm_base_url,
                         llm_temperature,
                         output_dir,
                         log_level)
        # 调用父类初始化
    def _call_llm(self,
                  system_messages: List[dict], 
                  text: str) -> str:
        """与智能体对话"""
        message = self.load_text(system_messages=system_messages,text=text)
        try:
            chat_completion = self.client.chat.completions.create(
                model=self.llm_model,
                messages=message,
            )
            res = chat_completion.choices[0].message.content
            return res
        except Exception as e:
            print("gpt exception", e)
            return ""
    def load_text(self,system_messages: List[dict], 
                  text: str) -> List[dict]:
        """加入新的文本内容"""
        messages = system_messages
        messages.append({"role": "user", "content": text})

        return messages
    def _parse_llm_response(self,
                            text:str) -> Tuple[dict, str]:
        """数据提取"""
        # default parameters
        dic = {}
        keys = ["terrain_exist",
                "terrain_region_num",
                "terrain_region_area",
                "terrain_region_single_area"]
       # terrain_exist	5 类地形是否存在
       # terrain_region_num	每类地形区域数量上下限
       # terrain_region_area	每类地形总占地比例上下限
       # terrain_region_single_area	每类地形单个地块比例上下限
       # max_hill_height	高地最大高度
       # 0: Unused（未使用）1: Aquatic（水域）2: Terrestrial（陆地）3: Artificial（人工 / 建筑）4: Elevated（高地）
        for key in keys:
            dic[key] = [-1 for _ in range(5)]
        dic["max_hill_height"] = -1

        # parse
        try:
            json_data = json.loads(text)
            data, fb = json_data["data"], json_data["feedback"]
            assert len(data) == 5
            lis = data[0]
            assert len(lis) == 5
            for i in range(5):
                assert lis[i] == 0 or lis[i] == 1 or lis[i] == -1
                dic["terrain_exist"][i] = lis[i]
            for j in range(1, 4):
                lis = data[j]
                assert len(lis) == 5
                for i in range(5):
                    assert len(lis[i]) == 2
                    assert lis[i][0] == -1 or lis[i][0] >= 0
                    assert lis[i][1] == -1 or lis[i][1] >= 0
                    if j == 1:
                        dic["terrain_region_num"][i] = lis[i]
                    elif j == 2:
                        dic["terrain_region_area"][i] = lis[i]
                    elif j == 3:
                        dic["terrain_region_single_area"][i] = lis[i]
            assert data[4] == -1 or data[4] > 0
            dic["max_hill_height"] = data[4]

            return dic, fb
        except Exception as e:
            print("parse exception:", e)
            return dic, "GPT response parsing error"
    def _algorithm(self,
                   args,
                   parameters: dict) -> List[List[int]]:
        """遗传算法生成地形"""
        from gardendesigner.algorithm.genetic import GeneticAlgorithm
        genetic_algorithm = GeneticAlgorithm()
        genetic_algorithm.excute(
            args=args,
            parameters=parameters
        )
        # 调用算法