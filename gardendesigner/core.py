import os
from gardendesigner.config.param import GetEnvParam
from gardendesigner.agent.terrain import TerrainGenerationAgent
from gardendesigner.agent.inf import RoadGenErationAgent
from gardendesigner.config.prompt import Prompt
from gardendesigner.agent.attribute import AttributeAgent
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
def main(args,
         text: str,
         use_query: bool,
         ckp: str,
         num: int,
         geter:GetEnvParam) -> None:
    llm_key = geter.get_key()
    llm_base_url = geter.get_base_url()
    llm_name = geter.get_model_name()
    prompt = Prompt()
    if num <= 1:
        parameters, total_feedback, terrain, infrastructure, attributes = [None for _ in range(5)]
        if os.path.exists("checkpoints/" + ckp + ".npy"):
            pass
        else:
            print("newly generate")
            terrain_gptres, inf_gptres, attribute_gptres = "", "", ""
            if use_query:
                terraingenerationagent = TerrainGenerationAgent(llm_model=llm_name,
                                                                llm_key=llm_key,
                                                                llm_base_url=llm_base_url)
                roadgenerationagent = RoadGenErationAgent(
                    llm_model=llm_name,
                    llm_key=llm_key,
                    llm_base_url=llm_base_url
                )
                attributeagent = AttributeAgent(llm_model=llm_name,
                                                        llm_key=llm_key,
                                                        llm_base_url=llm_base_url)
                attribute_sys_messages = attributeagent.loade_base_messages(prompt=prompt)
                terrain_sys_messages = terraingenerationagent.loade_base_messages(prompt=prompt)
                inf_sys_messages = roadgenerationagent.loade_base_messages(prompt=prompt)
                
                if use_query:
                    threads = []
                    threads.append(ThreadsPool(terraingenerationagent._call_llm, (terrain_sys_messages, text))) # text is brief, so input same query many times
                    threads.append(ThreadsPool(roadgenerationagent._call_llm, (inf_sys_messages, text)))
                    
                    if args.use_conlan:
                        threads.append(ThreadsPool(attributeagent._call_llm, (attribute_sys_messages, text)))
                    for thread in threads:
                        thread.start()
                    for thread in threads:
                        thread.join()
                    if args.use_conlan:
                        terrain_gptres, inf_gptres, attribute_gptres = (
                            threads[0].get_result(),
                            threads[1].get_result(),
                            threads[2].get_result(),
                        )
                    else:
                        terrain_gptres, inf_gptres = (
                            threads[0].get_result(),
                            threads[1].get_result(),
                        )
                    terrain_parameters, terrain_feedback = terraingenerationagent._parse_llm_response(text=terrain_gptres)
                    inf_parameters, inf_feedback = roadgenerationagent._parse_llm_response(text=inf_gptres)
                    if not args.use_conlan:
                        attribute_gptres = """{
                            "data":[
                                [1,-1,-1,-1,-1],
                                [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]],
                                [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]],
                                [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
                            ],
                            "feedback":"OK"
                        }"""
                    attribute_parameters, attribute_feedback = AttributeAgent._parse_llm_response(attribute_gptres)
                    parameters = {}
                    parameters.update(terrain_parameters)
                    parameters.update(inf_parameters)
                    parameters.update(attribute_parameters)
                    total_feedback = terrain_feedback + "\n" + inf_feedback + "\n" + attribute_feedback # "OK" in default
                    print(parameters)
                    terrain = terraingenerationagent.execute(args, parameters) # grid
                else:
                    pass
            
    else:
        pass