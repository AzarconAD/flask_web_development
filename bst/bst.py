from flask import Blueprint, render_template, request

bst_bp = Blueprint('bst_bp', __name__)

#   LOGIC CLASSES
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, root, key):
        if root is None:
            return Node(key)
        if key < root.value:
            root.left = self.insert(root.left, key)
        else:
            root.right = self.insert(root.right, key)
        return root

    def search(self, root, key):
        if root is None:
            return None
        if key == root.value:
            return root
        elif key < root.value:
            return self.search(root.left, key)
        else:
            return self.search(root.right, key)

    def post_traversal(self, start, traversal):
        if start:
            self.post_traversal(start.left, traversal)
            self.post_traversal(start.right, traversal)
            traversal.append(start.value)
        return traversal

# Init a global tree instance
tree = BST()

#   HELPER FUNCTIONS
def build_tree_data(node, x, y, level, nodes, edges):
    if not node: return
    offset = max(200 // (2 ** (level-1)) if level > 1 else 200, 40)
    
    nodes.append({'id': node.value, 'value': node.value, 'x': x, 'y': y})

    if node.left:
        edges.append({'from': node.value, 'to': node.left.value})
        build_tree_data(node.left, x - offset, y + 80, level + 1, nodes, edges)

    if node.right:
        edges.append({'from': node.value, 'to': node.right.value})
        build_tree_data(node.right, x + offset, y + 80, level + 1, nodes, edges)

def get_text_tree(node, prefix="", is_left=True):
    if not node: return ""
    result = ""
    if node.right:
        result += get_text_tree(node.right, prefix + ("│   " if is_left else "    "), False)
    result += prefix + ("└── " if is_left else "┌── ") + str(node.value) + "\n"
    if node.left:
        result += get_text_tree(node.left, prefix + ("    " if is_left else "│   "), True)
    return result

def render_view(highlight=None):
    traversal_list = tree.post_traversal(tree.root, [])
    nodes = []
    edges = []
    build_tree_data(tree.root, 400, 40, 1, nodes, edges)
    
    return render_template(
        'index.html',
        nodes=nodes,
        edges=edges,
        svg_info={'width': 800, 'height': 600, 'node_radius': 20},
        post_order=traversal_list,
        tree_visual=get_text_tree(tree.root),
        highlight=highlight
    )


#   ROUTES (Defined here)
@bst_bp.route("/", methods=["GET"])
def index():
    return render_view()

@bst_bp.route("/insert", methods=["POST"])
def insert_node():
    try:
        val = int(request.form["value"])
        tree.root = tree.insert(tree.root, val)
    except ValueError:
        pass
    return render_view()

@bst_bp.route("/search", methods=["POST"])
def search_node():
    highlight_val = None
    try:
        val = int(request.form["value"])
        found = tree.search(tree.root, val)
        if found:
            highlight_val = val
    except ValueError:
        pass
    return render_view(highlight=highlight_val)