
from jupyter_dash import JupyterDash

import dash_leaflet as dl
from dash import dcc
from dash import html
import plotly.express as px
from dash import dash_table
from dash.dependencies import Input, Output
import base64
import pandas as pd

from animal_shelter import AnimalShelter

###########################
# Data Manipulation / Model
###########################
username = "aacuser"
password = "SNHU1234"

# Connect to CRUD
db = AnimalShelter(username, password)
df = pd.DataFrame.from_records(db.read({}))
if '_id' in df.columns:
    df.drop(columns=['_id'], inplace=True)  # Remove the '_id' column if it exists

#########################
# Dashboard Layout / View
#########################
app = JupyterDash(__name__)
image_filename = 'Logo.png'  # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.layout = html.Div([
    html.Center(html.B(html.H1('Chandler McCarty-CS-499 Remake'))),
    html.Hr(),
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode('utf-8')),
             style={'display': 'block', 'margin': 'auto', 'textAlign': 'center', 'width': '15%'}),
    html.Div("By Chandler McCarty 2024", style={'textAlign': 'center', 'fontSize': 18, 'color': '#860c0f'}),
    
    # Search bar
    dcc.Input(id='search-bar', type='text', placeholder='Search...', style={'marginBottom': '20px'}),
    
    html.Div(
        dcc.RadioItems(
            id='filter-type',
            options=[
                {'label': 'Water Rescue', 'value': 'Water Rescue'},
                {'label': 'Mountain or Wilderness Rescue', 'value': 'Mountain'},
                {'label': 'Disaster Rescue or Individual Tracking', 'value': 'Disaster'},
                {'label': 'Reset', 'value': 'Reset'},
            ],
            labelStyle={'display': 'block'}
        )
    ),
    
    html.Hr(),
    dash_table.DataTable(
        id='datatable-id',
        columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable=False,
        row_selectable="single",
        row_deletable=False,
        selected_rows=[0],
        selected_columns=[],
        page_action="native",
        page_current=0,
        page_size=10,
    ),
    html.Br(),
    html.Hr(),
    html.Div(className='row', style={'display': 'flex'}, children=[
        html.Div(id='graph-id', className='col s12 m6'),
        html.Div(id='map-id', className='col s12 m6'),
    ])
])

#############################################
# Interaction Between Components / Controller
#############################################

@app.callback([Output('datatable-id', 'data'),
               Output('datatable-id', 'columns')],
              [Input('filter-type', 'value'),
               Input('search-bar', 'value')])
def update_dashboard(filter_value, search_value):
    query = {}

    # Construct the base query based on the search input
    if search_value:
        query = {
            '$or': [
                {'breed': {'$regex': search_value, '$options': 'i'}},
                {'animal_type': {'$regex': search_value, '$options': 'i'}},
                {'sex_upon_outcome': {'$regex': search_value, '$options': 'i'}}
            ]
        }

    # Filter buttons for specifc rescues
    if filter_value == 'Water Rescue':
        query.update({
            "animal_type": "Dog",
            "breed": {"$in": ["Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland"]},
            "sex_upon_outcome": "Intact Female",
            "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156}
        })
    elif filter_value == 'Mountain':
        query.update({
            "animal_type": "Dog",
            "breed": {"$in": ["German Shepherd", "Alaskan Malamute", "Old English Sheepdog", "Siberian Husky", "Rottweiler"]},
            "sex_upon_outcome": "Intact Male",
            "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156}
        })
    elif filter_value == 'Disaster':
        query.update({
            "animal_type": "Dog",
            "breed": {"$in": ["Doberman Pinscher", "German Shepherd", "Golden Retriever", "Bloodhound", "Rottweiler"]},
            "sex_upon_outcome": "Intact Male",
            "age_upon_outcome_in_weeks": {"$gte": 20, "$lte": 300}
        })
    elif filter_value == 'Reset': #Reseting the filters
        query = {}

    # Filtered data from MongoDB
    df = pd.DataFrame.from_records(db.read(query))

    
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)

    columns = [{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns]

    return df.to_dict('records'), columns

@app.callback(
    Output('graph-id', "children"),
    [Input('datatable-id', "derived_virtual_data")])
def update_graphs(viewData):
    if viewData is None:
        return []

    df = pd.DataFrame(viewData)
    breed_counts = df['breed'].value_counts()

    return [
        dcc.Graph(
            figure=px.pie(names=breed_counts.index,
                          values=breed_counts.values,
                          title='Preferred Animals')
        )
    ]

@app.callback(
    Output('datatable-id', 'style_data_conditional'),
    [Input('datatable-id', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('map-id', "children"),
    [Input('datatable-id', "derived_virtual_data"),
     Input('datatable-id', "derived_virtual_selected_rows")])
def update_map(viewData, index):  
    if viewData is None:
        return
    elif index is None:
        return

    dff = pd.DataFrame.from_dict(viewData)
    if index is None:
        row = 0
    else: 
        row = index[0]
        
    # Austin TX is at [30.75,-97.48]
    return [
        dl.Map(style={'width': '1000px', 'height': '500px'}, center=[30.75, -97.48], zoom=10, children=[
            dl.TileLayer(id="base-layer-id"),
            dl.Marker(position=[dff.iloc[row, 13], dff.iloc[row, 14]], children=[
                dl.Tooltip(dff.iloc[row, 4]),
                dl.Popup([
                    html.H1("Animal Name"),
                    html.P(dff.iloc[row, 9])
                ])
            ])
        ])
    ]

app.run_server(debug=True)
