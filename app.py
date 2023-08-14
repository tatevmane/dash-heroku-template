import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
import plotly.io as pio
import jupyter_dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from scipy.stats import linregress  # Import linregress from scipy.stats
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

%%capture
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])
                                                  
## Generate the individual tables and figures
mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

### Markdown text
markdown_text = text1 = '''
The gender wage gap is a measure of what women are paid relative to men. After calculations, it is concluded that women are paid 82.7% of what men are paid. Over the years, this gap has decreased, but there is still a noticeable difference in earnings. The wage gap tells us about gender discrimination, especially when there are nearly identical employees getting paid different salaries solely due to sex. Belonging to a certain race does not change this experience for women.
Source = "https://www.epi.org/publication/what-is-the-gender-pay-gap-and-is-it-real/"
'''
text2 = "GSS, aka the General Social Survey, is one of the biggest social studies and a reliable source of data that helps to answer questions about demographics, trends, and behaviors in America. It has been conducted since 1972 and collects data through scientific surveys. "

### Table
agss_new = gss_clean[["sex", "education", "income", "job_prestige", "socioeconomic_index"]]
mean_gss = gss_new.groupby('sex').mean().round(2)

mean_gss.rename(columns = {
    'income': 'mean income',
    'job_prestige': 'mean job prestige',
    'socioeconomic_index': 'mean socioeconomic index',
    'education': 'mean education'}, inplace = True)

mean_gss.reset_index()
table = ff.create_table(mean_gss)

### Barplot
gss3 = gss_clean.groupby(['sex', 'male_breadwinner']).size().reset_index(name = 'Count')
gss_bar = px.bar(gss3,
              x = 'male_breadwinner',
              y = 'Count',
              color = 'sex',
             color_discrete_map = {'male':'blue', 'female':'red'},
             labels = {'male_breadwinner':'Level of Agreement'})

# Scatter
scatter = px.scatter(gss_clean,
                 x = 'job_prestige',
                 y = 'income',
                 color = 'sex',
                 trendline = 'ols',
                 opacity = 0.75,
                 labels = {'job_prestige': 'Occupational Prestige',
                          'income': 'Income'})

### box plots
income_boxplot = px.box(gss_new, 
                  x = 'income', 
                  color = 'sex',
                  labels = {'income':'Income Distribution'})
income_boxplot.update_layout(showlegend = False)

prestige_boxplot = px.box(gss_new, 
                  x = 'job_prestige', 
                  color = 'sex',
                  labels = {'job_prestige':'Distribution of Occupational Prestige'})
prestige_boxplot.update_layout(showlegend = False)

new_df = gss_clean[['income', 'sex', 'job_prestige']]
new_df['job_prestige_cat'] = pd.cut(new_df['job_prestige'], 
                                      bins = 6, 
                                      labels = ["Level 1", "Level 2", "Level 3", 
                                                "Level 4", "Level 5", "Level 6"])
new_df.dropna(inplace = True)


### Facets
levels = ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5','Level 6']
facet = px.box(new_df, 
              x = 'income', 
              color = 'sex', 
              color_discrete_map = {'male': 'blue', 'female': 'red'},
              facet_col = 'job_prestige_cat',
              facet_col_wrap = 2,
              labels = {'job_prestige_cat':'Level of Occupational Prestige',
                       'income':'Income'},
              category_orders = {'job_prestige_cat': levels}, 
)


# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Gender Distribution of Income and Occupational Prestige"),
    
    dcc.Markdown(text1),
    dcc.Markdown(text2),
    
    dcc.Graph(id='table', figure=table),  # Figure from problem 2
    
    dcc.Graph(id='graph', figure=gss_bar),  # Figure from problem 3
    
    dcc.Graph(id='scatterplot', figure=scatter),  # Figure from problem 4
    
    html.Div([
        dcc.Graph(id='income-boxplots', figure=income_boxplot),  # Figure from problem 5
        dcc.Graph(id='prestige-boxplots', figure=prestige_boxplot),  # Figure from problem 5
    ]),
    
    dcc.Graph(id='facet_boxplot', figure=facet),  # Figure from problem 6
    
     dcc.Dropdown(
        id='grouping',
        options=[
            {'label': 'Sex', 'value': 'sex'},
            {'label': 'Region', 'value': 'region'},
            {'label': 'Education', 'value': 'education'}
        ],
        value='sex',  # Set a default value
    ),
    
    dcc.Dropdown(
        id='variable',
        options=[
            {'label': var, 'value': var}
            for var in ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']
        ],
        value='satjob',  # Set a default value
    ),
    
    dcc.Graph(id='barplot'),
    
    dcc.Graph(id='table2') 
])

#@app.callback(
   # [dash.dependencies.Output('table', 'figure'),
   #  dash.dependencies.Output('graph', 'figure')],
   # [dash.dependencies.Input('grouping', 'value')]
#)
#def update_graphs(selected_grouping):
    # Grouping based on selected_grouping
#    grouped_data = gss_clean.groupby([selected_grouping]).mean()

    # Create figures using grouped_data
    
    # Return figures
 #   return table_figure, graph_figure


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8045)

