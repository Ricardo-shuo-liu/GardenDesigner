from gardendesigner.agent import BaseAgent
import logging
import json
from typing import List,Tuple
class AttributeAgent(BaseAgent):
    def __init__(self, agent_name="attribute",
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
        pass

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
        dic = {}
        keys = ["attribute_exist",
                "attribute_region_num",
                "attribute_region_area",
                "attribute_region_single_area"]
        for key in keys:
            dic[key] = [-1 for _ in range(5)]

        # parse
        try:
            json_data = json.loads(text)
            data, fb = json_data["data"], json_data["feedback"]
            assert len(data) == 4
            lis = data[0]
            for i in range(5):
                assert lis[i] == 0 or lis[i] == 1 or lis[i] == -1
                dic["attribute_exist"][i] = lis[i]
            for j in range(1, 4):
                lis = data[j]
                assert len(lis) == 5
                for i in range(5):
                    assert len(lis[i]) == 2
                    assert lis[i][0] == -1 or lis[i][0] >= 0
                    assert lis[i][1] == -1 or lis[i][1] >= 0
                    if j == 1:
                        dic["attribute_region_num"][i] = lis[i]
                    elif j == 2:
                        dic["attribute_region_area"][i] = lis[i]
                    elif j == 3:
                        dic["attribute_region_single_area"][i] = lis[i]
            return dic, fb
        except Exception as e:
            print("parse exception:", e)
            return dic, "GPT response parsing error"
    def _algorithm(self):
        pass
    