from typing import List,Callable,Tuple
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
                          n: int,                 # 地形数量
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
            n(int):地形数量
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
            # 选择
            for j in range(self.baseparam.POPULATION_SIZE):
                times = int(fitness_list[j] * self.baseparam.POPULATION_SIZE / fitness_sum)
                for k in range(times):
                    new_population.append(deepcopy(population[j]))
                fitness_list[j] -= times * fitness_sum / self.baseparam.POPULATION_SIZE
                # 对于占比低的灭绝
            fitness_list_with_index = list(enumerate(fitness_list)) # add index for each fitness
            fitness_list_with_index.sort(key=lambda x: x[1], reverse=True) # 
            # 将建立得分和其原始对应的位置
            len_now = len(new_population)
            for j in range(self.baseparam.POPULATION_SIZE - len_now - self.baseparamPRESERVE_BEST_SIZE):
                new_population.append(deepcopy(population[fitness_list_with_index[j][0]]))
            # 如果淘汰足够多 按顺序填充
            len_now = len(new_population)
            for j in range(self.baseparam.POPULATION_SIZE - len_now):
                new_population.append(deepcopy(max_grid))
            # 剩下的全部按照最优来填充
            
            # 交叉
            random.shuffle(new_population)
            # 打乱种群
            for j in range(0, self.baseparam.POPULATION_SIZE, 2):
                if random.random() < crossover_rate:
                    new_population[j], new_population[j + 1] = self.crossover(new_population[j], new_population[j + 1], n)
            # 变异--加入随机因子
            for j in range(self.baseparam.POPULATION_SIZE):
                if random.random() < mutation_rate:
                    new_population[j] = self.mutation(new_population[j], n)
            # 修复
            if use_fix:
                for j in range(self.baseparam.POPULATION_SIZE):
                    if random.random() < self.baseparam.FIX_RATE:
                        new_population[j] = fix_func(new_population[j], parameters, terrain, infrastructure)
            population = new_population

        return max_grid, max_fitness
    
    def _init_population(self,n):
        population = []
        # 初始化种群
        for i in range(self.baseparam.POPULATION_SIZE):  # 100个
            population.append(self.randominit(n, 5))  # 地形数量
        return population
    
    def randominit(self,
                   n: int,
                   splits: int) -> List[List[int]]:
        """随机生成初始化地形""" 
        grid = [[0 for _ in range(self.baseparam.H)] for _ in range(self.baseparam.W)]
        # 初始化地图
        assert self.baseparam.W % splits == 0 and self.baseparam.H % splits == 0
        blockw, blockh = self.baseparam.W // splits, self.baseparam.H // splits

        # 填充五个部分
        for i in range(splits):
            for j in range(splits):
                randnum = random.randint(0, n - 1)
                for k in range(blockw):
                    for l in range(blockh):
                        grid[i * blockw + k][j * blockh + l] = randnum
        # 对于五个切分的部分随机选择填充

        # 让生存的地图更自然 核心的目的是在每个split的部分再随机填充一个 blockw X blockh 的block
        for i in range(splits - 1):
            for j in range(splits - 1):
                randnum = random.randint(0, n - 1)
                for k in range(blockw):
                    for l in range(blockh):
                        grid[i * blockw + blockw // 2 + k][j * blockh + blockh // 2 + l] = randnum
        return grid

    def crossover(self,
                  parent1: List[List[int]],
                  parent2: List[List[int]],
                  n: int) -> Tuple[List[List[int]], List[List[int]]]:
        """交叉"""
        components1 = self.find_connected_components(parent1, {}, n)
        components2 = self.find_connected_components(parent2, {}, n)

        # TODO 交叉核心
    def find_connected_components(self,
                                  grid: List[List[int]],
                                  split_edges: dict, 
                                  n: int) -> List[list]:
        """
        寻找连接在一起的相同区域

        Args:
            grid(List[List[int]]):要寻找的区域
            split_edges(dict):墙
            n(int):地形数量
        Returns:
            components(List[list]):链接在一起的区域
        """
        def is_valid(x, y):
            # Check if the coordinates are within the grid boundaries
            return 0 <= x < self.baseparam.W and 0 <= y < self.baseparam.H
        def dfs(
            x:int,
            y:int,
            component_id:int):
            """深度优先用于标记区域"""
            stack = [(x, y)]
            component = []
            dx_dys = [(0, 1), (0, -1), (1, 0), (-1, 0)]# 四个探索方向
            while stack:
                current_x, current_y = stack.pop()
                if component_labels[current_x][current_y] != -1:
                    continue
                component_labels[current_x][current_y] = component_id
                component.append((current_x, current_y))
                for dx, dy in dx_dys:
                    new_x, new_y = current_x + dx, current_y + dy
                    # 这里使用的是网格表示范 x，y标识一个网格 然后(x,y)(x+1,y),(x,y+1) (x+1,y+1)
                    # 表示四个定点 split_edge 为一个格子上的边
                    if dx == 0 and dy == 1:
                        split_edge = ((current_x, current_y + 1), (current_x + 1, current_y + 1))
                    elif dx == 0 and dy == -1:
                        split_edge = ((current_x, current_y), (current_x + 1, current_y))
                    elif dx == 1 and dy == 0:
                        split_edge = ((current_x + 1, current_y), (current_x + 1, current_y + 1))
                    elif dx == -1 and dy == 0:
                        split_edge = ((current_x, current_y), (current_x, current_y + 1))
                    # not overstep; adjacent grids have same terrain type; 
                    if (
                        is_valid(new_x, new_y)
                        and grid[new_x][new_y] == grid[x][y] # why not current_x/y
                        and ((split_edge not in split_edges) or split_edges[split_edge] == 0)
                    ):
                        stack.append((new_x, new_y))

            return component

        component_labels = [[-1 for _ in range(self.baseparam.H)] for _ in range(self.baseparam.W)]
        # 设置mask用于记录是否探索过
        components = [[] for _ in range(n)]
        # 返回对象
        component_id = 0
        # 记录区域id

        for x in range(self.baseparam.W):
            for y in range(self.baseparam.H):
                # 遍历每一个格子
                if component_labels[x][y] == -1:
                    # 如果没被探索
                    component = dfs(x, y, component_id) 
                    components[grid[x][y]].append(component)
                    component_id += 1

        return components
    def mutation(self,):
        pass