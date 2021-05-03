class Node:
    def __init__(self, value, neighbor=None, weight=None):
        self.value = value
        self.neighbor = neighbor
        self.weight = weight

    def __str__(self):
        return str(self.value)


class Graph:
    def __init__(self, value_list, arc_list, weight_list):
        self.nodes = {value: Node(value) for value in value_list}
        for value, arc, weight in zip(value_list, arc_list, weight_list):
            self.nodes[value].neighbor = [self.nodes[i] for i in arc]
            self.nodes[value].weight = weight

    def add(self, value, arc_list, weight_list):
        node = Node(value, weight=weight_list)
        neighbor = list()
        for value_ in arc_list:
            if value_ in self.nodes:
                neighbor.append(self.nodes[value_])
            else:
                print(f'value {value_} not in graph, please add first!')
                return
        node.neighbor = neighbor
        for n in node.neighbor:
            n.neighbor.append(node)
        self.nodes[value] = node

    def delete(self, target_value):
        target_node = self.nodes[target_value]
        for value in self.nodes:
            node = self.nodes[value]
            if target_node in node.neighbor:
                index = node.neighbor.index(target_node)
                del node.neighbor[index]
                del node.weight[index]
        del self.nodes[target_value]

    def gfs(self, node, visit_flag):
        if node not in visit_flag:
            print(node.value)
            visit_flag.add(node)
        for n, w in zip(node.neighbor, node.weight):
            if n in visit_flag:
                continue
            self.gfs(n, visit_flag)

    def bfs(self, node_list, visit_flag):
        new_node_list = list()
        for node in node_list:
            if node not in visit_flag:
                print(node.value)
                visit_flag.add(node)
            for n, w in zip(node.neighbor, node.weight):
                if n in visit_flag:
                    continue
                new_node_list += node.neighbor
        if new_node_list:
            self.bfs(new_node_list, visit_flag)

    def gfs_traversal(self):
        # 如果图只是一个任意选出的始顶点，那一般才有遍历的意义，假如是我写的这种，所有顶点已经被记录在nodes中，似乎不需要遍历了
        # 但路径仍然有问题，例如计算最小权重路径
        # 所以对于图来说，遍历的目的不是获取全部顶点，而是画出一条沟通全部顶点的路径线，也就是全部的边

        visit_flag = set()
        # 如果是有向图，存在一个只指向别的顶点，但没有顶点指向自己的顶点，就可以通过self.nodes找到
        # 也只有无向图可以任意画出一条连接全部结点的点，如果是有向图，情况就多了
        for value in self.nodes:
            node = self.nodes[value]
            self.gfs(node, visit_flag)

    def bfs_traversal(self):
        visit_flag = set()
        for value in self.nodes:
            node = self.nodes[value]
            self.bfs([node], visit_flag)

    def vis(self):
        for value in self.nodes:
            node = self.nodes[value]
            print(node.value, [n.value for n in node.neighbor], node.weight)


def main():
    # 值
    value_list = [1, 2, 3, 4]
    # 边
    arc_list = [[2, 4], [1, 3], [2, 4], [1, 3]]
    # 权重关系
    weight_list = [[2, 4], [1, 3], [2, 4], [1, 3]]

    # 无向图的实现

    # 创建图：本质上是顶点的列表，为了方便跟值对应，用字典
    graph = Graph(value_list, arc_list, weight_list)
    # graph.vis()
    # 添加一个结点
    value = 5
    arcs = [2, 4]
    # arcs = [2, 4, 7]
    weights = [2, 4]
    graph.add(value, arcs, weights)
    # graph.vis()
    # 删除操作
    value = 3
    graph.delete(value)
    graph.vis()
    # 深度优先遍历
    # graph.gfs_traversal()
    # 广度优先遍历
    graph.bfs_traversal()


if __name__ == '__main__':
    main()