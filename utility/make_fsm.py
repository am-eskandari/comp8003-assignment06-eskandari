# Create a refined FSM diagram with the proposed improvements
from graphviz import Digraph

fsm_refined = Digraph("Refined File Integrity Monitoring FSM", format="png")

# Define updated states including validation and logging
states_refined = [
    "START", "PARSE_ARGS", "HANDLE_ARGS", "VALIDATE_ARGS", "USAGE",
    "GENERATE_BASELINE", "CHECK_INTEGRITY", "DISPLAY_REPORT",
    "LOGGING", "CLEANUP", "EXIT"
]

# Add states to the graph
for state in states_refined:
    if state in ["START", "EXIT"]:
        fsm_refined.node(state, shape="circle")  # Start and Exit states as circles
    else:
        fsm_refined.node(state, shape="box")  # Other states as boxes

# Define improved transitions including validation and logging
transitions_refined = [
    ("START", "PARSE_ARGS", "parse_arguments"),
    ("PARSE_ARGS", "HANDLE_ARGS", "handle_arguments"),
    ("PARSE_ARGS", "USAGE", "usage"),
    ("HANDLE_ARGS", "VALIDATE_ARGS", "validate_arguments"),
    ("VALIDATE_ARGS", "GENERATE_BASELINE", "generate_baseline"),
    ("VALIDATE_ARGS", "CHECK_INTEGRITY", "check_integrity"),
    ("VALIDATE_ARGS", "DISPLAY_REPORT", "display_report"),
    ("VALIDATE_ARGS", "USAGE", "invalid input"),  # If validation fails, go to usage
    ("USAGE", "EXIT", "invalid args"),  # Directly exit if usage is shown
    ("GENERATE_BASELINE", "LOGGING", "handle file errors"),
    ("CHECK_INTEGRITY", "LOGGING", "handle file errors"),
    ("LOGGING", "CLEANUP", "log complete"),
    ("DISPLAY_REPORT", "CLEANUP", "report displayed"),
    ("CLEANUP", "EXIT", "cleanup complete"),
]

# Add transitions to the refined graph
for start, end, label in transitions_refined:
    fsm_refined.edge(start, end, label)

# Render and display the refined FSM diagram
fsm_refined_path = "/mnt/data/fsm_refined_diagram"
fsm_refined.render(fsm_refined_path, format="png")

# Display the updated FSM diagram
import IPython.display as display
display.Image(fsm_refined_path + ".png")
