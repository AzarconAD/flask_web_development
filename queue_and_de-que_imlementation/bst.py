
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        # layout properties (filled in by layout())
        self._x = None
        self._y = None
        self._id = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        """Insert a value into the BST."""
        if self.root is None:
            self.root = Node(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = Node(value)
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = Node(value)
            else:
                self._insert_recursive(node.right, value)

    def display(self, node=None, level=0):
        """Return a text-based rotated tree structure (for debugging)."""
        if node is None:
            node = self.root
        if node is None:
            return ""

        result = ""
        if node.right:
            result += self.display(node.right, level + 1)

        result += "    " * level + f"{node.value}\n"

        if node.left:
            result += self.display(node.left, level + 1)

        return result

    # -------------------------
    # SVG layout generation
    # -------------------------
    def layout(self, h_spacing=80, v_spacing=90, node_radius=18):
        """
        Compute simple layout positions for each node using an inorder x-spacing
        and depth-based y. Returns:
          nodes: list of dicts {id, value, x, y}
          edges: list of dicts {from: parent_id, to: child_id}
          svg_size: dict {width, height}
        """
        if self.root is None:
            return [], [], {"width": 400, "height": 200, "node_radius": node_radius}

        # assign ids and compute inorder x positions
        x_counter = {"x": 0}
        nodes = []
        edges = []

        def inorder_assign(node, depth):
            if node is None:
                return
            inorder_assign(node.left, depth + 1)
            # assign id and x/y
            node._id = len(nodes) + 1  # temporary sequential id (pre-append)
            node._x = x_counter["x"] * h_spacing
            node._y = depth * v_spacing
            nodes.append(node)
            x_counter["x"] += 1
            inorder_assign(node.right, depth + 1)

        # But the above appends nodes while visiting; we must ensure left and right edges refer to ids.
        # A two-pass approach: first compute x positions using a separate traversal that builds order, then assign ids.
        # We'll do clearer two-pass below.

        # First pass: compute x order count via inorder traversal without storing nodes list
        x_counter = {"x": 0}
        max_depth = {"d": 0}

        def inorder_count(node, depth):
            if node is None:
                return
            inorder_count(node.left, depth + 1)
            # set temporary attributes
            node._temp_x_index = x_counter["x"]
            x_counter["x"] += 1
            if depth > max_depth["d"]:
                max_depth["d"] = depth
            node._temp_depth = depth
            inorder_count(node.right, depth + 1)

        inorder_count(self.root, 0)

        # Second pass: collect nodes in any order but with positions
        id_counter = {"i": 1}
        def assign_ids_and_positions(node):
            if node is None:
                return
            # assign for this node
            node._id = id_counter["i"]
            id_counter["i"] += 1
            node._x = node._temp_x_index * h_spacing
            node._y = node._temp_depth * v_spacing
            # recurse to assign children
            if node.left:
                assign_ids_and_positions(node.left)
            if node.right:
                assign_ids_and_positions(node.right)

        assign_ids_and_positions(self.root)

        # Now produce nodes list in order of their _id so stable output
        def collect_nodes(node, out):
            if node is None:
                return
            out.append({
                "id": node._id,
                "value": node.value,
                "x": node._x,
                "y": node._y
            })
            collect_nodes(node.left, out)
            collect_nodes(node.right, out)

        nodes_out = []
        collect_nodes(self.root, nodes_out)

        # Build edges (parent -> child) by walking tree
        edges_out = []
        def collect_edges(node):
            if node is None:
                return
            if node.left:
                edges_out.append({"from": node._id, "to": node.left._id})
                collect_edges(node.left)
            if node.right:
                edges_out.append({"from": node._id, "to": node.right._id})
                collect_edges(node.right)
        collect_edges(self.root)

        # compute svg canvas size
        total_columns = x_counter["x"]
        width = max(400, total_columns * h_spacing + h_spacing)
        height = max(200, (max_depth["d"] + 1) * v_spacing + v_spacing)

        return nodes_out, edges_out, {"width": width, "height": height, "node_radius": node_radius}
    
    def search(self, root, key):
        if root is None:
            return None
        if root.value == key:
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
    
    def delete_node(self, root, key):
        if root is None:
            return root

        # Step 1: search for the node
        if key < root.value:
            root.left = self.delete_node(root.left, key)
        elif key > root.value:
            root.right = self.delete_node(root.right, key)
        else:
            # Case A: no child
            if root.left is None and root.right is None:
                return None

            # Case B: one child
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left

            # Case C: two children → find inorder successor
            successor = root.right
            while successor.left:
                successor = successor.left

            # replace root value with successor value
            root.value = successor.value

            # delete successor
            root.right = self.delete_node(root.right, successor.value)

        return root

