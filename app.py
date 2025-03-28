import dash
import dash_bootstrap_components as dbc
import crystal_toolkit.components as ctc
from dash import dcc, html
from pymongo import MongoClient
from pymatgen.core.lattice import Lattice
from dash.dependencies import Input, Output
from pymatgen.core.structure import Structure

dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], requests_pathname_prefix='/dash/')

client = MongoClient("mongodb+srv://ECD517:bing24@cluster0.6nj4o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["CONTCAR_DATA"]



structures = [
    Structure(Lattice.hexagonal(1, 1), [], []),
]

def update_layout(selected_dopent, number):
    structures.clear()
    selected_dopent=f"{selected_dopent}{'-' if number == 0 else '+'}{number}" 
    collection=db[selected_dopent]
    stored_structure = collection.find_one()
    structure = Structure.from_dict(stored_structure)
    structures.append(structure) 


structure_component = ctc.StructureMoleculeComponent(structures[0], id="my_structure", show_expand_button=False )



my_button = html.Button(
    "Crystal Structure Viewer",
    id="change_structure_button",
    style={
        "background-color": "#4CAF50",
        "color": "white",
        "padding": "10px",
        "border": "none",
        "border-radius": "5px",
        "width": "100%",
        "margin-top": "15px",
        "margin-bottom": "15px",
    },
)

my_layout = html.Div(
    children=[
        my_button,
        structure_component.layout()
        
    ],
    style={
        'width': '100%',
        'max-width': '100%',
        'overflow': 'hidden',
        'padding': '0 10px',
        'display': 'flex',            
        'flexDirection': 'column',     
        'justifyContent': 'center',   
        'alignItems': 'center',       
        'height': '100vh',             
    }
)

ctc.register_crystal_toolkit(app=dash_app, layout=my_layout)


@dash_app.callback(
    Output(structure_component.id(), "data"),
    [Input("change_structure_button", "n_clicks")],
)
def update_structure(n_clicks):
    return structures[0]



if __name__ == "__main__":
    dash_app.run_server(port=8050, debug=True)