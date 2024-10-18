import tkinter as tk
from tkinter import messagebox, simpledialog
import networkx as nx
import matplotlib.pyplot as plt
import random

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Application (Undirected Graph with Directed Euler Path/Circuit)")
        self.label = tk.Label(root, text="Enter Degree Sequence (comma-separated):")
        self.label.pack()
        self.entry = tk.Entry(root)
        self.entry.pack()
        self.generate_button = tk.Button(root, text="Generate Graph", command=self.generate_graph)
        self.generate_button.pack()
        self.euler_button = tk.Button(root, text="Find Euler Path/Circuit", command=self.find_euler, state=tk.DISABLED)
        self.euler_button.pack()
        self.shortest_path_button = tk.Button(root, text="Find Shortest Path", command=self.find_shortest_path, state=tk.DISABLED)
        self.shortest_path_button.pack()
        self.mst_button = tk.Button(root, text="Find Minimum Spanning Tree", command=self.find_mst, state=tk.DISABLED)
        self.mst_button.pack()
        self.connectivity_button = tk.Button(root, text="Find Edge and Vertex Connectivity", command=self.find_connectivity, state=tk.DISABLED)
        self.connectivity_button.pack()
        self.cutset_button = tk.Button(root, text="Find Fundamental Cutsets", command=self.find_fundamental_cutsets, state=tk.DISABLED)
        self.cutset_button.pack()
        self.cut_vertices_button = tk.Button(root, text="Find Cut Vertices", command=self.find_cut_vertices, state=tk.DISABLED)
        self.cut_vertices_button.pack()

        self.graph = None
        self.mst = None
        self.pos = None

    def is_graphic_sequence(self, seq):
        while True:
            seq = sorted(seq, reverse=True)
            if all(v == 0 for v in seq):
                return True
            if seq[0] < 0 or seq[0] >= len(seq):
                return False
            d = seq[0]
            seq = seq[1:]
            for i in range(d):
                if i >= len(seq):
                    return False
                seq[i] -= 1

    def havel_hakimi(self, seq):
        G = nx.Graph()
        if not self.is_graphic_sequence(seq):
            return None
        degree_list = sorted([(i, seq[i]) for i in range(len(seq))], key=lambda x: x[1], reverse=True)

        while degree_list:
            node, degree = degree_list.pop(0)
            if degree == 0:
                continue
            neighbors = [x[0] for x in degree_list[:degree]]
            for neighbor in neighbors:
                G.add_edge(node, neighbor)
            degree_list = [(x[0], x[1] - 1 if x[0] in neighbors else x[1]) for x in degree_list]
            degree_list = sorted(degree_list, key=lambda x: x[1], reverse=True)
        
        return G

    def draw_graph(self):
        plt.figure()
        labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw(self.graph, self.pos, with_labels=True, node_color='lightblue', node_size=700, font_size=10)
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=labels)
        plt.show(block=False)

    def generate_graph(self):
        degree_sequence = list(map(int, self.entry.get().split(',')))
        if not self.is_graphic_sequence(degree_sequence):
            messagebox.showerror("Error", "Invalid degree sequence.")
            return

        self.graph = self.havel_hakimi(degree_sequence)

        if self.graph is None:
            messagebox.showerror("Error", "Graph generation failed.")
            return

        for (u, v) in self.graph.edges():
            self.graph[u][v]['weight'] = random.randint(1, 10)

        self.pos = nx.spring_layout(self.graph)
        self.draw_graph()

        self.shortest_path_button.config(state=tk.NORMAL)
        self.mst_button.config(state=tk.NORMAL)
        self.euler_button.config(state=tk.NORMAL)
        self.connectivity_button.config(state=tk.NORMAL)

        self.cutset_button.config(state=tk.DISABLED)
        self.cut_vertices_button.config(state=tk.DISABLED)

    def visualize_euler(self, euler_edges, is_circuit=False):
        directed_graph = nx.DiGraph()
        if not is_circuit:
            euler_edges = euler_edges[:-1]

        directed_graph.add_edges_from(euler_edges)

        plt.figure()
        nx.draw(directed_graph, pos=self.pos, with_labels=True, node_color='lightgreen', node_size=700, font_size=10, arrows=True)
        edge_labels = {(u, v): f"{u}->{v}" for u, v in euler_edges}
        nx.draw_networkx_edge_labels(directed_graph, pos=self.pos, edge_labels=edge_labels)

        if is_circuit:
            plt.title("Euler Circuit (Directed)")
        else:
            plt.title("Euler Path (Directed, Open)")

        plt.show()

    def find_euler(self):
        if not nx.is_eulerian(self.graph):
            if nx.has_eulerian_path(self.graph):
                path = list(nx.eulerian_path(self.graph))
                path_edges = [(path[i][0], path[i][1]) for i in range(len(path))]
                messagebox.showinfo("Euler Path", f"Euler Path: {path_edges}")
                self.visualize_euler(path_edges, is_circuit=False)
            else:
                messagebox.showinfo("Result", "The graph does not have an Euler Path or Circuit.")
        else:
            circuit = list(nx.eulerian_circuit(self.graph))
            circuit_edges = [(circuit[i][0], circuit[i][1]) for i in range(len(circuit))]
            messagebox.showinfo("Euler Circuit", f"Euler Circuit: {circuit_edges}")
            self.visualize_euler(circuit_edges, is_circuit=True)
            
    def find_shortest_path(self):
        start_node = simpledialog.askinteger("Input", "Enter the starting vertex:")
        if start_node not in self.graph.nodes:
            messagebox.showerror("Error", "Invalid start node.")
            return
        length, path = nx.single_source_dijkstra(self.graph, start_node)
        messagebox.showinfo("Shortest Paths", f"Shortest Paths from {start_node}: {path}")

    def find_mst(self):
        if self.graph is None:
            messagebox.showerror("Error", "Graph has not been generated.")
            return
        
        self.mst = nx.minimum_spanning_tree(self.graph, algorithm='prim')
        plt.figure()
        labels = nx.get_edge_attributes(self.mst, 'weight')
        nx.draw(self.mst, self.pos, with_labels=True, node_color='lightgreen', node_size=700, font_size=10)
        nx.draw_networkx_edge_labels(self.mst, self.pos, edge_labels=labels)
        plt.title("Minimum Spanning Tree")
        plt.show()

        self.cutset_button.config(state=tk.NORMAL)
        self.cut_vertices_button.config(state=tk.NORMAL)

    def find_connectivity(self):
        edge_connectivity = nx.edge_connectivity(self.graph)
        vertex_connectivity = nx.node_connectivity(self.graph)

        messagebox.showinfo("Connectivity",
                            f"Edge Connectivity: {edge_connectivity}\n"
                            f"Vertex Connectivity: {vertex_connectivity}\n"
                            f"The graph is {vertex_connectivity}-connected.")

    def find_fundamental_cutsets(self):
        if self.mst is None:
            messagebox.showerror("Error", "Minimum Spanning Tree not generated.")
            return

        cutsets = []
        for edge in self.mst.edges():
            component_1 = nx.node_connected_component(self.mst, edge[0])
            component_2 = {edge[1]}
            cutset = nx.edge_boundary(self.graph, component_1, component_2)
            cutsets.append(list(cutset))

        messagebox.showinfo("Fundamental Cutsets", f"Fundamental Cutsets: {cutsets}")
    
    def find_cut_vertices(self):
        if self.mst is None:
            messagebox.showerror("Error", "Minimum Spanning Tree not generated.")
            return

        cut_vertices = list(nx.articulation_points(self.mst))
        messagebox.showinfo("Cut Vertices", f"Cut Vertices (Articulation Points): {cut_vertices}")

root = tk.Tk()
app = GraphApp(root)
root.mainloop()
