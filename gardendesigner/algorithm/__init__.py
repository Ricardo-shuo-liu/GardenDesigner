import abc
from gardendesigner.config.param import BaseParam
from typing import List
class Algorithm(abc.ABC):
    def __init__(self):
        self.baseparam = BaseParam()
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
            dx_dys = [(0, 1), (0, -1), (1, 0), (-1, 0)]# 四个探索方向types_count = [0 for _ in range(6)]
            for x, y in component:
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
    @abc.abstractmethod
    def excute(self):
        raise