from gardendesigner.agent import BaseAgent
import logging
import json
from typing import List,Tuple
class RoadGenErationAgent(BaseAgent):
    def __init__(self, agent_name="inf",
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
        # default parameters
        dic = {}
        keys = ["inf_entrance_num",
                "inf_keyunit_num",
                "inf_mainroad_width",
                "inf_road_complexity"]
        for key in keys:
            dic[key] = -1
        # parse
        try:
            json_data = json.loads(text)
            data, fb = json_data["data"], json_data["feedback"]
            assert len(data) == 4
            for i in range(4):
                lis = data[i]
                assert len(lis) == 2
                assert lis[0] == -1 or lis[0] >= 0
                assert lis[1] == -1 or lis[1] >= 0
                dic[keys[i]] = lis
            return dic, fb
        except Exception as e:
            print("parse exception:", e)
            return dic, "GPT response parsing error"
    