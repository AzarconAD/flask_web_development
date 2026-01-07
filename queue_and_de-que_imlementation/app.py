from flask import Flask, render_template, request, redirect, url_for, flash, session
from collections import deque
from bst import BST
from restaurant import Restaurant
from station_lines_graph import stations_graph
from collections import deque
import subprocess
import os
import sys

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class Queue:
    def __init__(self):
        self.front = None
        self.rear = None
        self._size = 0

    def is_empty(self):
        return self.front is None
    
    def enqueue(self, item):
        new_node = Node(item)
        if self.rear is None:
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self._size += 1

    def dequeue(self):
        if self.is_empty():
            raise Exception("Queue is empty, cannot dequeue.")
        temp = self.front
        self.front = temp.next
        if self.front is None:
            self.rear = None
        self._size -= 1
        return temp.data
    
    def size(self):
        return self._size
    
    def peek(self):
        if self.is_empty():
            return None
        return self.front.data
    
    def get_queue_list(self):
        """Convert linked list to Python list for display"""
        result = []
        current = self.front
        while current:
            result.append(current.data)
            current = current.next
        return result
    
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
            for neighbor in graph.vertices[station]:
                queue.append(path + [neighbor])
    return None

restaurant = Restaurant()
tabs = deque()
bst_tree = BST()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for flash messages

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/profile')
def profile():
    return render_template('profiles.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/projects/queue_card_game')
def queue_card_game():
    return render_template('queue_card_game.html')

@app.route('/projects/restaurant_simulator')
def restaurant():
    session.pop('_flashes', None)
    return render_template('restaurant.html', queue=Q.get_queue_list())

@app.route('/projects/restaurant_simulator/add', methods=['POST'])
def add_customer():
    name = request.form.get('name')
    if name:
        Q.enqueue(name)
        flash(f'✅ Added "{name}" to the queue!', 'success')
    else:
        flash('❌ Please enter a customer name!', 'error')
    return redirect(url_for('restaurant'))

@app.route('/projects/restaurant_simulator/remove', methods=['POST'])
def remove_customer():
    if Q.is_empty():
        flash('❌ Queue is empty, nothing to remove!', 'error')
    else:
        removed = Q.dequeue()
        flash(f'✅ Removed "{removed}" from the queue!', 'success')
    return redirect(url_for('restaurant'))

@app.route('/projects/restaurant_simulator/next')
def next_customer():
    next_customer = Q.peek()
    if next_customer is None:
        flash('ℹ️ Queue is empty, no next customer!', 'info')
    else:
        flash(f'👤 Next customer: {next_customer}', 'info')
    return redirect(url_for('restaurant'))

@app.route('/projects/restaurant_simulator/size')
def queue_size():
    size = Q.size()
    flash(f'📊 Queue size: {size} customer(s)', 'info')
    return redirect(url_for('restaurant'))

# Tab Manager Routes
@app.route('/projects/tab_manager')
def tab_manager():
    return render_template('tab_manager.html', tabs=list(tabs))

@app.route('/projects/tab_manager/add_front', methods=['POST'])
def add_front():
    page = request.form.get("page")
    if page:
        tabs.appendleft(page)
        flash(f'✅ Added "{page}" to front!', 'success')
    else:
        flash('❌ Please enter a page name!', 'error')
    return redirect(url_for("tab_manager"))

@app.route('/projects/tab_manager/add_rear', methods=['POST'])
def add_rear():
    page = request.form.get("page")
    if page:
        tabs.append(page)
        flash(f'✅ Added "{page}" to rear!', 'success')
    else:
        flash('❌ Please enter a page name!', 'error')
    return redirect(url_for("tab_manager"))

@app.route('/projects/tab_manager/remove_front', methods=['POST'])
def remove_front():
    if tabs:
        removed = tabs.popleft()
        flash(f'✅ Removed "{removed}" from front!', 'success')
    else:
        flash('❌ No tabs to remove!', 'error')
    return redirect(url_for("tab_manager"))

@app.route('/projects/tab_manager/remove_rear', methods=['POST'])
def remove_rear():
    if tabs:
        removed = tabs.pop()
        flash(f'✅ Removed "{removed}" from rear!', 'success')
    else:
        flash('❌ No tabs to remove!', 'error')
    return redirect(url_for("tab_manager"))

# Binary Search Tree Routes
@app.route('/projects/binary_tree')
def binary_tree():
    session.pop('_flashes', None)
    nodes, edges, svg_info = bst_tree.layout()
    traversal = bst_tree.post_traversal(bst_tree.root, [])
    return render_template('binary_tree.html', nodes=nodes, edges=edges, svg_info=svg_info, traversal=traversal)

@app.route('/projects/binary_tree/insert', methods=['POST'])
def bst_insert():
    try:
        value = int(request.form.get('value'))
        bst_tree.insert(value)
        flash(f'Inserted {value} into the tree!', 'success')
    except ValueError:
        flash('Please enter a valid number!', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('binary_tree'))

@app.route('/projects/binary_tree/search', methods=['POST'])
def bst_search():
    try:
        value = int(request.form.get('value'))
        found = bst_tree.search(bst_tree.root, value)
        if found:
            flash(f'Found {value} in the tree!', 'success')
        else:
            flash(f'{value} not found in the tree.', 'info')
    except ValueError:
        flash('Please enter a valid number!', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('binary_tree'))

@app.route('/projects/binary_tree/delete', methods=['POST'])
def bst_delete():
    try:
        value = int(request.form.get('value'))
        found = bst_tree.search(bst_tree.root, value)
        if found:
            bst_tree.root = bst_tree.delete_node(bst_tree.root, value)
            flash(f'Deleted {value} from the tree!', 'success')
        else:
            flash(f'{value} not found in the tree.', 'info')
    except ValueError:
        flash('Please enter a valid number!', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('binary_tree'))

@app.route('/projects/binary_tree/clear', methods=['POST'])
def bst_clear():
    bst_tree.root = None
    flash('Tree cleared!', 'success')
    return redirect(url_for('binary_tree'))

# Baccarat Game Routes
@app.route('/projects/baccarat_game')
def baccarat_game():
    session.pop('_flashes', None)
    return render_template('baccarat_game.html')

@app.route('/projects/baccarat_game/run', methods=['POST'])
def run_baccarat_game():
    try:
        # First, check if pygame is installed
        try:
            import pygame
        except ImportError:
            flash('Error: Pygame is not installed. Please install it with: pip install pygame', 'error')
            return redirect(url_for('baccarat_game'))
        
        # Path to the baccarat game script
        # app.py is at: queue_and_de-que_imlementation/app.py
        # baccarat_game.py is at: queue_and_de-que_imlementation/baccarat_game/baccarat_game.py
        current_dir = os.path.dirname(os.path.abspath(__file__))  # queue_and_de-que_imlementation
        game_dir = os.path.join(current_dir, 'baccarat_game')
        script_path = os.path.join(game_dir, 'baccarat_game.py')
        
        # Normalize paths for Windows
        script_path = os.path.normpath(script_path)
        game_dir = os.path.normpath(game_dir)
        
        # Verify the file exists
        if not os.path.exists(script_path):
            flash(f'Error: Game file not found at {script_path}', 'error')
            return redirect(url_for('baccarat_game'))
        
        # Use sys.executable to use the same Python interpreter, or try 'py' as fallback on Windows
        python_exe = sys.executable
        if os.name == 'nt':
            # On Windows, try 'py' launcher if sys.executable doesn't exist
            if not os.path.exists(python_exe):
                python_exe = 'py'
        
        # Debug: Print what we're trying to run
        print(f"Launching game with: {python_exe} {script_path}")
        print(f"Working directory: {game_dir}")
        
        # Launch the game as a subprocess (non-blocking)
        # Set working directory to game directory so assets can be found
        if os.name == 'nt':
            # Windows: Create new console window
            try:
                # Try with CREATE_NEW_CONSOLE first
                process = subprocess.Popen(
                    [python_exe, script_path], 
                    cwd=game_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                # Give it a moment to start
                import time
                time.sleep(0.5)
                # Check if process is still running (if it crashed immediately)
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    error_msg = stderr.decode('utf-8', errors='ignore') if stderr else 'Unknown error'
                    # Check for common errors
                    if 'ModuleNotFoundError' in error_msg or 'No module named' in error_msg:
                        if 'pygame' in error_msg.lower():
                            flash('Error: Pygame is not installed. Please install it with: pip install pygame', 'error')
                        else:
                            flash(f'Missing module: {error_msg[:150]}', 'error')
                    else:
                        flash(f'Game failed to start: {error_msg[:200]}', 'error')
                    print(f"Game process exited with code {process.returncode}")
                    print(f"STDERR: {error_msg}")
                    return redirect(url_for('baccarat_game'))
            except Exception as e:
                # Fallback: try without CREATE_NEW_CONSOLE
                try:
                    process = subprocess.Popen(
                        [python_exe, script_path], 
                        cwd=game_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    import time
                    time.sleep(0.5)
                    if process.poll() is not None:
                        stdout, stderr = process.communicate()
                        error_msg = stderr.decode('utf-8', errors='ignore') if stderr else 'Unknown error'
                        if 'ModuleNotFoundError' in error_msg or 'No module named' in error_msg:
                            if 'pygame' in error_msg.lower():
                                flash('Error: Pygame is not installed. Please install it with: pip install pygame', 'error')
                            else:
                                flash(f'Missing module: {error_msg[:150]}', 'error')
                        else:
                            flash(f'Game failed to start: {error_msg[:200]}', 'error')
                        return redirect(url_for('baccarat_game'))
                except Exception as e2:
                    flash(f'Error launching game: {str(e2)}', 'error')
                    print(f"Error details: {e2}")
                    import traceback
                    print(traceback.format_exc())
                    return redirect(url_for('baccarat_game'))
        else:
            # Unix/Linux: Run in background
            subprocess.Popen([python_exe, script_path], cwd=game_dir)
        
        flash('Baccarat game launched!', 'success')
    except Exception as e:
        flash(f'Error launching game: {str(e)}', 'error')
        import traceback
        print(f"Error details: {traceback.format_exc()}")
    
    return redirect(url_for('baccarat_game'))

@app.route("/projects/train-stations-simulator", methods=["GET", "POST"])
def train():
    path = None
    message = ""
    stations = stations = sorted([station.replace('_', ' ') for station in stations_graph.vertices.keys()])
    display_to_key = {station.replace('_', ' '): station for station in stations_graph.vertices.keys()}

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


    return render_template("transport_page.html", stations=stations, path=path, message=message, station_coords=station_coords)

#station coords for html coloring
station_coords = {
    #MRT COORDS
    "North_Avenue": (60,100),
    "Quezon_Avenue": (120,140),
    "GMA_Kamuning": (180,180),
    "Araneta_Center-Cubao": (180,300),
    "Santolan-Anapolis": (180,380),
    "Ortigas": (180,480),
    "Shaw_Boulevard": (140,520),
    "Boni_Avenue": (80,560),
    "Guadalupe": (0,620),
    "Buendia": (-80,680),
    "Ayala": (-180,703),
    "Magallanes": (-280,703),
    "Taft_Avenue": (-380,703),

    #LRT2 COORDS
    "Recto": (-420, 340),
    "Legarda": (-340, 340),
    "Pureza": (-260, 340),
    "V_Mapa": (-160, 340),
    "J_Ruiz": (-80, 340),
    "Gilmore": (30, 335),
    "Betty_Go-Belmonte": (80, 300),
    "Araneta_Center-Cubao": (180,300),
    "Anonas": (240, 300),
    "Katipunan": (300, 300),
    "Santolan": (360, 335),
    "Marikina-Pasig": (440, 335),
    "Antipolo": (520, 335),

    #LRT2 COORDS
    "Roosevelt": (50,50),
    "Balintawak": (-200, 50),
    "Monumento": (-450, 50),
    "5th_Avenue": (-450, 100),
    "R_Papa": (-450, 140),
    "Abad_Santos": (-450, 180),
    "Blumentritt": (-450, 220),
    "Tayuman": (-450, 260),
    "Bambang": (-450, 300),
    "Doroteo_Jose": (-450, 340),
    "Carriedo": (-450, 380),
    "Central_Terminal": (-450, 420),
    "UN_Avenue": (-450, 460),
    "Pedro_Gil": (-450, 500),
    "Quirino": (-450, 540),
    "Vito_Cruz": (-450, 580),
    "Gil_Puyat": (-450, 620),
    "Libertad": (-450, 660),
    "EDSA": (-450, 700),
    "Baclaran": (-450, 740)
}

if __name__ == "__main__":
    app.run(debug=True)
