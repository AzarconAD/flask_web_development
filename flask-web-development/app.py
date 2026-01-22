from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from collections import deque
import os

# --- CUSTOM IMPORTS ---
# 1. Card Game Logic (queue_card_game.py)
from queue_card_game import Game 
# 2. Binary Tree Logic (binary_tree.py)
from binary_tree import BinaryTree
# 3. Sorting Functions (sorting_functions.py)
from sorting_functions import bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort
# 4. Transport Optimization (station_lines_graph.py)
from station_lines_graph import stations_graph

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Route to serve assets
@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(os.path.join(app.root_path, 'assets'), filename)

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
            '5th_Avenue': (-450, 100),
            'R_Papa': (-450, 140),
            'Abad_Santos': (-450, 180),
            'Blumentritt': (-450, 220),
            'Tayuman': (-450, 260),
            'Bambang': (-450, 300),
            'Doroteo_Jose': (-450, 340),
            'Carriedo': (-450, 380),
            'Central_Terminal': (-450, 420),
            'UN_Avenue': (-450, 460),
            'Pedro_Gil': (-450, 500),
            'Quirino': (-450, 540),
            'Vito_Cruz': (-450, 580),
            'Gil_Puyat': (-450, 620),
            'Libertad': (-450, 660),
            'EDSA': (-450, 700),
            'Baclaran': (-450, 740),

            # --- LRT 2 (Purple) ---
            'Recto': (-420, 340),
            'Legarda': (-340, 340),
            'Pureza': (-260, 340),
            'V_Mapa': (-160, 340),
            'J_Ruiz': (-80, 340),
            'Gilmore': (30, 335),
            'Betty_Go-Belmonte': (80, 300),
            'Araneta_Center-Cubao': (180, 300), # Interchange
            'Anonas': (240, 300),
            'Katipunan': (300, 300),
            'Santolan': (360, 335),
            'Marikina-Pasig': (440, 335),
            'Antipolo': (520, 335),

            # --- MRT 3 (Blue) ---
            'North_Avenue': (60, 100),
            'Quezon_Avenue': (120, 140),
            'GMA_Kamuning': (180, 180),
            'Santolan-Anapolis': (180, 380),
            'Ortigas': (180, 480),
            'Shaw_Boulevard': (140, 520),
            'Boni_Avenue': (80, 560),
            'Guadalupe': (0, 620),
            'Buendia': (-80, 680),
            'Ayala': (-180, 703),
            'Magallanes': (-280, 703),
            'Taft_Avenue': (-380, 703)
        }

# --- VISUALIZER HELPERS ---
# For BST (Binary Search Tree)
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

# For Binary Tree (uses different Node class from binary_tree.py)
# Use object id to handle duplicate values
def build_tree_data_binary(node, x, y, level, nodes, edges):
    if not node: return
    offset = max(200 // (2 ** (level-1)) if level > 1 else 200, 40)
    node_id = id(node)  # Use unique object ID instead of value
    nodes.append({'id': node_id, 'value': node.value, 'x': x, 'y': y})
    if node.left:
        edges.append({'from': node_id, 'to': id(node.left)})
        build_tree_data_binary(node.left, x - offset, y + 80, level + 1, nodes, edges)
    if node.right:
        edges.append({'from': node_id, 'to': id(node.right)})
        build_tree_data_binary(node.right, x + offset, y + 80, level + 1, nodes, edges)

def get_text_tree_binary(node, prefix="", is_left=True):
    if not node: return ""
    result = ""
    if node.right: result += get_text_tree_binary(node.right, prefix + ("│   " if is_left else "    "), False)
    result += prefix + ("└── " if is_left else "┌── ") + str(node.value) + "\n"
    if node.left: result += get_text_tree_binary(node.left, prefix + ("    " if is_left else "│   "), True)
    return result


# ==========================================
#    GLOBAL INSTANCES
# ==========================================
Q = Queue()              
tabs = deque()           
bst_tree = BST()         
card_game = Game()       
tree = BinaryTree()      
transit_map = TransportGraph()


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
    nodes = []
    edges = []
    tree_visual = ""
    
    # Build tree visualization data if tree has nodes
    if tree.root:
        build_tree_data_binary(tree.root, 400, 40, 1, nodes, edges)
        tree_visual = get_text_tree_binary(tree.root)
    
    return render_template('binary_tree.html',
                         nodes=nodes,
                         edges=edges,
                         svg_info={'width': 800, 'height': 600, 'node_radius': 20},
                         tree_visual=tree_visual,
                         level_order=tree.level_order())

@app.route("/projects/binary_tree/insert", methods=["POST"])
def binary_tree_insert():
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

@app.route("/projects/binary_tree/traverse/<method>")
def binary_tree_traverse(method):
    if method == "preorder": return jsonify(tree.preorder()) 
    elif method == "inorder": return jsonify(tree.inorder())
    elif method == "postorder": return jsonify(tree.postorder())
    elif method == "level": return jsonify(tree.level_order())
    else: return jsonify({"error": "Invalid traversal method"}), 400


# ==========================================
#    PROJECT 6: SORTING VISUALIZER
# ==========================================
# Wrapper functions to capture steps for visualization
def bubble_sort_steps(array):
    steps = []
    n = len(array)
    arr = array.copy()
    for i in range(n - 1):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                steps.append(arr.copy())
    return steps

def selection_sort_steps(array):
    steps = []
    n = len(array)
    arr = array.copy()
    for i in range(n - 1):
        min_index = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_index]:
                min_index = j
        if min_index != i:
            arr[i], arr[min_index] = arr[min_index], arr[i]
            steps.append(arr.copy())
    return steps

def insertion_sort_steps(array):
    steps = []
    n = len(array)
    arr = array.copy()
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
        steps.append(arr.copy())
    return steps

def merge_sort_steps(array):
    steps = []
    arr = array.copy()
    
    def merge_sort_rec(arr):
        if len(arr) > 1:
            mid = len(arr) // 2
            left_half = arr[:mid]
            right_half = arr[mid:]
            merge_sort_rec(left_half)
            merge_sort_rec(right_half)
            i = j = k = 0
            while i < len(left_half) and j < len(right_half):
                if left_half[i] < right_half[j]:
                    arr[k] = left_half[i]
                    i += 1
                else:
                    arr[k] = right_half[j]
                    j += 1
                k += 1
            while i < len(left_half):
                arr[k] = left_half[i]
                i += 1
                k += 1
            while j < len(right_half):
                arr[k] = right_half[j]
                j += 1
                k += 1
            steps.append(arr.copy())
    
    merge_sort_rec(arr)
    return steps

def quick_sort_steps(array):
    steps = []
    arr = array.copy()
    
    def quick_sort_rec(arr, low, high):
        if low < high:
            pi = partition(arr, low, high)
            steps.append(arr.copy())
            quick_sort_rec(arr, low, pi - 1)
            quick_sort_rec(arr, pi + 1, high)
    
    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    quick_sort_rec(arr, 0, len(arr) - 1)
    return steps

@app.route('/projects/sorting_visualizer', methods=["GET", "POST"])
def sorting_visualizer():
    steps = []
    numbers = ""
    algo = ""
    if request.method == "POST":
        numbers = request.form["numbers"]
        algo = request.form["algorithm"]
        try:
            array = list(map(int, numbers.strip().split(",")))
        except:
            array = []
        if algo == "Bubble Sort":
            steps = bubble_sort_steps(array)
        elif algo == "Selection Sort":
            steps = selection_sort_steps(array)
        elif algo == "Insertion Sort":
            steps = insertion_sort_steps(array)
        elif algo == "Merge Sort":
            steps = merge_sort_steps(array)
        elif algo == "Quick Sort":
            steps = quick_sort_steps(array)
    return render_template("sorting.html", steps=steps, numbers=numbers, algo=algo)


# ==========================================
#    PROJECT 7: TRANSPORT OPTIMIZATION
# ==========================================

def bfs_shortest_path(graph, start, goal):
        visited = set()
        queue = deque([[start]])
        while queue:
            path = queue.popleft()
            station = path[-1]
            if station == goal:
                return path
            if station not in visited:
                visited.add(station)
                for neighbor in graph.vertices.get(station, []):
                    queue.append(path + [neighbor])
        return None

@app.route('/projects/transport_optimization', methods=['GET', 'POST'])
def transport_optimization():
    path = None
    message = ""
    stations = sorted([s.replace('_', ' ') for s in stations_graph.vertices.keys()])
    display_to_key = {s.replace('_', ' '): s for s in stations_graph.vertices.keys()}

    if request.method == "POST":
        start_display = request.form.get("from_station")
        end_display = request.form.get("to_station")

        start = display_to_key.get(start_display)
        end = display_to_key.get(end_display)

        if start is None or end is None:
            message = "Invalid station input! Please select from available stations."
        else:
            path = bfs_shortest_path(stations_graph, start, end)
            if not path:
                message = "No path found between the selected stations."

    return render_template(
        "transport.html", 
        stations=stations, 
        path=path, 
        message=message, 
        station_coords=transit_map.coords  # coords for plotting
    )

if __name__ == "__main__":
    app.run(debug=True)