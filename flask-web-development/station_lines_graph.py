from collections import deque

class Graph:
    def __init__(self):
        self.vertices = {}
    
    def add_vertex(self, vertex):
        self.vertices[vertex] = []

    def add_edge(self, source, target):
        self.vertices[source].append(target)

    def add_edges_from(self, edges):
        for source, target in edges:
            self.add_edge(source, target)

# -- MRT --

mrt_stations = [
    "North_Avenue",
    "Quezon_Avenue",
    "GMA_Kamuning",
    "Araneta_Center-Cubao",
    "Santolan-Anapolis",
    "Ortigas",
    "Shaw_Boulevard",
    "Boni_Avenue",
    "Guadalupe",
    "Buendia",
    "Ayala",
    "Magallanes",
    "Taft_Avenue"
]

mrt_edges = [
    ("North_Avenue","Quezon_Avenue"),
    ("Quezon_Avenue","GMA_Kamuning"),
    ("Quezon_Avenue","North_Avenue"),
    ("GMA_Kamuning","Araneta_Center-Cubao"),
    ("GMA_Kamuning","Quezon_Avenue"),
    ("Araneta_Center-Cubao","Santolan-Anapolis"),
    ("Araneta_Center-Cubao","GMA_Kamuning"),
    ("Santolan-Anapolis","Ortigas"),
    ("Santolan-Anapolis","Araneta_Center-Cubao"),
    ("Ortigas","Shaw_Boulevard"),
    ("Ortigas","Santolan-Anapolis"),
    ("Shaw_Boulevard","Boni_Avenue"),
    ("Shaw_Boulevard","Ortigas"),
    ("Boni_Avenue","Guadalupe"),
    ("Boni_Avenue","Shaw_Boulevard"),
    ("Guadalupe","Buendia"),
    ("Guadalupe","Boni_Avenue"),
    ("Buendia","Ayala"),
    ("Buendia","Guadalupe"),
    ("Ayala","Magallanes"),
    ("Ayala","Buendia"),
    ("Magallanes","Taft_Avenue"),
    ("Magallanes","Ayala"),
    ("Taft_Avenue","Magallanes")
]


# -- LRT2 --

LRT2_stations = [
    "Recto",
    "Legarda",
    "Pureza",
    "V_Mapa",
    "J_Ruiz",
    "Gilmore",
    "Betty_Go-Belmonte",
    "Araneta_Center-Cubao",
    "Anonas",
    "Katipunan",
    "Santolan",
    "Marikina-Pasig",
    "Antipolo"
]

LRT2_edges = [
    ("Recto","Legarda"),
    ("Legarda","Pureza"),
    ("Legarda","Recto"),
    ("Pureza","V_Mapa"),
    ("Pureza","Legarda"),
    ("V_Mapa","J_Ruiz"),
    ("V_Mapa","Pureza"),
    ("J_Ruiz","Gilmore"),
    ("J_Ruiz","V_Mapa"),
    ("Gilmore","Betty_Go-Belmonte"),
    ("Gilmore","J_Ruiz"),
    ("Betty_Go-Belmonte","Araneta_Center-Cubao"),
    ("Betty_Go-Belmonte","Gilmore"),
    ("Araneta_Center-Cubao","Anonas"),
    ("Araneta_Center-Cubao","Betty_Go-Belmonte"),
    ("Anonas","Katipunan"),
    ("Anonas","Araneta_Center-Cubao"),
    ("Katipunan","Santolan"),
    ("Katipunan","Anonas"),
    ("Santolan","Marikina-Pasig"),
    ("Santolan","Katipunan"),
    ("Marikina-Pasig","Antipolo"),
    ("Marikina-Pasig","Santolan"),
    ("Antipolo","Marikina-Pasig")
]

# -- LRT1 --

LRT1_stations = [
    "Roosevelt",
    "Balintawak",
    "Monumento",
    "5th_Avenue",
    "R_Papa",
    "Abad_Santos",
    "Blumentritt",
    "Tayuman",
    "Bambang",
    "Doroteo_Jose",
    "Carriedo",
    "Central_Terminal",
    "UN_Avenue",
    "Pedro_Gil",
    "Quirino",
    "Vito_Cruz",
    "Gil_Puyat",
    "Libertad",
    "EDSA",
    "Baclaran"
]

LRT1_edges = [
    ("Roosevelt","Balintawak"),
    ("Balintawak","Monumento"),
    ("Balintawak","Roosevelt"),
    ("Monumento","5th_Avenue"),
    ("Monumento","Balintawak"),
    ("5th_Avenue","R_Papa"),
    ("5th_Avenue","Monumento"),
    ("R_Papa","Abad_Santos"),
    ("R_Papa","5th_Avenue"),
    ("Abad_Santos","Blumentritt"),
    ("Abad_Santos","R_Papa"),
    ("Blumentritt","Tayuman"),
    ("Blumentritt","Abad_Santos"),
    ("Tayuman","Bambang"),
    ("Tayuman","Blumentritt"),
    ("Bambang","Doroteo_Jose"),
    ("Bambang","Tayuman"),
    ("Doroteo_Jose","Carriedo"),
    ("Doroteo_Jose","Bambang"),
    ("Carriedo","Central_Terminal"),
    ("Carriedo","Doroteo_Jose"),
    ("Central_Terminal","UN_Avenue"),
    ("Central_Terminal","Carriedo"),
    ("UN_Avenue","Pedro_Gil"),
    ("UN_Avenue","Central_Terminal"),
    ("Pedro_Gil","Quirino"),
    ("Pedro_Gil","UN_Avenue"),
    ("Quirino","Vito_Cruz"),
    ("Quirino","Pedro_Gil"),
    ("Vito_Cruz","Gil_Puyat"),
    ("Vito_Cruz","Quirino"),
    ("Gil_Puyat","Libertad"),
    ("Gil_Puyat","Vito_Cruz"),
    ("Libertad","EDSA"),
    ("Libertad","Gil_Puyat"),
    ("EDSA","Baclaran"),
    ("EDSA","Libertad"),
    ("Baclaran","EDSA"),
]

# ----INTERCONNECTIONS GRAPH----

stations_graph = Graph()

for station in mrt_stations + LRT2_stations + LRT1_stations:
    stations_graph.add_vertex(station)

stations_graph.add_edges_from(mrt_edges)
stations_graph.add_edges_from(LRT2_edges)
stations_graph.add_edges_from(LRT1_edges)

# -- STATION TRANSFER CONNECTIONS --

stations_graph.add_edge("Araneta_Center-Cubao", "Araneta_Center-Cubao")
stations_graph.add_edge("Araneta_Center-Cubao", "Araneta_Center-Cubao")
stations_graph.add_edge("Taft_Avenue", "EDSA")
stations_graph.add_edge("EDSA", "Taft_Avenue")
stations_graph.add_edge("Roosevelt", "North_Avenue")
stations_graph.add_edge("North_Avenue","Roosevelt")
stations_graph.add_edge("Doroteo_Jose","Recto")
stations_graph.add_edge("Recto","Doroteo_Jose")

def bfs_shortest_path(graph, start, goal):
    if start not in graph.vertices or goal not in graph.vertices:
        return None

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
                new_path = path + [neighbor]
                queue.append(new_path)
    return None