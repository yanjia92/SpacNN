# -*- coding: utf-8 -*-

'''
TreeNode:
    object
    left
    right
'''

def BT_level_traverse(root):
    '''
    水平遍历
    :param root:
    :return: None
    '''
    result = list()
    queue = list()
    queue.append(root)
    while len(queue) > 0:
        top = queue.pop(0)
        result.append(top.object)
        left = top.left
        right = top.right
        if left:
            queue.append(left)
        if right:
            queue.append(right)
    return result