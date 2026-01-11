from collections import deque

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    # --- INSERTION (Level Order) ---
    def insert(self, value):
        new_node = Node(value)
        if not self.root:
            self.root = new_node
            return

        # Use a queue to find the first empty spot
        queue = deque([self.root])
        while queue:
            temp = queue.popleft()

            if not temp.left:
                temp.left = new_node
                return
            else:
                queue.append(temp.left)

            if not temp.right:
                temp.right = new_node
                return
            else:
                queue.append(temp.right)

    # --- 1. PRE-ORDER TRAVERSAL (Root -> Left -> Right) ---
    def preorder(self, node=None, result=None):
        if result is None:
            result = []
            node = self.root # Start at root if called without arguments
        
        if node:
            result.append(node.value)
            self.preorder(node.left, result)
            self.preorder(node.right, result)
        return result

    # --- 2. IN-ORDER TRAVERSAL (Left -> Root -> Right) ---
    def inorder(self, node=None, result=None):
        if result is None:
            result = []
            node = self.root
            
        if node:
            self.inorder(node.left, result)
            result.append(node.value)
            self.inorder(node.right, result)
        return result

    # --- 3. POST-ORDER TRAVERSAL (Left -> Right -> Root) ---
    def postorder(self, node=None, result=None):
        if result is None:
            result = []
            node = self.root
            
        if node:
            self.postorder(node.left, result)
            self.postorder(node.right, result)
            result.append(node.value)
        return result

    # --- 4. LEVEL-ORDER TRAVERSAL (Breadth-First) ---
    def level_order(self):
        if not self.root:
            return []
            
        result = []
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            result.append(node.value)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
                
        return result