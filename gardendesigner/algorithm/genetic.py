from typing import List,Callable
from gardendesigner.config.param import BaseParam
from copy import deepcopy
import random
class GeneticAlgorithm():
    def __init__(self):
        self.baseparam = BaseParam()
    def excute(self,
               args,
               parameters: dict) -> List[List[int]]:
            """遗传算法生成地形"""
            if args.use_conlan:
                return self.genetic_algorithm(
                    parameters,
                    5,
                    terrain_fitness,
                    terrain_evo,
                    100,
                    self.baseparam.MAX_GENERATION,
                    self.baseparam.MUTATION_RATE,
                    self.baseparam.CROSSOVER_RATE,
                    True
                )[0]
            else:
                return self.genetic_algorithm(
                    parameters,
                    5,
                    terrain_fitness_with_loc,
                    terrain_evo,
                    100,
                    self.baseparam.MAX_GENERATION,
                    self.baseparam.MUTATION_RATE,
                    self.baseparam.CROSSOVER_RATE,
                    False
                )[0]
    def genetic_algorithm(self,
                          parameters: dict,       # 设计要求：地形/属性/道路约束
                          n: int,                 # 网格大小 n*n，n=5 → 5x5
                          fitness_func: Callable, # 打分函数：给园林算分
                          fix_func: Callable,     # 修复函数：让园林变合法
                          fitness_thres: float,   # 目标分数：达到就停止
                          max_generation: int,    # 最多进化多少代
                          mutation_rate: float,   # 变异概率
                          crossover_rate: float,  # 杂交概率
                          is_use_conlan:bool = False,
                          terrain=None,
                          infrastructure=None,
                          use_fix: bool = True,
                          alpha:float = -1e-6
                          ):
        """
        遗传算法核心
        Args:
            parameters(dict): 设计要求：地形/属性/道路约束
            n(int):网格大小 n*n，n=5 → 5x5
            fitness_func(Callable):打分函数：给园林算分
            fix_func(Callable):修复函数：让园林变合法
            fitness_thres(float):目标分数：达到就停止
            max_generation(int): 最多进化多少代
            mutation_rate(float):变异概率
            crossover_rate(float):杂交概率
            is_use_conlan(bool):是否使用conlan
            terrain:生成的地图
            infrastructure:生成的道路
            use_fix:是否开启修复
        Return:
            None
        """
        population = self._init_population(n=n)
        # 保存全局最优
        max_fitness, max_grid = 0, None
        for i in range(max_generation):
            fitness_list = []
            fitness_sum = 0 
            local_max_fitness = 0
            for j in range(self.baseparam.POPULATION_SIZE):
                # 判断是否启用conlan
                if is_use_conlan:
                    fitness = fitness_func(population[j], parameters, terrain, infrastructure)
                else:
                    fitness = fitness_func(population[j], parameters, terrain, infrastructure, i)
                # 更新参数
                fitness_list.append(fitness)
                fitness_sum += fitness
                local_max_fitness = fitness if fitness > local_max_fitness else local_max_fitness
                if fitness > max_fitness:
                    max_fitness = fitness
                    max_grid = deepcopy(population[j])
                elif fitness == max_fitness:
                    if random.random() < 0.5:
                        max_grid = deepcopy(population[j])
                    # 0.5 概率保留

                if max_fitness - fitness_thres > alpha:# 大于alpha结束
                    break
                 
                new_population = []
                
    def _init_population(self,n):
        population = []
        # 初始化种群
        for i in range(self.baseparam.POPULATION_SIZE):  # 100个
            population.append(self.randominit(n, 5))  # 随机生成 n*n 网格
        return population
    
    def randominit(self,n: int,
                   splits: int) -> List[List[int]]:
        pass