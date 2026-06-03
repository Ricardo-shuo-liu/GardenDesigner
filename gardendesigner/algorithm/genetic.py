from typing import List,Callable,Tuple
from gardendesigner.algorithm import BaseAlgorithm
from copy import deepcopy
import random
from math import (
    floor,
    ceil)
class GeneticAlgorithm(BaseAlgorithm):
    def __init__(self):
        super().__init__()
    def excute(self,
               args,
               parameters: dict) -> List[List[int]]:
            """遗传算法生成地形"""
            if args.use_conlan:
                return self.genetic_algorithm(
                    parameters,
                    5,
                    self.terrain_fitness,
                    self.terrain_evo,
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
                    self.terrain_fitness_with_loc,
                    self.terrain_evo,
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
            for j in range(self.baseparam.POPULATION_SIZE - len_now - self.baseparam.PRESERVE_BEST_SIZE):
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
        randx, randy, comp_idx1, comp_idx2, type1, type2 = [None for _ in range(6)]
        success = False
        for k in range(10): # 随机获取最多10次
            randx, randy = random.randint(0, self.baseparam.W - 1), random.randint(0, self.baseparam.H - 1)
            comp_idx1, comp_idx2 = None, None
            for i in range(n):
                for j in range(len(components1[i])):
                    if (randx, randy) in components1[i][j]:
                        type1 = i
                        comp_idx1 = (i, j)
                        break
                if comp_idx1 != None:
                    break
            for i in range(n):
                for j in range(len(components2[i])):
                    if (randx, randy) in components2[i][j]:
                        type2 = i
                        comp_idx2 = (i, j)
                        break
                if comp_idx2 != None:
                    break
            if type1 != type2:
                success = True
                break
        if not success: # 如果两块type一样
            return parent1, parent2
        # 获得对应的区块信息
        comp1, comp2 = components1[comp_idx1[0]][comp_idx1[1]], components2[comp_idx2[0]][comp_idx2[1]]
        # 获取共同部分
        intersection = set(comp1).intersection(set(comp2))
        # 计算比例
        intersection_rate = len(intersection) / (len(comp1) + len(comp2) - len(intersection))

        use_approx = random.random() < self.baseparam.CROSSOVER_APPROX_RATE
        # 是否全部交换
        if use_approx:
            if intersection_rate < self.baseparam.CROSSOVER_APPROX_ACCEPT_RATE: 
                # 如果重合度不够高
                return parent1, parent2
            else:
                # 区块全部交换
                for x, y in comp1:
                    parent1[x][y] = type2
                for x, y in comp2:
                    parent2[x][y] = type1
                return parent1, parent2
        else:
            # 只交换重叠部分
            for x, y in intersection:
                parent1[x][y] = type2
                parent2[x][y] = type1
            return parent1, parent2
    def mutation(self,
                 grid: List[List[int]],
                 n: int) -> List[List[int]]:
        """变异"""
        # 随机获取变异区域
        randw, randh = random.randint(self.baseparam.MUTATION_MINL, self.baseparam.MUTATION_MAXL), random.randint(self.baseparam.MUTATION_MINL, self.baseparam.MUTATION_MAXL)
        randx, randy = random.randint(0, self.baseparam.W - randw), random.randint(0, self.baseparam.H - randh)
        # 概率选择变异情况
        region_mutation = random.random() < self.baseparam.REGION_MUTATION_RATE
        consistent_mutation = random.random() < self.baseparam.MUTATION_CONSISTENT_RATE

        if region_mutation:
            components = self.find_connected_components(grid, {}, n)
            components_count = 0
            for i in range(n):
                components_count += len(components[i])
            
            rand_idx = random.randint(0, components_count - 1)
            component_type, component = None, None
            # 找到随机到的连通块的位置
            for i in range(n):
                if rand_idx < len(components[i]):
                    component_type = i
                    component = components[i][rand_idx]
                    break
                rand_idx -= len(components[i])
            new_type = random.randint(0, n - 1)
            # 抽取一个和当前不同的type用于替换
            while new_type == component_type:
                new_type = random.randint(0, n - 1)
            for x, y in component:
                grid[x][y] = new_type
        else:
            # 如果和周围的type一样
            if consistent_mutation:
                randtype = None
                # 存储周围的类别信息
                adjacent_types = set()
                # 矩阵大小+1 用于获取type
                for i in range(randx - 1, randx + randw + 1):
                    for j in range(randy - 1, randy + randh + 1):
                        if (
                        0 <= i < self.baseparam.W
                        and (i == randx - 1 or i == randx + randw)
                        and 0 <= j < self.baseparam.H
                        and (j == randy - 1 or j == randy + randh)):
                            adjacent_types.add(grid[i][j])
                if len(adjacent_types) == 0:
                    randtype = random.randint(0, n - 1)
                else:
                    # 随机挑选一个类别
                    randtype = random.choice(list(adjacent_types))
                for i in range(randw):
                    for j in range(randh):
                        grid[randx + i][randy + j] = randtype      
            else:
                # 随机选者type
                randtype = random.randint(0, n - 1)
                for i in range(randw):
                    for j in range(randh):
                        grid[randx + i][randy + j] = randtype
        
        return grid
    def terrain_evo(self,
                    grid: List[List[int]],
                    parameters: dict,
                    terrain,
                    infrastructure) -> List[List[int]]:
        """修复函数"""
        components = self.find_connected_components(grid, {}, 5)
        # 获取五个地形是否存在
        terrain_exist = deepcopy(parameters["terrain_exist"])
        for tp in range(5):
            exist = terrain_exist[tp]
            real_region_num = len(components[tp])
            # 如果地形不存在但是生成的时候生成相关地形
            if exist == 0 and real_region_num > 0:
                # 将该地形全部转化为陆地 2
                for component in components[tp]:
                    for x, y in component:
                        grid[x][y] = 2
                return grid
            # 如果这个地形存在但是没有生成
            elif exist == 1 and real_region_num == 0:
                # 随机生存一个区域设置为该类型
                randw, randh = random.randint(2, 4), random.randint(2, 4)
                randx, randy = random.randint(0, self.baseparam.W - randw), random.randint(0, self.baseparam.H - randh)
                for i in range(randw):
                    for j in range(randh):
                        grid[randx + i][randy + j] = tp
                return grid
        dx_dys = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        # 对于未定义的区域
        for component in components[0]:
            types_count = [0 for _ in range(6)]
            for x, y in component:
                for dx, dy in dx_dys:
                    new_x, new_y = x + dx, y + dy

                    if 0 <= new_x < self.baseparam.W and 0 <= new_y < self.baseparam.H:
                        # 如果附近的格子不在当前区域内
                        if (new_x, new_y) not in component:
                            types_count[grid[new_x][new_y]] += 1
                    # 如果不合法 最后的类别加一
                    else:
                        types_count[-1] += 1
            # 如果这个未使用的地区没有依靠在地图边界 将其转化为合法正常类型
            if types_count[-1] == 0:
                # 在允许存在的地形里面选择填充地形
                # 在官方的GitHub的代码中这里存在逻辑错误会生成不允许存在的地形
                allowed = [tp for tp in range(1,5) if terrain_exist[tp] == 1]
                new_type = random.choice(allowed)
                for x, y in component:
                    grid[x][y] = new_type
                return grid
        return grid
    
    def get_boundary(self,
                     grid: List[List[int]],
                     get: bool = False) -> Tuple[bool, List[Tuple[int, int]]]:
        """判断是否联通并且选择获取边缘的轮廓点"""
        new_grid = deepcopy(grid)
        # 遍历地图上每一个点
        for i in range(self.baseparam.W):
            for j in range(self.baseparam.H):
                # 将所有的使用的点的type转化为1用于判断是否联通
                if new_grid[i][j] != 0:
                    new_grid[i][j] = 1
        components = self.find_connected_components(new_grid, {}, 2)
        # 判断是否联通
        if len(components[1]) != 1:
            return False, []
        
        if not get:
            return True, []
        # 存储边界数据
        boundary_edges = []
        for i in range(self.baseparam.W):
            # 增加一个用于下边界
            for j in range(self.baseparam.H + 1):
                # 上界
                if j == 0:
                    if new_grid[i][j] == 1:
                        boundary_edges.append([(i, j), (i + 1, j)])
                # 下界
                elif j == self.baseparam.H:
                    if new_grid[i][j - 1] == 1:
                        boundary_edges.append([(i, j), (i + 1, j)])
                # 分割
                elif new_grid[i][j - 1] != new_grid[i][j]:
                    boundary_edges.append([(i, j), (i + 1, j)])
        for i in range(self.baseparam.W + 1):
            # 增加一个用于判断右边界
            for j in range(self.baseparam.H):
                #  左界
                if i == 0:
                    if new_grid[i][j] == 1:
                        boundary_edges.append([(i, j), (i, j + 1)])
                # 右界
                elif i == self.baseparam.W:
                    if new_grid[i - 1][j] == 1:
                        boundary_edges.append([(i, j), (i, j + 1)])
                # 分割
                elif new_grid[i - 1][j] != new_grid[i][j]:
                    boundary_edges.append([(i, j), (i, j + 1)])
        # 起点
        ordered_boundary_corners = [boundary_edges[0][0]]
        # 依据起点实现围绕成圈
        while True:
            corner = ordered_boundary_corners[-1]
            for edge in boundary_edges:
                if edge[0] == corner:
                    ordered_boundary_corners.append(edge[1])
                    boundary_edges.remove(edge)
                    break
                elif edge[1] == corner:
                    ordered_boundary_corners.append(edge[0])
                    boundary_edges.remove(edge)
                    break
            if ordered_boundary_corners[-1] == ordered_boundary_corners[0]:
                break
        return True, ordered_boundary_corners[:-1]
    def terrain_fitness(self,
                        grid: List[List[int]],
                        parameters: dict,
                        terrain,
                        infrastructure) -> float:
        """打分函数"""
        """使用完整版本的打分函数"""
        # 判断是否联通
        connected, _ = self.get_boundary(grid)
        
        if not connected:
            return 0
        
        components = self.find_connected_components(grid, {}, 5)
        terrain_exist, terrain_region_num, terrain_region_area, terrain_region_single_area = (
            deepcopy(parameters["terrain_exist"]),
            deepcopy(parameters["terrain_region_num"]),
            deepcopy(parameters["terrain_region_area"]),
            deepcopy(parameters["terrain_region_single_area"]),
        )


        loss = 1
        for tp in range(5):# 对于每个地形
            exist, region_num, region_area, region_single_area = (
                terrain_exist[tp],
                terrain_region_num[tp],
                terrain_region_area[tp],
                terrain_region_single_area[tp],
            )

            real_region_num = len(components[tp]) # 判断

            if exist == -1: 
                # 默认存在
                exist = 1
            if exist == 0 and real_region_num > 0:
                # 不应该存在但存在
                loss += 20
                continue
            elif exist == 1 and real_region_num == 0:
                # 应该存在但不存在
                loss += 20
                continue
            if real_region_num == 0:# 不存在
                continue

            if region_num == -1:
                region_num = (-1, -1)
            # 修正格式

            lowerline, highline = region_num
            # 修正上下限数值关系情况
            if tp == 1 and highline == -1:
                # 如果为水源类型 默认上为 3 如果上下限存在数值差异 那么将上限转化为 max(lowerline, 3)
                highline = 3 if lowerline == -1 else max(lowerline, 3)
            elif tp == 2 and highline == -1:
                highline = 4 if lowerline == -1 else max(lowerline, 4)
            elif tp == 3 and highline == -1:
                highline = 3 if lowerline == -1 else max(lowerline, 3)
            elif tp == 4 and highline == -1:
                highline = 3 if lowerline == -1 else max(lowerline, 3)
            
            if lowerline != -1 and real_region_num < lowerline:
                loss += min(lowerline - real_region_num, 5)
                # 如果低于最小loss增加
            if highline != -1 and real_region_num > highline:
                loss += min(real_region_num - highline, 5)
                # 如果搞于最高loss增加
            

            if region_area == -1:
                region_area = (-1, -1)
            # 修正格式
            real_region_area = 0

            for component in components[tp]:
                real_region_area += len(component)
            real_region_area /= self.baseparam.W * self.baseparam.H
            # 计算占比
            lowerline, highline = region_area
            # 修正上限界默认值
            if tp == 0:
                if highline == -1:
                    highline = 0.2 if lowerline == -1 else max(lowerline, 0.2)
                if lowerline == -1:
                    lowerline = 0.05 if highline == -1 else min(highline, 0.05)
            elif tp == 1:
                if highline == -1:
                    highline = 0.6 if lowerline == -1 else max(lowerline, 0.6)
                if lowerline == -1:
                    lowerline = 0.2 if highline == -1 else min(highline, 0.2)
            elif tp == 2:
                if highline == -1:
                    highline = 0.7 if lowerline == -1 else max(lowerline, 0.7)
                if lowerline == -1:
                    lowerline = 0.3 if highline == -1 else min(highline, 0.3)
            elif tp == 3:
                if highline == -1:
                    highline = 0.4 if lowerline == -1 else max(lowerline, 0.4)
                if lowerline == -1:
                    lowerline = 0.1 if highline == -1 else min(highline, 0.1)
            elif tp == 4:
                if highline == -1:
                    highline = 0.35 if lowerline == -1 else max(lowerline, 0.35)
                if lowerline == -1:
                    lowerline = 0.15 if highline == -1 else min(highline, 0.15)
            # 更新loss
            if lowerline != -1 and real_region_area < lowerline:
                loss += min((lowerline - real_region_area) * 100, 5)
            if highline != -1 and real_region_area > highline:
                loss += min((real_region_area - highline) * 100, 5)

            if region_single_area == -1:
                region_single_area = (-1, -1)
            real_region_single_area = []
            for component in components[tp]:
                real_region_single_area.append(len(component) / self.baseparam.W / self.baseparam.H)
            lowerline, highline = region_single_area
            if tp == 1 and lowerline == -1:
                lowerline = 0.02 if highline == -1 else min(highline, 0.02)
            elif tp == 2 and lowerline == -1:
                lowerline = 0.02 if highline == -1 else min(highline, 0.02)
            elif tp == 3 and lowerline == -1:
                lowerline = 0.01 if highline == -1 else min(highline, 0.01)
            elif tp == 4 and lowerline == -1:
                lowerline = 0.02 if highline == -1 else min(highline, 0.02)
            # 更新loss
            local_loss = 0
            for area in real_region_single_area:
                if lowerline != -1 and area < lowerline:
                    local_loss += min((lowerline - area) * 100, 2)
                if highline != -1 and area > highline:
                    local_loss += min((area - highline) * 100, 2)
            loss += min(local_loss, 5)


        dx_dys = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        adjacent_types = [[] for _ in range(5)]
        land_in_lake_count = 0

        for tp in range(5):
            for component in components[tp]:
                types_count = [0 for _ in range(6)]
                # 统计该地形区域下的周围数据地形类型
                for x, y in component:
                    for dx, dy in dx_dys:
                        new_x, new_y = x + dx, y + dy
                        if 0 <= new_x < self.baseparam.W and 0 <= new_y < self.baseparam.H:
                            if (new_x, new_y) not in component:
                                types_count[grid[new_x][new_y]] += 1
                        else:
                            types_count[-1] += 1
                adjacent_types[tp].append(types_count)
                if tp == 0:
                    if types_count[-1] == 0: # 未使用的地形需要靠墙
                        loss += min(types_count[1] * 0.8, 15)
                elif tp == 1:
                    if types_count[4] > 0:
                        # 如果湖旁边是建筑
                        loss += min(types_count[4] * 0.3, 5)
                    if types_count[0] + types_count[-1] > 0:
                        # 如果旁边存在空地或者达到边界
                        loss += min((types_count[0] + types_count[-1]) * 0.2, 3)
                elif tp == 2 or tp == 3:
                    if (
                        types_count[0] + types_count[-1] + types_count[2] + types_count[3] + types_count[4] == 0
                        and len(component) / (self.baseparam.W * self.baseparam.H) < 0.02
                    ):
                        land_in_lake_count += 1
                        # land在湖中间
                elif tp == 4:
                        if types_count[0] + types_count[-1] > 0:
                            loss += min((types_count[0] + types_count[-1]) * 0.3, 5)        
                
        lake_count = 0
        for component in components[1]:
            if len(component) / (self.baseparam.W * self.baseparam.H) > 0.08:
                # 判断湖泊数量
                lake_count += 1
        if land_in_lake_count < lake_count:
            loss += min((lake_count - land_in_lake_count) * 2, 5)

        fitness = 100 / loss
        return fitness
    def terrain_fitness_with_loc(self,
                                 grid: List[List[int]],
                                 parameters: dict,
                                 terrain,
                                 infrastructure,
                                 generation: int) -> float:
        """打分函数"""
        """非完整启动版本"""
        # 判断是否联通
        connected, _ = self.get_boundary(grid)
        
        if not connected:
            return 0
        
        components = self.find_connected_components(grid, {}, 5)
        terrain_exist, terrain_region_num, terrain_region_area, terrain_region_single_area = (
            deepcopy(parameters["terrain_exist"]),
            deepcopy(parameters["terrain_region_num"]),
            deepcopy(parameters["terrain_region_area"]),
            deepcopy(parameters["terrain_region_single_area"]),
        )
        loss = 1

        for tp in range(5):
            exist, region_num, region_area, region_single_area = (
                terrain_exist[tp],
                terrain_region_num[tp],
                terrain_region_area[tp],
                terrain_region_single_area[tp],
            )
            real_region_num = len(components[tp])
            if tp in [1,2,3] :
                exist = 1
            # 如果为1,2,3 那么必须存在
            
            if exist == -1:
                exist = 1
            if exist == 0 and real_region_num > 0:
                loss += 20
                continue
            elif exist == 1 and real_region_num == 0:
                loss += 20
                continue
            if real_region_num == 0:
                continue

            if region_num == -1:
                region_num = (-1, -1)
            # 修正格式
            lowerline, highline = region_num
            # 修正上下限数值关系情况
            if tp == 1 and highline == -1:
                # 如果为水源类型 默认上为 1 如果上下限存在数值差异 那么将上限转化为 max(lowerline, 3)
                highline = 1 if lowerline == -1 else max(lowerline, 3)
            elif tp == 2 and highline == -1:
                highline = 2 if lowerline == -1 else max(lowerline, 2)
            elif tp == 3 and highline == -1:
                highline = 3 if lowerline == -1 else max(lowerline, 3)
            elif tp == 4 and highline == -1:
                highline = 3 if lowerline == -1 else max(lowerline, 3)
            
            if lowerline != -1 and real_region_num < lowerline:
                loss += min(lowerline - real_region_num, 5)
                # 如果低于最小loss增加
            if highline != -1 and real_region_num > highline:
                loss += min(real_region_num - highline, 5)
                # 如果搞于最高loss增加
            
            
            if region_area == -1:
                region_area = (-1, -1)
            # 修正格式
            real_region_area = 0

            for component in components[tp]:
                real_region_area += len(component)
            real_region_area /= self.baseparam.W * self.baseparam.H
            # 计算占比
            lowerline, highline = region_area
            # 修正上限界默认值
            if tp == 0:
                if highline == -1:
                    highline = 0.15 if lowerline == -1 else max(lowerline, 0.15)
                if lowerline == -1:
                    lowerline = 0.05 if highline == -1 else min(highline, 0.05)
            elif tp == 1:
                if highline == -1:
                    highline = 0.4 if lowerline == -1 else max(lowerline, 0.4)
                if lowerline == -1:
                    lowerline = 0.2 if highline == -1 else min(highline, 0.2)
            elif tp == 2:
                if highline == -1:
                    highline = 0.3 if lowerline == -1 else max(lowerline, 0.3)
                if lowerline == -1:
                    lowerline = 0.1 if highline == -1 else min(highline, 0.1)
            elif tp == 3:
                if highline == -1:
                    highline = 0.5 if lowerline == -1 else max(lowerline, 0.5)
                if lowerline == -1:
                    lowerline = 0.2 if highline == -1 else min(highline, 0.2)
            elif tp == 4:
                if highline == -1:
                    highline = 0 if lowerline == -1 else max(lowerline, 0)
                if lowerline == -1:
                    lowerline = 0 if highline == -1 else min(highline, 0)
                # NOTE 这里官方代码的注释和代码不符合 我认为是取消高地
            # 更新loss
            if lowerline != -1 and real_region_area < lowerline:
                loss += min((lowerline - real_region_area) * 100, 5)
            if highline != -1 and real_region_area > highline:
                loss += min((real_region_area - highline) * 100, 5)
            if tp == 1:
                # 水源处于中心得分
                for component in components[tp]:
                    center_pixel_loss = 10
                    centering_pixel_count = 0
                    for x, y in component:
                        split_W = floor(self.baseparam.W/3)
                        split_H = floor(self.baseparam.H/3)
                        if ceil(self.baseparam.W/2-split_W)<= x < floor(self.baseparam.W/2+split_W) and ceil(self.baseparam.H/2-split_H)<= y < floor(self.baseparam.H/2+split_H):
                            centering_pixel_count +=1
                    if centering_pixel_count >=18:
                        center_pixel_loss = 0
                    loss += center_pixel_loss
            
            if region_single_area == -1:
                region_single_area = (-1, -1)
            real_region_single_area = []
            for component in components[tp]:
                real_region_single_area.append(len(component) / self.baseparam.W / self.baseparam.H)
            lowerline, highline = region_single_area
            if tp == 1 and lowerline == -1:
                lowerline = 0.02 if highline == -1 else min(highline, 0.02)
            elif tp == 2 and lowerline == -1:
                lowerline = 0.01 if highline == -1 else min(highline, 0.01)
            elif tp == 3 and lowerline == -1:
                lowerline = 0.03 if highline == -1 else min(highline, 0.03)
            elif tp == 4 and lowerline == -1:
                lowerline = 0.00 if highline == -1 else min(highline, 0.00)
            local_loss = 0
            for area in real_region_single_area:
                if lowerline != -1 and area < lowerline:
                    local_loss += min((lowerline - area) * 100, 2)
                if highline != -1 and area > highline:
                    local_loss += min((area - highline) * 100, 2)
            loss += min(local_loss, 5)

        dx_dys = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        adjacent_types = [[] for _ in range(5)]
        land_in_lake_count = 0
        for tp in range(5):
            for component in components[tp]:
                types_count = [0 for _ in range(6)]
                for x, y in component:
                    for dx, dy in dx_dys:
                        new_x, new_y = x + dx, y + dy
                        if 0 <= new_x < self.baseparam.W and 0 <= new_y < self.baseparam.H:
                            if (new_x, new_y) not in component:
                                types_count[grid[new_x][new_y]] += 1
                        else:
                            types_count[-1] += 1 
                adjacent_types[tp].append(types_count)
                if tp == 0:
                    if types_count[-1] == 0: 
                        loss += min(types_count[1] * 0.8, 15)
                elif tp == 1:
                    if types_count[0] + types_count[-1] > 0:
                        loss += min((types_count[0] + types_count[-1]) * 0.2, 3)
                elif tp == 2 or tp == 3:
                    if (
                        types_count[0] + types_count[-1] + types_count[2] + types_count[3] + types_count[4] == 0
                        and len(component) / (self.baseparam.W * self.baseparam.H) < 0.02
                    ):
                        land_in_lake_count += 1
                elif tp == 4:
                    if types_count[0] + types_count[-1] > 0:
                        loss += min((types_count[0] + types_count[-1]) * 0.3, 5)
       
        lake_count = 0
        for component in components[1]:
            if len(component) / (self.baseparam.W * self.baseparam.H) > 0.08:
                lake_count += 1
        if land_in_lake_count < lake_count:
            loss += min((lake_count - land_in_lake_count) * 2, 5)
        fitness = 100 / loss
        # NOTE 本部分和完整除了部分数据基本一样
        # 核心修正在存在了增加以水为中心的loss函数
        # 在原始论文中没有使用完整的部分
        return fitness
                