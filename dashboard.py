from mesa_viz_tornado.ModularVisualization import ModularServer
from mesa_viz_tornado.modules import CanvasGrid, ChartModule
from mesa_viz_tornado.UserParam import Slider
from model import TaxComplianceModel

def agent_portrayal(agent):
    """
    How agents appear on the grid.
    Red if evading, Blue if compliant.
    """
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Layer": 0
    }
    
    # Red if evading, Blue if compliant
    if agent.declared_profit >= agent.true_profit:
        portrayal["Color"] = "blue"
    else:
        portrayal["Color"] = "red"
        
    # Scale radius based on category: Micro (0.4) vs Small/Medium (0.8)
    portrayal["r"] = 0.4 if agent.category == "Micro" else 0.8
    
    return portrayal

# Dashboard Sliders; Slider(Label, Default, Min, Max, Step)
model_params = {
    "N": Slider("Number of SMEs", 100, 10, 500, 1),
    "audit_rate": Slider("Audit Rate", 0.07, 0.0, 0.3, 0.01),
    "penalty_rate": Slider("Penalty Multiplier", 3.0, 1.0, 6.0, 0.5),
    "social_influence": Slider("Social Influence (w)", 0.5, 0.0, 1.0, 0.1),
}

# Assemble Dashboard

# 1. Visual Grid (20x20 cells, 500x500 pixels)
grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500) # Same height and width as the TaxComplianceModel grid

# 2. Charts
chart = ChartModule([
    {"Label": "Tax Gap", "Color": "Black"},
    {"Label": "Compliance Rate", "Color": "Blue"}
])

# 3. Initialize the Server
server = ModularServer(
    TaxComplianceModel,
    [grid, chart],
    "Belastingdienst SME Simulator",
    model_params
)

# Launch
server.port = 8521 # change if busy
server.launch()