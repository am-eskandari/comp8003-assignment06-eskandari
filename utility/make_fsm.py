from graphviz import Digraph

# Define FSM diagram
fsm = Digraph("File Integrity Monitoring FSM", format="png")
fsm.attr(
    rankdir="TB", size="8,12", dpi="300"
)  # Force portrait mode with proper spacing

# Define states with shape adjustments
fsm.node("START", "START", shape="circle", style="bold")
fsm.node("PARSE_ARGS", "PARSE_ARGS", shape="box")
fsm.node("HANDLE_ARGS", "HANDLE_ARGS", shape="box")
fsm.node("USAGE", "USAGE", shape="box")
fsm.node("GENERATE_BASELINE", "GENERATE_BASELINE", shape="box")
fsm.node("CHECK_INTEGRITY", "CHECK_INTEGRITY", shape="box")
fsm.node("DISPLAY_REPORT", "DISPLAY_REPORT", shape="box")
fsm.node("CLEAR_REPORT", "CLEAR_REPORT", shape="box")
fsm.node("CLEANUP", "CLEANUP", shape="box")
fsm.node("EXIT", "EXIT", shape="doublecircle", style="bold")

# Define transitions from the state table
fsm.edge("START", "PARSE_ARGS", label="parse_args")

fsm.edge("PARSE_ARGS", "HANDLE_ARGS", label="handle_args")
fsm.edge("PARSE_ARGS", "USAGE", label="usage")

fsm.edge("HANDLE_ARGS", "GENERATE_BASELINE", label="generate_baseline")
fsm.edge("HANDLE_ARGS", "CHECK_INTEGRITY", label="check_integrity")
fsm.edge("HANDLE_ARGS", "DISPLAY_REPORT", label="display_report")
fsm.edge("HANDLE_ARGS", "CLEAR_REPORT", label="clear_report")
fsm.edge("HANDLE_ARGS", "USAGE", label="usage")

fsm.edge("GENERATE_BASELINE", "CLEANUP", label="cleanup")
fsm.edge("CHECK_INTEGRITY", "CLEANUP", label="cleanup")
fsm.edge("DISPLAY_REPORT", "CLEANUP", label="cleanup")
fsm.edge("CLEAR_REPORT", "CLEANUP", label="cleanup")
fsm.edge("USAGE", "CLEANUP", label="cleanup")

fsm.edge("CLEANUP", "EXIT", label="end execution")

# Render the FSM diagram locally
fsm_path = "fsm_diagram"
fsm.render(fsm_path)

print(f"FSM diagram generated: {fsm_path}.png")
