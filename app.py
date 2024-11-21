# dash_app.py
import dash
import dash_bootstrap_components as dbc
import crystal_toolkit.components as ctc
from dash import dcc, html
from pymongo import MongoClient
from pymatgen.core.lattice import Lattice
from dash.dependencies import Input, Output
from pymatgen.core.structure import Structure


# Initialize Dash app with Bootstrap theme and requests pathname prefix
dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], requests_pathname_prefix='/dash/')

# Connect to MongoDB
client = MongoClient("mongodb+srv://ECD517:bing24@cluster0.6nj4o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["vasp_data"]
# now we give a list of structures to pick from



structures = [
    Structure(Lattice.hexagonal(5, 3), ["Na", "Cl"], [[0, 0, 0], [0.5, 0.5, 0.5]]),
]

def update_layout(selected_dopent):
    structures.clear()
    collection=db[selected_dopent]
    stored_structure = collection.find_one()
    structure = Structure.from_dict(stored_structure['structure'])
    structures.append(structure)



# we show the first structure by default
structure_component = ctc.StructureMoleculeComponent(structures[0], id="my_structure")

# and we create a button for user interaction
my_button = html.Button(
    "Update Structure",
    id="change_structure_button",
    style={
        "background-color": "#4CAF50",
        "color": "white",
        "padding": "10px",
        "border": "none",
        "cursor": "pointer",
        "border-radius": "5px",
        "width": "100%",
        "margin-top": "15px",
    },
)


# now we have two entries in our app layout,
# the structure component's layout and the button
my_layout = html.Div(
    children=[
        structure_component.layout(),
        my_button
    ],
    style={
        'width':'100%',
        'max-width': '78%',  # Prevents layout from exceeding the container width
        'overflow': 'hidden',  # Prevents overflow if any element tries to exceed bounds
        'padding': '0 10px'  # Adjust padding for spacing
    }
)

ctc.register_crystal_toolkit(app=dash_app, layout=my_layout)


# for the interactivity, we use a standard Dash callback
@dash_app.callback(
    Output(structure_component.id(), "data"),
    [Input("change_structure_button", "n_clicks")],
)
def update_structure(n_clicks):
    return structures[0]


if __name__ == "__main__":
    dash_app.run_server(port=8050, debug=True)