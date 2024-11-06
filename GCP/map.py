import os
from graphviz import Digraph

class MindMapFromIndentedText:
    def __init__(self, text_file, max_depth=None):
        self.text_file = text_file
        self.graph = Digraph(comment="Mind Map", format='svg')  # Use SVG for better scalability
        self.graph.attr(rankdir='LR')  # Set graph direction to Left-to-Right (horizontal layout)
        self.node_counter = 0
        self.level_colors = ["lightblue", "lightgreen", "lightcoral", "lightyellow", "lightpink", "lightgrey"]
        self.max_depth = max_depth  # Optional: Limit visualization depth
        self.node_dict = {}  # Dictionary to keep track of nodes by level

        # Parse the text file and build the mind map directly
        self.parse_text_file_to_graph(text_file)

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

            # Calculate indentation level (number of leading spaces)
            indent_level = len(line) - len(stripped_line)

            # Create a new node for this line
            node_id = f"node{self.node_counter}"
            self.node_counter += 1
            color = self.level_colors[(indent_level // 2) % len(self.level_colors)]  # Color based on depth level
            self.graph.node(node_id, stripped_line, style="filled", fillcolor=color, shape="ellipse")

            # Adjust parent-child relationships based on the indentation level
            if indent_level > prev_indent:
                # The current node is a child of the previous node
                parent_stack.append(node_id)
            elif indent_level == prev_indent and parent_stack:
                # The current node is a sibling, so pop the last child and create a new sibling
                parent_stack.pop()
                parent_stack.append(node_id)
            elif indent_level < prev_indent:
                # The current node is a sibling of a higher level, so pop until we reach the right parent
                while len(parent_stack) > (indent_level // 2):
                    parent_stack.pop()
                parent_stack.append(node_id)

            # If there's a parent, connect the current node to the parent
            if len(parent_stack) > 1:
                self.graph.edge(parent_stack[-2], parent_stack[-1])

            prev_indent = indent_level  # Update previous indentation level

    def generate_mind_map(self):
        """Generate the mind map from the parsed data."""
        # Implicitly done during graph creation, so no need to add extra logic here.

    def view_mind_map(self, output_file):
        """Render the mind map to a file and view it."""
        self.graph.render(output_file, view=True)


if __name__ == "__main__":
    # Define the input text file
    text_filename = 'map.txt'  # Change this to your actual text file name

    # Get the absolute path of the current folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    text_file_path = os.path.join(script_dir, text_filename)

    # Check if the text file exists and proceed
    if os.path.exists(text_file_path):
        # Create the mind map from the indented text file
        mind_map = MindMapFromIndentedText(text_file_path, max_depth=15)  # Set max_depth to limit the levels visualized

        # Generate the mind map
        mind_map.generate_mind_map()

        # Automatically save the mind map with the same name as the text file in SVG format
        output_filename = os.path.splitext(text_filename)[0]  # Strip the extension
        output_filepath = os.path.join(script_dir, output_filename)

        # View and save the generated mind map as an SVG image
        mind_map.view_mind_map(output_file=output_filepath)
    else:
        print(f"Text file '{text_filename}' not found in the current directory.")
