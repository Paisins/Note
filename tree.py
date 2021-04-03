# coding=utf-8
# 二叉搜索树
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.father = None
    def __str__(self):
        return str(self.value)

class BST:
    def __init__(self, value=None):
        if value:
            self.root = Node(value)
        else:
            self.root = None
    def compare(node, value):
        if not node:
            return None
        if node.value == value:
            return self.root
        elif node.value < value:
            return f(node.left, value)
        else:
            return f(node.right, value)
    # 遍历
    def serach(self, value):
        return self.compare(self.root, value)
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
        # print(node_father.value, node.value)
        # 为了便于验证删除操作，返回插入的node对象
        return node
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

    # 删除
    def delete(self, node):
        # 找到被删除的叶子结点和值
        if node.left:
            leaf_node, value = self._delete_find(node.left, 'max')
        elif node.right:
            leaf_node, value = self._delete_find(node.left, 'min')
        else:
            leaf_node, value = node, None

        # 偷个懒，找父结点不写了，直接改成属性
        # 将叶子结点的值赋给被删除的目标结点
        # 删除的是root
        if node.father is None:
            if value is None:
                self.root = None
            else:
                self.root.value = value
        # 删除的是父结点的左子结点
        elif node == node.father.left:
            if value is None:
                node.father.left = None
            else:
                node.father.left.value = value
        # 删除的是父结点的右子结点
        else:
            if value is None:
                node.father.right = None
            else:
                node.father.right.value = value

        # 判断是叶子结点完成删除
        if node.left is None and node.right is None:
            return
        else:
            self.delete(leaf_node)
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
        node = self.root
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
                if i :
                    level_str += split_char*(split_part - len(str(i)) + 1) + str(i)
                else:
                    level_str += split_char*split_part + none_char
            tree_str.append(level_str)
            split_part = split_part + (split_part + 1) // 2 * 2
        print('----------------------------------------------------')
        for line in tree_str[::-1]:
            print(line)


if __name__ == '__main__':
    data = [10, 5, 20, 0, 7, 15, 25, 12 ,17, 22, 30]
    # data = list(range(5))
    tree = BST()

    value_node_mapping = dict()
    for i in data:
        node = tree.insert(i)
        value_node_mapping[node.value] = node
    tree.vis_tree()
    # 测试一
    # tree.delete(value_node_mapping[12])
    # tree.delete(value_node_mapping[17])
    # 测试二
    # tree.delete(value_node_mapping[20])
    # 测试三
    tree.insert(3)
    tree.vis_tree()
    tree.delete(value_node_mapping[7])
    tree.vis_tree()
    tree.delete(value_node_mapping[10])
    tree.vis_tree()
    # tree.delete(value_node_mapping[10])
    # tree.vis_tree()