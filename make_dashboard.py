#!/usr/bin/env python
# script to connect to API, extract character gender data and create a dashboard
# @saevrenk, 03.06.23
import plotly.express as px
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import pandas as pd
import os
import plotly_express as px
from collections import Counter
import datetime as dt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from api_funcs import connectAPI


# Connect to the Rick and Morty API and build dataframes
df_rm_character = connectAPI("RICKMORTYAPI", "character").get_results_df()
df_rm_episode = connectAPI("RICKMORTYAPI", "episode").get_results_df()

# Connect to the Star Wars API and build dataframes
df_sw_films = connectAPI("SWAPI", "films").get_results_df()
df_sw_people = connectAPI("SWAPI", "people").get_results_df()

# Connect to the movie db API and build dataframe
if not os.path.exists("./df_tmdb_people.csv"):
    df_tmdb_people = connectAPI("TMDBAPI", "person").get_results_df()
    df_tmdb_people.to_csv("df_tmdb_people.csv")
else:
    df_tmdb_people = pd.read_csv("df_tmdb_people.csv")

# clean up
df_sw_people["gender"][df_sw_people["gender"] == "none"] = "Not Specified"
df_sw_people["gender"][df_sw_people["gender"] == "n/a"] = "Genderless"
df_rm_character["gender"][df_rm_character["gender"] == "Unknown"] = "Not Specified"

df_rm_character["gender"] = df_rm_character["gender"].str.capitalize()
df_sw_people["gender"] = df_sw_people["gender"].str.capitalize()

# Total gender distributions:
sw = pd.DataFrame(df_sw_people["gender"].value_counts()).reset_index()
rm = pd.DataFrame(df_rm_character["gender"].value_counts()).reset_index()
md = pd.DataFrame(df_tmdb_people["gender"].value_counts())
df_temp = df_tmdb_people.groupby("gender").sum()
md["Total Credits"] = df_temp["n_credits"]
md = md.reset_index()

# create an images directory for saving images
if not os.path.exists("images"):
    os.mkdir("images")


### DASH ####

# style sheet
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

# start app
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "gender-in-movies"

app.layout = html.Div(
    [
        html.H1("Gender Distributions in Movies"),
        dcc.Dropdown(
            id="movie_dropdown",
            options=[
                {"label": "Star Wars", "value": 0},
                {"label": "Rick and Morty", "value": 1},
                {"label": "Movie DB characters", "value": 2},
                {"label": "Movie DB Total Credits", "value": 3},
            ],
            multi=False,
            value=0,
            style={"width": "60%"},
        ),
        dcc.Graph(id="pie", figure={}),
    ]
)


@app.callback(Output("pie", "figure"), [Input("movie_dropdown", "value")])
def draw_graph(user_selection):
    titles = [
        "Star Wars",
        "Rick & Morty",
        "Movie DB characters",
        "Movie DB Total Credits",
    ]
    dfs = [sw, rm, md, md]
    i = user_selection
    if i == 3:
        variable = "Total Credits"
    else:
        variable = "gender"
    fig = px.pie(
        dfs[i], values=variable, names="index", title=titles[i], width=600, height=400
    )
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=-0.5))
    return fig


# if __name__ == "__main__":
app.run_server()
