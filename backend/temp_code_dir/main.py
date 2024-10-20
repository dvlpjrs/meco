
from typing import Any, Optional

class MyNode:
    def __init__(self, data: Any):
        self.data = data
        self.left = None
        self.right = None
        self.height = 1

    def get_data(self) -> Any:
        return self.data

    def get_left(self) -> 'MyNode | None':
        return self.left

    def get_right(self) -> 'MyNode | None':
        return self.right

    def set_left(self, node: 'MyNode | None') -> None:
        self.left = node

    def set_right(self, node: 'MyNode | None') -> None:
        self.right = node

    def set_height(self, height: int) -> None:
        self.height = height

    def get_height(self) -> int:
        return self.height

def get_height(node: MyNode | None) -> int:
    if node is None:
        return 0
    return node.get_height()

def my_max(a: int, b: int) -> int:
    if a > b:
        return a
    return b

def right_rotation(node: MyNode) -> MyNode:
    ret = node.get_left()
    assert ret is not None
    node.set_left(ret.get_right())
    ret.set_right(node)
    node.set_height(my_max(get_height(node.get_right()), get_height(node.get_left())) + 1)
    ret.set_height(my_max(get_height(ret.get_right()), get_height(ret.get_left())) + 1)
    return ret

def left_rotation(node: MyNode) -> MyNode:
    ret = node.get_right()
    assert ret is not None
    node.set_right(ret.get_left())
    ret.set_left(node)
    node.set_height(my_max(get_height(node.get_right()), get_height(node.get_left())) + 1)
    ret.set_height(my_max(get_height(ret.get_right()), get_height(ret.get_left())) + 1)
    return ret

def lr_rotation(node: MyNode) -> MyNode:
    left_child = node.get_left()
    assert left_child is not None
    node.set_left(left_rotation(left_child))
    return right_rotation(node)

def rl_rotation(node: MyNode) -> MyNode:
    right_child = node.get_right()
    assert right_child is not None
    node.set_right(right_rotation(right_child))
    return left_rotation(node)

def insert_node(node: MyNode | None, data: Any) -> MyNode | None:
    if node is None:
        return MyNode(data)
    if data < node.get_data():
        node.set_left(insert_node(node.get_left(), data))
        if get_height(node.get_left()) - get_height(node.get_right()) == 2:
            left_child = node.get_left()
            assert left_child is not None
            if data < left_child.get_data():
                node = right_rotation(node)
            else:
                node = lr_rotation(node)
    else:
        node.set_right(insert_node(node.get_right(), data))
        if get_height(node.get_right()) - get_height(node.get_left()) == 2:
            right_child = node.get_right()
            assert right_child is not None
            if data < right_child.get_data():
                node = rl_rotation(node)
            else:
                node = left_rotation(node)
    node.set_height(my_max(get_height(node.get_right()), get_height(node.get_left())) + 1)
    return node

# Sample inputs to test
def print_tree(node: Optional[MyNode], level=0):
    if node is not None:
        print_tree(node.get_right(), level + 1)
        print(' ' * 4 * level + '->', node.get_data())
        print_tree(node.get_left(), level + 1)

root = None
root = insert_node(root, 10)
root = insert_node(root, 5)
root = insert_node(root, 15)
root = insert_node(root, 20)
print_tree(root)
