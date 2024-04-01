import ast
import click
import networkx as nx
from networkx.drawing.nx_agraph import write_dot

class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.call_graph = {}
        self.current_function = None  # Initialize to None

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        if node.name not in self.call_graph:
            self.call_graph[node.name] = set()
        self.generic_visit(node)
        self.current_function = None  # Reset to None after visiting the function

    def visit_Call(self, node):
        if self.current_function:  # Only proceed if inside a function definition
            if hasattr(node.func, 'id'):  # Simple function calls
                self.call_graph[self.current_function].add(node.func.id)
            elif hasattr(node.func, 'attr'):  # Method calls
                self.call_graph[self.current_function].add(node.func.attr)
        self.generic_visit(node)

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
def analyze_file(file_path):
    """Analyzes a Python file and prints a function call graph in Dot format."""
    try:
        with open(file_path, 'r') as file:
            source_code = file.read()

        tree = ast.parse(source_code)
        visitor = FunctionCallVisitor()
        visitor.visit(tree)

                # Create a networkx graph from the call graph
        G = nx.DiGraph()

        # Add edges to the graph
        for caller, callees in visitor.call_graph.items():
            for callee in callees:
                G.add_edge(caller, callee)
        
        # Style nodes and edges in networkx
        for node in G.nodes():
            if G.out_degree(node) > 4:
                G.nodes[node]['color'] = 'red'
                G.nodes[node]['fontcolor'] = 'red'
                # Get edges for this node and color them red
                for edge in G.out_edges(node):
                    G.edges[edge]['color'] = 'red'
        
        # Now convert networkx graph to AGraph (pygraphviz)
        A = nx.nx_agraph.to_agraph(G)

        # Apply styles from networkx to AGraph
        for node in A.nodes():
            n = A.get_node(node)
            if 'color' in G.nodes[node]:
                n.attr['color'] = G.nodes[node]['color']
                n.attr['fontcolor'] = G.nodes[node]['fontcolor']
        
        for edge in A.edges():
            e = A.get_edge(edge[0], edge[1])
            if 'color' in G.edges[edge]:
                e.attr['color'] = G.edges[edge]['color']

        print(A.to_string())

    except Exception as e:
        click.echo(f"Error analyzing file: {e}")

if __name__ == "__main__":
    analyze_file()

