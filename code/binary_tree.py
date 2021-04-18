class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
    def __str__(self):
        return str(self.value)

class Tree:
    # 构建二叉树
    def __init__(self, value=None):
        if value:
            self.root = Node(value)
        else:
            self.root = None
    # 添加元素
    def add_note(self, value):
        note = Node(value)
        if not self.root:
            self.root = note
        else:
            nodes = [self.root]
            while True:
                n_node = nodes.pop()
                if n_node.left is None:
                    n_node.left = node
                    break
                elif n_node.right is None:
                    n_node.right = node
                    break
                else:
                    nodes.append(n_node.left)
                    nodes.append(n_node.right)
    def get_parent(self, item):
        # 找到item的父节点
        if self.root.data == item:
            return None
        q = [self.root]
        while q:
            pop_node = q.pop(0)
            if pop_node.left and pop_node.left.data == item:
                return pop_node
            elif pop_node.right and pop_node.right.data == item:
                return pop_node
            else:
                if pop_node.left is not None:
                    q.append(pop_node.left)
                if pop_node.right is not None:
                    q.append(pop_node.right)
                return None
    # 删除
    def delete(self, item):
        '''
        从二叉树中删除一个元素
        先获取 待删除节点 item 的父节点
        如果父节点不为空，
            判断 item 的左右子树
            如果左子树为空，那么判断 item 是父节点的左孩子，还是右孩子，如果是左孩子，将父节点的左指针指向 item 的右子树，反之将父节点的右指针指向 item 的右子树
            如果右子树为空，那么判断 item 是父节点的左孩子，还是右孩子，如果是左孩子，将父节点的左指针指向 item 的左子树，反之将父节点的右指针指向 item 的左子树
            如果左右子树均不为空，寻找右子树中的最左叶子节点 x ，将 x 替代要删除的节点。
        删除成功，返回 True
        删除失败, 返回 False

        '''
        if self.root is None:  # 如果根为空，就什么也不做
            return False

        parent = self.get_parent(item)
        if parent:
            del_node = parent.left if parent.left.data == item else parent.right  # 待删除节点
            if del_node.left is None:
                if parent.left.data == item:
                    parent.left = del_node.right
                else:
                    parent.right = del_node.right
                    del del_node
                    return True
            elif del_node.right is None:
                if parent.left.data == item:
                        parent.left = del_node.left
                else:
                    parent.right = del_node.left
                    del del_node
                    return True
            else:  # 左右子树都不为空
                tmp_pre = del_node
                tmp_next = del_node.right
                if tmp_next.left is None:
                    # 替代
                    tmp_pre.right = tmp_next.right
                    tmp_next.left = del_node.left
                    tmp_next.right = del_node.right
                else:
                    while tmp_next.left:  # 让tmp指向右子树的最后一个叶子
                        tmp_pre = tmp_next
                        tmp_next = tmp_next.left
                        # 替代
                        tmp_pre.left = tmp_next.right
                        tmp_next.left = del_node.left
                        tmp_next.right = del_node.right
                        if parent.left.data == item:
                            parent.left = tmp_next
                        else:
                            parent.right = tmp_next
                            del del_node
                            return True
        else:
            return False
