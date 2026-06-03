from gardendesigner.agent import BasePipeline
from gardendesigner.agent.attribute import AttributeAgent
from gardendesigner.config.prompt import Prompt
import threading
class ThreadsPool(threading.Thread):
    def __init__(self, func, args=()):
        super(ThreadsPool, self).__init__()
        self.func = func
        self.args = args
        self.result = None

    def run(self):
        self.result = self.func(*self.args)
    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


class Pipline(BasePipeline):
    def __init__(self, agents,use_conlan=False):
        super().__init__(agents)
        self.use_conlan = use_conlan
        self._check(use_conlan=use_conlan)
        self.prompt = Prompt
    def _check(self,
               use_conlan:bool):
        """检验agents序列类型"""
        oil = [isinstance(agent,AttributeAgent) for agent in self.agents]
        if use_conlan:
            if not any(oil):
                raise ValueError("you need an AttributeAgent")
        else:
            if any(oil):
                raise ValueError("you not need an AttributeAgent")
        
    def run(self,text):
        threads = []
        for agent in self.agents:
            sys_messages = agent.loade_base_messages(prompt=self.prompt)
            threads.append(ThreadsPool(agent._call_llm, (sys_messages, text)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        for thread in threads:
            self.pipeline_output.append(thread.get_result())
        if not self.use_conlan:
            attribute_gptres = """{
                    "data":[
                        [1,-1,-1,-1,-1],
                        [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]],
                        [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]],
                        [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
                    ],
                    "feedback":"OK"
                }"""
            self.pipeline_output.append(attribute_gptres)
        # TODO 完成pipline