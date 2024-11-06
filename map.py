import os
import argparse
from graphviz import Digraph

class MindMapFromIndentedText:
    def __init__(self, text_file, max_depth=None, max_line_length=30):
        self.text_file = text_file
        self.graph = Digraph(comment="Mind Map", format='svg')  # Use SVG for better scalability
        self.graph.attr(rankdir='LR')  # Set to Left-to-Right layout
        self.graph.attr(nodesep="0.4", ranksep="0.4")  # Set node and rank separation for compact layout
        self.node_counter = 0
        self.level_colors = ["lightblue", "lightgreen", "lightcoral", "lightyellow", "lightpink", "lightgrey"]
        self.multi_parent_color = "orange"  # Color for nodes with multiple parents
        self.final_node_color = "gold"  # Color for the final node
        self.max_depth = max_depth  # Optional: Limit visualization depth
        self.max_line_length = max_line_length  # Set maximum line length for text wrapping
        self.node_dict = {}  # Dictionary to keep track of nodes by level
        self.parent_count = {}  # Dictionary to count parents for each node
        self.leaf_nodes = set()  # Set to track leaf nodes
        self.final_node_id = None  # Placeholder for the final node ID

        # Parse the text file and build the mind map directly
        self.parse_text_file_to_graph(text_file)

    def wrap_text(self, text):
        """Wrap text into multiple lines based on max_line_length."""
        lines = []
        while len(text) > self.max_line_length:
            split_index = text[:self.max_line_length].rfind(" ")
            if split_index == -1:
                split_index = self.max_line_length
            lines.append(text[:split_index])
            text = text[split_index:].strip()
        lines.append(text)
        return "\n".join(lines)

    def parse_text_file_to_graph(self, text_file):
        """Parse the indented text file into a mind map structure."""
        with open(text_file, 'r') as f:
            lines = f.readlines()

        parent_stack = []  # Stack to maintain parent-child relationships
        prev_indent = 0  # Track previous line's indentation

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue  # Skip empty lines

            # Check if it's the final node
            if stripped_line.startswith("FINAL_NODE:"):
                final_text = stripped_line.replace("FINAL_NODE:", "").strip()
                final_display_text = self.wrap_text(final_text)
                
                # Create the final node
                self.final_node_id = f"node{self.node_counter}"
                self.node_counter += 1
                self.graph.node(self.final_node_id, final_display_text, style="filled", fillcolor=self.final_node_color, shape="ellipse")
                continue  # Skip connecting to parents, as it's a special node

            # Detect multiple parents syntax (e.g., "node text => parent1,parent2")
            if "=>" in stripped_line:
                node_text, parents = stripped_line.split("=>")
                parents = [p.strip() for p in parents.split(",")]
                stripped_line = node_text.strip()
            else:
                parents = None

            # Wrap text if it exceeds max_line_length
            display_text = self.wrap_text(stripped_line)

            # Calculate indentation level (number of leading spaces)
            indent_level = len(line) - len(stripped_line)

            # Create a new node for this line
            node_id = f"node{self.node_counter}"
            self.node_counter += 1

            # Determine node color: use a special color if it has multiple parents
            if parents:
                color = self.multi_parent_color
            else:
                color = self.level_colors[(indent_level // 2) % len(self.level_colors)]  # Color based on depth level

            # Add the node with the determined color and wrapped text
            self.graph.node(node_id, display_text, style="filled", fillcolor=color, shape="ellipse")
            self.leaf_nodes.add(node_id)  # Initially, assume each node is a leaf

            # Handle multiple parents if specified
            if parents:
                for parent_text in parents:
                    parent_id = self.node_dict.get(parent_text)
                    if parent_id:
                        self.graph.edge(parent_id, node_id, minlen="1")  # Set minlen to reduce arrow length
                        self.leaf_nodes.discard(parent_id)  # Remove parent from leaf nodes as it's not a leaf
            else:
                # Adjust parent-child relationships based on the indentation level
                if indent_level > prev_indent:
                    parent_stack.append(node_id)
                elif indent_level == prev_indent and parent_stack:
                    parent_stack.pop()
                    parent_stack.append(node_id)
                elif indent_level < prev_indent:
                    while len(parent_stack) > (indent_level // 2):
                        parent_stack.pop()
                    parent_stack.append(node_id)

                # If there's a parent, connect the current node to the parent
                if len(parent_stack) > 1:
                    self.graph.edge(parent_stack[-2], parent_stack[-1], minlen="1")  # Set minlen to reduce arrow length
                    self.leaf_nodes.discard(parent_stack[-2])  # Remove parent from leaf nodes as it's not a leaf

            # Save the node ID in node_dict for future reference
            self.node_dict[stripped_line] = node_id
            prev_indent = indent_level  # Update previous indentation level

    def generate_mind_map(self):
        """Generate the mind map from the parsed data."""
        # Connect all leaf nodes to the final node if it exists
        if self.final_node_id:
            for leaf in self.leaf_nodes:
                self.graph.edge(leaf, self.final_node_id, minlen="1")

    def view_mind_map(self, output_file):
        """Render the mind map to a file and view it."""
        self.graph.render(output_file, view=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a mind map from a text file.")
    parser.add_argument("folder", help="The folder containing the map.txt file.")
    args = parser.parse_args()

    # Build the path to the map.txt file in the specified folder
    text_file_path = os.path.join(args.folder, "map.txt")

    # Check if the text file exists and proceed
    if os.path.exists(text_file_path):
        # Create the mind map from the indented text file
        mind_map = MindMapFromIndentedText(text_file_path, max_depth=15, max_line_length=30)  # Set max_depth and max line length

        # Generate the mind map
        mind_map.generate_mind_map()

        # Automatically save the mind map with the same name as the text file in SVG format
        output_filename = os.path.join(args.folder, "mind_map")
        mind_map.view_mind_map(output_file=output_filename)
    else:
        print(f"Text file 'map.txt' not found in the folder '{args.folder}'.")
