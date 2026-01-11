from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from collections import deque

# --- CUSTOM IMPORTS ---
# 1. Card Game Logic (queue_card_game.py)
from queue_card_game import Game 
# 2. Binary Tree Logic (binary_tree.py)
from binary_tree import BinaryTree

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# ==========================================
#    INTERNAL DATA STRUCTURE CLASSES 
# ==========================================

# --- 1. LINKED LIST QUEUE (Restaurant) ---
class Node:
    def __init__(self, data): self.data = data; self.next = None

class Queue:
    def __init__(self): self.front = None; self.rear = None; self._size = 0
    def is_empty(self): return self.front is None
    def enqueue(self, item):
        new_node = Node(item)
        if self.rear is None: self.front = self.rear = new_node
        else: self.rear.next = new_node; self.rear = new_node
        self._size += 1
    def dequeue(self):
        if self.is_empty(): return None
        temp = self.front; self.front = temp.next
        if self.front is None: self.rear = None
        self._size -= 1; return temp.data
    def size(self): return self._size
    def peek(self): return None if self.is_empty() else self.front.data
    def get_queue_list(self):
        result = []; current = self.front
        while current: result.append(current.data); current = current.next
        return result

# --- 2. BINARY SEARCH TREE (For Visualizer UI Only) ---
class BSTNode:
    def __init__(self, value): self.value = value; self.left = None; self.right = None

class BST:
    def __init__(self): self.root = None
    def insert(self, root, key):
        if root is None: return BSTNode(key)
        if key < root.value: root.left = self.insert(root.left, key)
        else: root.right = self.insert(root.right, key)
        return root
    def search(self, root, key):
        if root is None or key == root.value: return root
        if key < root.value: return self.search(root.left, key)
        return self.search(root.right, key)
    def post_traversal(self, start, traversal):
        if start:
            self.post_traversal(start.left, traversal)
            self.post_traversal(start.right, traversal)
            traversal.append(start.value)
        return traversal

# --- 3. TRANSPORT GRAPH (For Route Finder) ---
class TransportGraph:
    def __init__(self):
        # 1. Define Coordinates for ALL stations
        self.coords = {
            # --- LRT 1 (Yellow) ---
            'Roosevelt': (50, 50),
            'Balintawak': (-200, 50),
            'Monumento': (-450, 50),
            '5th Avenue': (-450, 100),
            'R Papa': (-450, 140),
            'Abad Santos': (-450, 180),
            'Blumentritt': (-450, 220),
            'Tayuman': (-450, 260),
            'Bambang': (-450, 300),
            'Doroteo Jose': (-450, 340),
            'Carriedo': (-450, 380),
            'Central Terminal': (-450, 420),
            'UN Avenue': (-450, 460),
            'Pedro Gil': (-450, 500),
            'Quirino': (-450, 540),
            'Vito Cruz': (-450, 580),
            'Gil Puyat': (-450, 620),
            'Libertad': (-450, 660),
            'EDSA': (-450, 700),
            'Baclaran': (-450, 740),

            # --- LRT 2 (Purple) ---
            'Recto': (-420, 340),
            'Legarda': (-340, 340),
            'Pureza': (-260, 340),
            'V. Mapa': (-160, 340),
            'J. Ruiz': (-80, 340),
            'Gilmore': (30, 335),
            'Betty Go-Belmonte': (80, 300),
            'Araneta Center-Cubao': (180, 300), # Interchange
            'Anonas': (240, 300),
            'Katipunan': (300, 300),
            'Santolan': (360, 335),
            'Marikina-Pasig': (440, 335),
            'Antipolo': (520, 335),

            # --- MRT 3 (Blue) ---
            'North Ave': (60, 100),
            'Quezon Ave': (120, 140),
            'GMA Kamuning': (180, 180),
            'Santolan-Anapolis': (180, 380),
            'Ortigas': (180, 480),
            'Shaw Boulevard': (140, 520),
            'Boni Avenue': (80, 560),
            'Guadalupe': (0, 620),
            'Buendia': (-80, 680),
            'Ayala': (-180, 703),
            'Magallanes': (-280, 703),
            'Taft Avenue': (-380, 703)
        }

        # 2. Define Connections (Edges)
        self.edges = {}
        
        def add_connection(station1, station2):
            if station1 not in self.edges: self.edges[station1] = []
            if station2 not in self.edges: self.edges[station2] = []
            self.edges[station1].append(station2)
            self.edges[station2].append(station1)

        # LRT 1
        lrt1 = ['Roosevelt', 'Balintawak', 'Monumento', '5th Avenue', 'R Papa', 
                'Abad Santos', 'Blumentritt', 'Tayuman', 'Bambang', 'Doroteo Jose', 
                'Carriedo', 'Central Terminal', 'UN Avenue', 'Pedro Gil', 'Quirino', 
                'Vito Cruz', 'Gil Puyat', 'Libertad', 'EDSA', 'Baclaran']
        for i in range(len(lrt1) - 1): add_connection(lrt1[i], lrt1[i+1])

        # LRT 2
        lrt2 = ['Recto', 'Legarda', 'Pureza', 'V. Mapa', 'J. Ruiz', 'Gilmore', 
                'Betty Go-Belmonte', 'Araneta Center-Cubao', 'Anonas', 'Katipunan', 
                'Santolan', 'Marikina-Pasig', 'Antipolo']
        for i in range(len(lrt2) - 1): add_connection(lrt2[i], lrt2[i+1])

        # MRT 3
        mrt3 = ['North Ave', 'Quezon Ave', 'GMA Kamuning', 'Araneta Center-Cubao', 
                'Santolan-Anapolis', 'Ortigas', 'Shaw Boulevard', 'Boni Avenue', 
                'Guadalupe', 'Buendia', 'Ayala', 'Magallanes', 'Taft Avenue']
        for i in range(len(mrt3) - 1): add_connection(mrt3[i], mrt3[i+1])

        # INTERCHANGES
        add_connection('Roosevelt', 'North Ave')
        add_connection('Doroteo Jose', 'Recto')
        add_connection('EDSA', 'Taft Avenue')

    def get_shortest_path(self, start, end):
        if start not in self.edges or end not in self.edges: return None
        queue = deque([[start]])
        visited = set()
        
        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == end: return path
            if node not in visited:
                visited.add(node)
                for neighbor in self.edges.get(node, []):
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)
        return None

# --- VISUALIZER HELPERS ---
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
    if node.right: result += get_text_tree(node.right, prefix + ("│   " if is_left else "    "), False)
    result += prefix + ("└── " if is_left else "┌── ") + str(node.value) + "\n"
    if node.left: result += get_text_tree(node.left, prefix + ("    " if is_left else "│   "), True)
    return result


# ==========================================
#    GLOBAL INSTANCES
# ==========================================
Q = Queue()              
tabs = deque()           
bst_tree = BST()         
card_game = Game()       
tree = BinaryTree()      
transit_map = TransportGraph() # Project 6 Instance


# ==========================================
#    MAIN PAGE ROUTES
# ==========================================
@app.route('/')
def index(): return render_template('home.html')

@app.route('/profile')
def profile(): return render_template('profiles.html')

@app.route('/projects')
def projects(): return render_template('projects.html')


# ==========================================
#    PROJECT 1: QUEUE CARD GAME
# ==========================================
@app.route('/projects/queue_card_game')
def queue_card_game():
    return render_template('queue_card_game.html', game=card_game)

@app.route('/projects/queue_card_game/deposit', methods=['POST'])
def game_deposit():
    try:
        amount = float(request.form.get('amount'))
        success, msg = card_game.deposit(amount)
        flash(f"{'✅' if success else '❌'} {msg}", 'success' if success else 'error')
    except ValueError:
        flash('❌ Invalid input', 'error')
    return redirect(url_for('queue_card_game'))

@app.route('/projects/queue_card_game/withdraw', methods=['POST'])
def game_withdraw():
    try:
        amount = float(request.form.get('amount'))
        success, msg = card_game.withdraw(amount)
        flash(f"{'✅' if success else '❌'} {msg}", 'success' if success else 'error')
    except ValueError:
        flash('❌ Invalid input', 'error')
    return redirect(url_for('queue_card_game'))

@app.route('/projects/queue_card_game/bet', methods=['POST'])
def game_bet():
    try:
        amount = float(request.form.get('amount'))
        success, msg = card_game.place_bet(amount)
        flash(f"{'🎲' if success else '❌'} {msg}", 'info' if success else 'error')
    except ValueError:
        flash('❌ Invalid bet amount', 'error')
    return redirect(url_for('queue_card_game'))

@app.route('/projects/queue_card_game/shuffle', methods=['POST'])
def game_shuffle():
    card_game.reset_game()
    flash('🔀 Deck reshuffled! New cards dealt.', 'info')
    return redirect(url_for('queue_card_game'))


# ==========================================
#    PROJECT 2: RESTAURANT SIMULATOR
# ==========================================
@app.route('/projects/restaurant_simulator')
def restaurant():
    session.pop('_flashes', None)
    return render_template('restaurant.html', queue=Q.get_queue_list())

@app.route('/projects/restaurant_simulator/add', methods=['POST'])
def add_customer():
    name = request.form.get('name')
    if name:
        Q.enqueue(name); flash(f'✅ Added "{name}"', 'success')
    else: flash('❌ Enter name', 'error')
    return redirect(url_for('restaurant'))

@app.route('/projects/restaurant_simulator/remove', methods=['POST'])
def remove_customer():
    if Q.is_empty(): flash('❌ Queue empty', 'error')
    else: removed = Q.dequeue(); flash(f'✅ Served "{removed}"', 'success')
    return redirect(url_for('restaurant'))

@app.route('/projects/restaurant_simulator/size')
def queue_size():
    flash(f'📊 Count: {Q.size()}', 'info')
    return redirect(url_for('restaurant'))


# ==========================================
#    PROJECT 3: TAB MANAGER
# ==========================================
@app.route('/projects/tab_manager')
def tab_manager(): return render_template('tab_manager.html', tabs=list(tabs))

@app.route('/projects/tab_manager/add_front', methods=['POST'])
def add_front():
    page = request.form.get("page")
    if page: tabs.appendleft(page); flash('✅ Added to Front', 'success')
    return redirect(url_for("tab_manager"))

@app.route('/projects/tab_manager/add_rear', methods=['POST'])
def add_rear():
    page = request.form.get("page")
    if page: tabs.append(page); flash('✅ Added to Rear', 'success')
    return redirect(url_for("tab_manager"))

@app.route('/projects/tab_manager/remove_front', methods=['POST'])
def remove_front():
    if tabs: tabs.popleft(); flash('✅ Removed Front', 'success')
    else: flash('❌ Empty', 'error')
    return redirect(url_for("tab_manager"))

@app.route('/projects/tab_manager/remove_rear', methods=['POST'])
def remove_rear():
    if tabs: tabs.pop(); flash('✅ Removed Rear', 'success')
    else: flash('❌ Empty', 'error')
    return redirect(url_for("tab_manager"))


# ==========================================
#    PROJECT 4: BST VISUALIZER (HTML)
# ==========================================
@app.route('/projects/bst', methods=["GET"])
def bst_index(): return render_bst_view()

@app.route('/projects/bst/insert', methods=["POST"])
def bst_insert():
    try: bst_tree.root = bst_tree.insert(bst_tree.root, int(request.form["value"]))
    except ValueError: pass
    return render_bst_view()

@app.route('/projects/bst/search', methods=["POST"])
def bst_search():
    try:
        val = int(request.form["value"])
        found = bst_tree.search(bst_tree.root, val)
        return render_bst_view(highlight=val if found else None)
    except ValueError: return render_bst_view()

def render_bst_view(highlight=None):
    nodes = []; edges = []
    build_tree_data(bst_tree.root, 400, 40, 1, nodes, edges)
    return render_template('bstvisual.html', nodes=nodes, edges=edges, 
                           svg_info={'width': 800, 'height': 600, 'node_radius': 20},
                           post_order=bst_tree.post_traversal(bst_tree.root, []),
                           tree_visual=get_text_tree(bst_tree.root), highlight=highlight)


# ==========================================
#    PROJECT 5: BINARY TREE (JSON API)
# ==========================================
@app.route('/projects/binary_tree')
def binary_tree_page():
    return render_template('binary_tree.html')

@app.route("/insert", methods=["POST"])
def insert():
    data = request.get_json()
    if data: value = data.get("value")
    else: value = request.form.get("value")
    
    if value is not None:
        try:
            val_int = int(value)
            tree.insert(val_int)
            return jsonify({"message": f"Inserted {val_int}", "level_order": tree.level_order()})
        except ValueError:
            return jsonify({"error": "Invalid integer"}), 400
    return jsonify({"error": "No value provided"}), 400

@app.route("/traverse/<method>")
def traverse(method):
    if method == "preorder": return jsonify(tree.preorder()) 
    elif method == "inorder": return jsonify(tree.inorder())
    elif method == "postorder": return jsonify(tree.postorder())
    elif method == "level": return jsonify(tree.level_order())
    else: return jsonify({"error": "Invalid traversal method"}), 400


# ==========================================
#    PROJECT 6: TRANSPORT OPTIMIZATION (This was missing!)
# ==========================================
@app.route('/projects/transport_optimization', methods=['GET', 'POST'])
def transport_optimization():
    path = None
    stations = []
    
    # Check if map exists (it is defined in globals at the top)
    if 'transit_map' in globals():
        stations = list(transit_map.edges.keys())
        stations.sort() # Sort alphabetically for easy dropdown
        
        if request.method == 'POST':
            start = request.form.get('from_station')
            end = request.form.get('to_station')
            
            # BFS Algorithm
            path = transit_map.get_shortest_path(start, end)
            
            if not path:
                flash(f"No path found between {start} and {end}", "error")
    else:
        flash("Error: Transit Map not initialized.", "error")

    return render_template('transport.html', 
                           stations=stations, 
                           path=path, 
                           station_coords=transit_map.coords if 'transit_map' in globals() else {})


if __name__ == "__main__":
    app.run(debug=True)