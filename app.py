# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from mysql_utils import sql_db_data
from mongodb_utils import mongo_db_data
from neo4j_utils import neo4j_data
import re

# Incorporate university data from SQL
df_universities = sql_db_data('SELECT * FROM university;')

# Incorporate data from MongoDB
df_mongo_publications = mongo_db_data('publications')

# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div('University Guide', className="header-section")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H4('Select University'),
            dcc.Dropdown(
                id='university-dropdown',
                options=[{'label': row['name'], 'value': row['name']} for _, row in df_universities.iterrows()],
                value='',
                style={'width': '100%'}
            ),
            html.Div(id='university-info', className='mt-3')
        ], width=6, className='bordered-section'),

        dbc.Col([
            html.H4('Faculty Data'),
            dcc.Input(id='faculty-search', type='text', placeholder='Search faculty by name...', style={'width': '100%'}),
            dash_table.DataTable(
                id='faculty-table',
                page_size=5,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                editable=True,
            ),
            html.Button('Save Changes', id='save-faculty-changes', n_clicks=0, style={'marginTop': '10px'}),
        ], width=6, className='bordered-section'),
    ], className='mt-4'),

    dbc.Row([
        dbc.Col([
            html.H4('Top Collaborators'),
            html.Div(id='top-collaborators-table')
        ], width=6, className='bordered-section'),

        dbc.Col([
            html.H4('Select Keyword'),
            dcc.Dropdown(
                id='keywords-dropdown',
                options=[],
                style={'width': '100%'}
            ),
            dash_table.DataTable(
                id='keywords-table',
                page_size=5,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
            )
        ], width=6, className='bordered-section'),
    ], className='mt-4'),

    dbc.Row([
        dbc.Col([
            html.H4('Publications Data'),
            dcc.Input(id='publications-search', type='text', placeholder='Search publications by title or venue...', style={'width': '100%'}),
            dash_table.DataTable(
                id='publications-table',
                page_size=5,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                editable=True,
            ),
            html.Button('Save Changes', id='save-publications-changes', n_clicks=0, style={'marginTop': '10px'}),
        ], width=6, className='bordered-section'),

        dbc.Col([
            html.H4('Top Faculty Members Citations (By Selected Keyword)'),
            html.Div(id='top-faculty-table')
        ], width=6, className='bordered-section'),
    ], className='mt-4'),
    
], fluid=True)

# Add controls to build the interaction
@callback(
    Output('university-info', 'children'),
    Input('university-dropdown', 'value')
)
def choose_university(selected_university):
    # Choose a university from dropdown menu that then displays the name, photo, and saves it
    if selected_university:
        matching_universities = df_universities[df_universities['name'] == selected_university]
        if not matching_universities.empty:
            
            university_name = matching_universities.iloc[0]['name']
            university_logo = matching_universities.iloc[0].get('photo_url')
            
            return [
                html.Img(src=university_logo, height='100px'),
                html.H5(university_name)
            ]
    return "No University selected."


@callback(
    Output('keywords-dropdown', 'options'),
    Output('keywords-dropdown', 'value'),
    Input('university-dropdown', 'value')
)
def choose_keyword(selected_university):
    # Choose a keyword from chosen university, used in other widgets
    if selected_university:
        query = f"""
        SELECT DISTINCT keyword 
        FROM university_keywords_view
        WHERE university_name = %s
        """
        df_keywords = sql_db_data(query, (selected_university,))
        
        options = [{'label': keyword, 'value': keyword} for keyword in df_keywords['keyword']]
        return options, None
    return [], None
    """
    View Used in MySQL Database:
    CREATE VIEW university_keywords_view AS
    SELECT u.name AS university_name, k.name AS keyword
    FROM university u
    JOIN faculty f ON u.id = f.university_id
    JOIN faculty_keyword fk ON f.id = fk.faculty_id
    JOIN keyword k ON fk.keyword_id = k.id;
    """


client = MongoClient('mongodb://localhost:27017/')
db = client['academicworld']
faculty_collection1 = db['faculty']
faculty_collection2 = db['publications']

@callback(
    Output('faculty-table', 'data'),
    Output('faculty-table', 'columns'),
    Input('faculty-search', 'value'),
    Input('university-dropdown', 'value'),
    Input('faculty-table', 'data_timestamp'),
    Input('faculty-table', 'data'),
    Input('save-faculty-changes', 'n_clicks'),
    State('faculty-table', 'data')
)
def search_update_faculty_members(search_value, selected_university, timestamp, rows, save_clicks, current_data):
    # Search & edit faculty members based on selected university and search input
    if selected_university:
        pipeline = [
            {"$match": {"affiliation.name": selected_university}},
            {"$project": {"_id": 0, "name": 1, "phone": 1, "email": 1}},
            {"$sort": {"name": 1}}
        ]
        
        df_filtered_faculty = mongo_db_data('faculty', pipeline=pipeline)
        
        if search_value:
            escaped_search_value = re.escape(search_value)
            df_filtered_faculty = df_filtered_faculty[
                df_filtered_faculty['name'].str.contains(escaped_search_value, case=False, na=False)
            ]
        
        if save_clicks > 0 and current_data:
            df_updated = pd.DataFrame(current_data)
            
            for _, updated_row in df_updated.iterrows():
                original_row = df_filtered_faculty[df_filtered_faculty['name'] == updated_row['name']].iloc[0]
                
                if original_row['phone'] != updated_row['phone']:
                    faculty_collection1.update_one(  # Update phone number in DB
                        {'name': updated_row['name']}, {'$set': {'phone': updated_row['phone']}}
                    )
            
            # Re-fetch data to show changes
            df_filtered_faculty = mongo_db_data('faculty', pipeline=pipeline)
        
        columns = [
            {'name': col, 'id': col, 'editable': col == 'phone'} for col in df_filtered_faculty.columns
        ]
        return df_filtered_faculty.to_dict('records'), columns
    
    return [], []


@callback(
    Output('publications-table', 'data'),
    Output('publications-table', 'columns'),
    Input('publications-search', 'value'),
    Input('keywords-dropdown', 'value'),
    Input('publications-table', 'data_timestamp'),
    Input('publications-table', 'data'),
    Input('save-publications-changes', 'n_clicks'),
    State('publications-table', 'data')
)
def search_update_publications_table(publications_search_value, selected_keyword, timestamp, rows, save_clicks, current_data):
    # Search & edit publications based on selected university, keyword and search input
    pipeline = [
        {
            '$match': {
                'keywords.name': selected_keyword
            }
        },
        {
            '$project': {
                '_id': 0,
                'title': 1,
                'venue': 1,
                'year': 1,
                'numCitations': 1,
                'keywords': {
                    '$map': {
                        'input': '$keywords',
                        'as': 'keyword',
                        'in': '$$keyword.name'
                    }
                }
            }
        }
    ]
    
    df_publications = mongo_db_data('publications', pipeline=pipeline)

    if publications_search_value:
        escaped_search_value = re.escape(publications_search_value)
        df_publications = df_publications[
            df_publications['title'].str.contains(escaped_search_value, case=False, na=False) |
            df_publications['venue'].str.contains(escaped_search_value, case=False, na=False)
        ]
        
    columns = [
        {'name': col, 'id': col, 'editable': col == 'venue'} for col in df_publications.columns
    ]
    
    if save_clicks > 0 and current_data:
        df_updated = pd.DataFrame(current_data)
        
        for _, updated_row in df_updated.iterrows():
            if 'title' in updated_row and 'venue' in updated_row:
                updated_title = updated_row['title']
                updated_venue = updated_row['venue']
                
                if updated_title and updated_venue:
                    result = faculty_collection2.update_one(  # Update venue in DB
                        {'title': updated_title}, 
                        {'$set': {'venue': updated_venue}}
                    )

        # Re-fetch data to show changes
        df_publications = mongo_db_data('publications', pipeline=pipeline)

    return df_publications.to_dict('records'), columns


@callback(
    Output('top-collaborators-table', 'children'),
    Input('university-dropdown', 'value')
)
def top_collaborators(selected_university):
    # Show pie graph of top collaborators based on selected university
    if selected_university:
        query = f"""
        MATCH (other_university:INSTITUTE {{name: '{selected_university}'}})<-[:AFFILIATION_WITH]-(other_faculty:FACULTY)-[:PUBLISH]->(:PUBLICATION)<-[:PUBLISH]-(faculty:FACULTY)-[:AFFILIATION_WITH]->(university:INSTITUTE)
        WHERE other_university <> university
        RETURN university.name AS university_name, COUNT(DISTINCT other_faculty) AS faculty_count
        ORDER BY faculty_count DESC
        LIMIT 10
        """
        df_top_collaborators = neo4j_data(query)
        fig = px.pie(df_top_collaborators, names='university_name', values='faculty_count', 
                     title='Top Faculty Collaborators')
        
        return dcc.Graph(figure=fig)
    return "No University selected."


@callback(
    Output('top-faculty-table', 'children'),
    Input('university-dropdown', 'value'),
    Input('keywords-dropdown', 'value')
)
def top_faculty(selected_university, selected_keyword):
    # Show bar graph of top faculty members citations based on selected university and keyword
    if selected_university and selected_keyword:
        query = f"""
        MATCH (university:INSTITUTE {{name: '{selected_university}'}})
        <-[:AFFILIATION_WITH]-(faculty:FACULTY)
        -[:PUBLISH]->(publication:PUBLICATION)
        -[label_by:LABEL_BY]->(keyword:KEYWORD {{name: '{selected_keyword}'}})
        WITH faculty, publication, label_by.score AS score, publication.numCitations AS citations
        WITH faculty, SUM(score * citations) AS accumulated_citations
        ORDER BY accumulated_citations DESC
        LIMIT 10
        RETURN faculty.name AS name, accumulated_citations
        """
        # Indexes used to speed things up a little on Neo4J database:
        # CREATE INDEX institute_name_idx FOR (n:INSTITUTE) ON (n.name);
        # CREATE INDEX keyword_name_idx FOR (k:KEYWORD) ON (k.name);

        df_top_faculty = neo4j_data(query)
        
        if not df_top_faculty.empty:
            # Convert accumulated citations to nums & force errors to NaN then drop them
            df_top_faculty['accumulated_citations'] = pd.to_numeric(df_top_faculty['accumulated_citations'], errors='coerce')
            df_top_faculty = df_top_faculty.dropna(subset=['accumulated_citations'])
            
            fig = px.bar(df_top_faculty, x='name', y='accumulated_citations',
                        labels={'name': 'Faculty Member Name', 'accumulated_citations': 'Accumulated Citations'})
            
            # Make y-axis start at 0
            fig.update_layout(yaxis=dict(range=[0, df_top_faculty['accumulated_citations'].max() + 10]))
            
            return dcc.Graph(figure=fig)
    
    return html.Div()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
