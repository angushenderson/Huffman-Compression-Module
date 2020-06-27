class Tree:
    """ Object for representing tree data structure """
    def __init__(self, symbol, frequency=None, left=None, right=None):
        """
        :param symbol: character the node in the tree represents
        :param frequency: frequency of that character - symbol
        :param left: left subtree
        :param right: right subtree
        """
        self.symbol = symbol
        self.frequency = frequency
        self.left = left
        self.right = right
        self.depth = None

    def __str__(self):
        return str(self.symbol)


def print_tree_indented(tree: Tree, level=0):
    """
    Method for displaying a tree indented from with root at the left and leaves to the right
    :param tree: tree to be displayed
    :param level: leave blank, for method computation
    """
    if tree is None:
        return 
    print_tree_indented(tree.right, level+1)
    if tree.symbol == None:
        print("      " * level + str(tree.frequency))
    else:
        if tree.symbol in ['\n', '\r', '\t', '\b', '\f']:
            print("      " * level + 'escape character , ' + str(tree.frequency))
        else:
            print("      " * level + str(tree.symbol), ',', str(tree.frequency))
    print_tree_indented(tree.left, level+1)


def get_tree_preorder(tree, preorder=''):
    """
    Returns a string of the given tree in preorder
    :param tree: Tree object to traverse
    :param preorder: Leave blank, for function computation
    :return preorder: String of tree in preorder
    """
    if tree is None:
        return preorder
    preorder = get_tree_preorder(tree.left, preorder)
    # Payload here
    if tree.symbol:
        preorder += "1" + str(tree.symbol)
    else:
        preorder += "0"
    preorder = get_tree_preorder(tree.right, preorder)
    return preorder


def get_tree_postorder(tree, postorder=''):
    """
    Returns a string of the given tree in postorder
    This is what is used in the compression algorithm and what is stored in the
    file header
    :param tree: Tree object to traverse
    :param postorder: Leave blank, for function computation
    :return postorder: String of the tree in postorder
    """
    if tree is None:
        return postorder
    postorder = get_tree_postorder(tree.left, postorder)
    postorder = get_tree_postorder(tree.right, postorder)
    if tree.symbol != None:
        # Represents a leaf node
        postorder += "1" + str(tree.symbol)
    else:
        # Represents an internal node
        postorder += "0"
    return postorder


def construct_tree_from_postorder(postorder: list) -> Tree:
    """
    Generate a binary tree from postorder list
    :param postorder: 
    :return stack[0]: 
    """
    # Make use of stacks to complete this operation
    stack = []
    if sum(isinstance(i, str) for i in postorder) == 1:
        # There is only 1 leaf in the tree
        return Tree(None, None, Tree(postorder[0]), None)
    
    else:
        # Multiple leafs to build
        for node in postorder:
            if type(node) == str:
                # Push character to the top of the stack
                stack.append(node)
            elif node == None:
                if len(stack) == 1:
                    # Tree has been fully constructed
                    return stack[0]
                else:
                    # Merge nodes and put back into stack
                    new_node = Tree(None, None, Tree(stack[-2]) if type(stack[-2]) == str else stack[-2], 
                                                Tree(stack[-1]) if type(stack[-1]) == str else stack[-1])
                    del stack[-2:]
                    stack.append(new_node)

def tree_depth(tree):
    """
    Calculate the number of layers in the tree
    :param tree: Root tree object
    :return int: depth of the tree
    """
    if tree is None:
        return 0
    else:
        # Compute the depth of each subnode
        left_depth = tree_depth(tree.left)
        right_depth = tree_depth(tree.right)

        # Return the larger value
        return left_depth + 1 if left_depth > right_depth else right_depth + 1
