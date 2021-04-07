# coding=utf-8
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.father = None
        self.bf = 0

    def __str__(self):
        return str(self.value)


class AVL:
    def __init__(self, value=None):
        if value:
            self.root = Node(value)
        else:
            self.root = None
    # def _insert_change_bf(self, node):
    #     # 修改bf值，只会影响父结点-根结点这一条线上的结点
    #     unbalance_nodes = list()
    #     while node.father:
    #         if node.father.left == node:
    #             node.father.bf += 1
    #         else:
    #             node.father.bf -= 1
    #         if node.father.bf not in [-1, 0, 1]:
    #             unbalance_nodes.append(node.father)
    #         node = node.father
    #         print(node.value, node.bf)
    #     return unbalance_nodes

    def _change_all_bf(self, node, unbalance_nodes):
        # 修改node结点下面的所有结点的bf值
        if node.left:
            left_height = 1 + self._change_all_bf(node.left, unbalance_nodes)
        else:
            left_height = 0
        if node.right:
            right_height = 1 + self._change_all_bf(node.right, unbalance_nodes)
        else:
            right_height = 0
        node.bf = left_height - right_height
        if node.bf not in [-1, 0, 1]:
            unbalance_nodes.append(node)
        # print(f'node: {node.value}, bf: {node.bf}, left_height: {left_height}, right_height: {right_height}')
        return max(left_height, right_height)

    # 删除查找
    def _delete_find(self, node, type_):
        if type_ == 'min':
            if node.left:
                return self._delete_find(node.left, 'min')
            else:
                return node, node.value
        else:
            if node.right:
                return self._delete_find(node.right, 'max')
            else:
                return node, node.value

    # 旋转算法
    def spin_tree(self, insert_node, unbalance_node):
        # 判断旋转类型需要三个结点：插入结点，插入结点的父结点，以及不平衡结点
        if insert_node.value < unbalance_node.value:
            if insert_node.value < unbalance_node.left.value:
                type_ = 'll'
            else:
                type_ = 'lr'
        else:
            if insert_node.value < unbalance_node.right.value:
                type_ = 'rl'
            else:
                type_ = 'rr'
        # print(insert_node.value, unbalance_node.value, type_)
        if type_ == 'll':
            left_kid = unbalance_node.left
            node_father = unbalance_node.father
            unbalance_node.left = left_kid.right
            left_kid.right = unbalance_node
            unbalance_node.father = left_kid
            if node_father is None:
                self.root = left_kid
            elif node_father.left is unbalance_node:
                left_kid.father = node_father
                node_father.left = left_kid
            else:
                left_kid.father = node_father
                node_father.right = left_kid
        elif type_ == 'rr':
            right_kid = unbalance_node.right
            node_father = unbalance_node.father
            unbalance_node.right = right_kid.left
            right_kid.left = unbalance_node
            unbalance_node.father = right_kid
            if node_father is None:
                self.root = right_kid
            elif node_father.left is unbalance_node:
                right_kid.father = node_father
                node_father.left = right_kid
            else:
                right_kid.father = node_father
                node_father.right = right_kid
        elif type_ == 'lr':
            # 被拆分的结点
            split_node = unbalance_node.left.right
            left_kid = split_node.left
            right_kid = split_node.right

            unbalance_node_left = unbalance_node.left
            unbalance_node_left.right = left_kid
            if left_kid:
                left_kid.father = unbalance_node_left

            unbalance_node.left = right_kid
            if right_kid:
                right_kid.father = unbalance_node

            split_node.left = unbalance_node_left
            split_node.right = unbalance_node
            unbalance_node_left.father = split_node
            if unbalance_node.father is None:
                self.root = split_node
            else:
                split_node.father = unbalance_node.father
                unbalance_node.father = split_node

        else:
            # 被拆分的结点
            split_node = unbalance_node.right.left
            left_kid = split_node.left
            right_kid = split_node.right

            unbalance_node_right = unbalance_node.right
            unbalance_node_right.left = right_kid
            if right_kid:
                left_kid.father = unbalance_node_right

            unbalance_node.right = left_kid
            if left_kid:
                left_kid.father = unbalance_node

            split_node.left = unbalance_node
            split_node.right = unbalance_node_right
            unbalance_node_right.father = split_node
            if unbalance_node.father is None:
                self.root = split_node
            else:
                split_node.father = unbalance_node.father
                unbalance_node.father = split_node

    # 插入
    def insert(self, value):
        if not self.root:
            self.root = Node(value)
            return self.root
        node = self.root
        while node is not None:
            node_father = node
            if node.value >= value:
                node = node.left
            else:
                node = node.right
        node = Node(value)
        node.father = node_father
        if node_father.value <= value:
            node_father.right = node
        else:
            node_father.left = node
        
        # 修改bf值，并检查是否导致不平衡
        # unbalance_nodes = self._insert_change_bf(node)
        unbalance_nodes = list()
        self._change_all_bf(self.root, unbalance_nodes)
        if unbalance_nodes:
            print([i.value for i in unbalance_nodes])
            self.spin_tree(node, unbalance_nodes[0])
        # 为了便于验证删除操作，返回插入的node对象
        return node

    # 删除
    def delete(self, node):
        # 找到被删除的叶子结点和值
        if node.left is not None:
            leaf_node, value = self._delete_find(node.left, 'max')
        elif node.right is not None:
            leaf_node, value = self._delete_find(node.right, 'min')
        else:
            leaf_node, value = node, None

        # 偷个懒，找父结点不写了，直接改成属性
        # 将叶子结点的值赋给被删除的目标结点
        # 删除的是root
        if node.father is None:
            if value is None:
                self.root = None
            elif leaf_node.left:
                self.root.value = leaf_node.value
                self.root.left = leaf_node.left
            else:
                self.root.value = leaf_node.value
                self.root.left = leaf_node.right
        # 删除的是父结点的左子结点
        elif node == node.father.left:
            if value is None:
                node.father.left = None
            elif leaf_node.left:
                node.father.left = leaf_node.left
            elif leaf_node.right:
                node.father.left = leaf_node.right
            else:
                node.value = value
                self.delete(leaf_node)
        # 删除的是父结点的右子结点
        else:
            if value is None:
                node.father.right = None
            elif leaf_node.left:
                node.father.right = leaf_node.left
            elif leaf_node.right:
                node.father.right = leaf_node.right
            else:
                node.value = value
                self.delete(leaf_node)

        # 删除后检查bf值，如果有不平衡结点，待测试
        unbalance_nodes = list()
        self._change_all_bf(self.root, unbalance_nodes)
        if unbalance_nodes:
            print([i.value for i in unbalance_nodes])
            self.spin_tree(node, unbalance_nodes[0])

    def level_print(self, node_list):
        next_node_list = list()
        for node in node_list[-1]:
            if node is None:
                next_node_list += [None, None]
            else:
                next_node_list += [node.left, node.right]
        if any(next_node_list):
            node_list.append(next_node_list)
            self.level_print(node_list)
        else:
            return node_list

    def vis_tree(self):
        node_list = [[self.root]]
        self.level_print(node_list)

        split_char = ' '
        split_part = 5
        none_char = '*'

        tree_str = list()
        for level_index, nodes in enumerate(node_list[::-1]):
            if level_index == 0:
                start_part = 0
            else:
                start_part = 6*(2**(level_index-1) - 1) + 3

            if nodes[0]:
                level_str = start_part*split_char + str(nodes[0])
            else:
                level_str = start_part*split_char + none_char
            for i in nodes[1:]:
                if i:
                    level_str += split_char*(split_part - len(str(i)) + 1) + str(i)
                else:
                    level_str += split_char*split_part + none_char
            tree_str.append(level_str)
            split_part = split_part + (split_part + 1) // 2 * 2
        print('----------------------------------------------------')
        for line in tree_str[::-1]:
            print(line)


if __name__ == '__main__':
    data = [5, 4, 8, 3, 4.5]
    tree = AVL()

    value_node_mapping = dict()
    for i in data:
        node = tree.insert(i)
        value_node_mapping[node.value] = node
    tree.vis_tree()

    # 测试 ll
    # tree.insert(3.5)
    # tree.vis_tree()
    # 测试 rr
    # tree.insert(9)
    # tree.vis_tree()
    # tree.insert(10)
    # tree.vis_tree()
    # 测试lr
    # tree.insert(4.7)
    # tree.vis_tree()
    # 测试rl
    tree.delete(value_node_mapping[3])
    tree.delete(value_node_mapping[4.5])
    tree.insert(7.5)
    tree.vis_tree()
    tree.insert(9)
    tree.vis_tree()
    tree.insert(7.2)
    tree.vis_tree()

    # 测试删除