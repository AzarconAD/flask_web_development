W = 64
B = int(W**(1/5)) # branching factor (like in B-trees, can tune)
# With W=64, B=2. This means each node holds at most 2 keys.

class FusionNode:
    def __init__(self, leaf=True):
        self.keys = []          # stores INTEGER values
        self.children = []      # pointers to children
        self.leaf = leaf        # True if leaf node
        self.n = 0              # number of keys


def split_child(parent, i, y):
    """Split the full child y of parent at index i"""
    z = FusionNode(leaf=y.leaf)
    mid = B // 2
    parent.keys.insert(i, y.keys[mid])
    z.keys = y.keys[mid+1:]
    y.keys = y.keys[:mid]
    if not y.leaf:
        z.children = y.children[mid+1:]
        y.children = y.children[:mid+1]
    parent.children.insert(i+1, z)
    y.n = len(y.keys)
    z.n = len(z.keys)
    parent.n = len(parent.keys)

class FusionTree:
    def __init__(self):
        self.root = FusionNode()

    def _find_rank_in_node(self, key, node):
        """
        Simulates a constant-time search for the key's rank within a single node.
        """
    
        if node.n > B:
            rank = 0
            for k in node.keys:
                if k <= key:
                    rank += 1
            return rank
        if node.n == 0:
            return 0
        bits_per_key = W // B
        packed_keys = 0
        for i in range(node.n):
            packed_keys |= node.keys[i] << (i * bits_per_key)
        query_mask = 0
        for i in range(B):
            query_mask |= key << (i * bits_per_key)
        high_bits_mask = 0
        for i in range(B):
            high_bits_mask |= 1 << ((i * bits_per_key) + bits_per_key - 1)
        diff = query_mask - packed_keys
        borrows = diff & high_bits_mask
        num_keys_greater_than_key = bin(borrows).count('1')
        rank = node.n - num_keys_greater_than_key
        return rank

    def _insert_non_full(self, node, key):
        """Insert key into a non-full node using O(1) rank finding."""
        i = self._find_rank_in_node(key, node)
        if node.leaf:
            node.keys.insert(i, key)
            node.n += 1
        else:
            if len(node.children[i].keys) == B:
                split_child(node, i, node.children[i])
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)
    
    def insert(self, key):
        r = self.root
        if len(r.keys) == B:
            s = FusionNode(leaf=False)
            s.children.append(r)
            self.root = s
            split_child(s, 0, r)
            self._insert_non_full(s, key)
        else:
            self._insert_non_full(r, key)

    def _search_recursive(self, node, key):
        """Helper for search using O(1) rank finding."""
        rank = self._find_rank_in_node(key, node)
        index = rank - 1

        if index >= 0 and index < node.n and node.keys[index] == key:
            return True
        
        if node.leaf:
            return False
        
        # Child to descend into is at index 'rank'
        if rank < len(node.children):
             return self._search_recursive(node.children[rank], key)
        return False


    def search(self, key):
        return self._search_recursive(self.root, key)

    def delete(self, key):
        """Public method to delete a key from the tree."""
        if not self.search(key):
            print(f"Element {key} not found in the tree.")
            return

        self._delete_recursive(self.root, key)

        if len(self.root.keys) == 0 and not self.root.leaf and self.root.children:
            self.root = self.root.children[0]

    def _delete_recursive(self, node, key):
        """Recursive delete helper that uses O(1) intra-node search."""
        min_keys = B // 2
        rank = self._find_rank_in_node(key, node)
        index = rank - 1

        # Case 1: Key is present at this node
        if index >= 0 and index < node.n and node.keys[index] == key:
            if node.leaf:
                node.keys.pop(index)
                node.n -= 1
            else:
                self._delete_from_internal_node(node, index)
        # Case 2: Key is not in this node, recurse down
        else:
            if node.leaf:
                return

            child_idx = rank
            is_last_child = (child_idx == node.n)
            
            if child_idx < len(node.children) and node.children[child_idx].n < min_keys + 1:
                self._fill_child(node, child_idx)

            if is_last_child and child_idx > node.n:
                self._delete_recursive(node.children[child_idx - 1], key)
            else:
                 if child_idx < len(node.children):
                    self._delete_recursive(node.children[child_idx], key)
    
    def _delete_from_internal_node(self, node, key_idx):
        min_keys = B // 2
        key = node.keys[key_idx]
        if node.children[key_idx].n > min_keys:
            pred = self._get_predecessor(node.children[key_idx])
            node.keys[key_idx] = pred
            self._delete_recursive(node.children[key_idx], pred)
        elif key_idx + 1 < len(node.children) and node.children[key_idx + 1].n > min_keys:
            succ = self._get_successor(node.children[key_idx + 1])
            node.keys[key_idx] = succ
            self._delete_recursive(node.children[key_idx + 1], succ)
        else:
            self._merge_children(node, key_idx)
            self._delete_recursive(node.children[key_idx], key)

    def _get_predecessor(self, node):
        current = node
        while not current.leaf:
            # The predecessor is the rightmost key in the left subtree.
            # The child index for the rightmost path is 'current.n'
            current = current.children[current.n]
        return current.keys[-1]

    def _get_successor(self, node):
        current = node
        while not current.leaf:
            current = current.children[0]
        return current.keys[0]

    def _fill_child(self, parent_node, child_idx):
        min_keys = B // 2
        if child_idx != 0 and parent_node.children[child_idx - 1].n > min_keys:
            self._borrow_from_prev(parent_node, child_idx)
        elif child_idx != parent_node.n and parent_node.children[child_idx + 1].n > min_keys:
            self._borrow_from_next(parent_node, child_idx)
        else:
            if child_idx != parent_node.n:
                self._merge_children(parent_node, child_idx)
            else:
                self._merge_children(parent_node, child_idx - 1)

    def _borrow_from_prev(self, parent_node, child_idx):
        child = parent_node.children[child_idx]
        sibling = parent_node.children[child_idx - 1]
        child.keys.insert(0, parent_node.keys[child_idx - 1])
        parent_node.keys[child_idx - 1] = sibling.keys.pop()
        if not sibling.leaf:
            child.children.insert(0, sibling.children.pop())
        child.n += 1
        sibling.n -= 1

    def _borrow_from_next(self, parent_node, child_idx):
        child = parent_node.children[child_idx]
        sibling = parent_node.children[child_idx + 1]
        child.keys.append(parent_node.keys[child_idx])
        parent_node.keys[child_idx] = sibling.keys.pop(0)
        if not sibling.leaf:
            child.children.append(sibling.children.pop(0))
        child.n += 1
        sibling.n -= 1

    def _merge_children(self, parent_node, idx):
        child = parent_node.children[idx]
        sibling = parent_node.children[idx + 1]
        child.keys.append(parent_node.keys.pop(idx))
        child.keys.extend(sibling.keys)
        if not child.leaf:
            child.children.extend(sibling.children)
        parent_node.children.pop(idx + 1)
        parent_node.n -= 1
        child.n = len(child.keys)

    def get_min(self):
        node = self.root
        while not node.leaf:
            node = node.children[0]
        return node.keys[0] if node.keys else None

    def is_empty(self):
        return len(self.root.keys) == 0
    
    def get_all_keys(self):
        """Returns a list of all keys in the tree."""
        keys = []
        self._get_all_keys_recursive(self.root, keys)
        return keys

    def _get_all_keys_recursive(self, node, keys):
        """Helper to recursively gather all keys."""
        if node:
            keys.extend(node.keys)
            if not node.leaf:
                for child in node.children:
                    self._get_all_keys_recursive(child, keys)

