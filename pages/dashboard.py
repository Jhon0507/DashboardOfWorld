import dash
from dash import dcc, html, callback, Input, Output
import plotly.express as px
from db_utils import fetch_data

# registrar la pagina como la ruta principal
dash.register_page(__name__, path='/dashboard', name='Dashboard')

# definir el layout de la pagina
def layout():
    return html.Div([

        # Contenedor de gráficos 1
        html.Div([
            html.Div([
                dcc.Graph(id='graph-gnp-choropleth', style={'height': '600px', 'width': '100%'})
            ], className='grafico-1-hijo')
        ], className='grafico-1'),

        # Contenedor de gráficos 2
        html.Div([
            html.Div([
                dcc.Graph(id='graph-top-countries')
            ], className='columna-mitad'),
            html.Div([
                dcc.Graph(id='graph-pop-continent-pie')
            ], className='columna-mitad')
        ], className='filas-principales grafico-2'),

        # Contenedor de gráficos 3
        html.Div([
            # lado izquierdo
            html.Div([
                html.Div([
                    dcc.Graph(id='graph-top-cities')
                ], className='columna-stacked'),
                html.Div([
                    dcc.Graph(id='graph-language-dist')
                ], style={'width': '100%'})
            ], className='columna-mitad'),

            # lado derecho
            html.Div([
                dcc.Graph(id='graph-lifeexp-vs-gnp', style={'height': '800px'})
            ], className='columna-mitad')
        ], className='filas-principales'),

        # contenedor de gráficos 4
        html.Div([
            html.Div([
                dcc.Graph(id='graph-govform-dist')
            ], className='columna-mitad'),
            html.Div([
                dcc.Graph(id='graph-surface-continent')
            ], className='columna-mitad')
        ], className='filas-principales')
    ], )

# Callbacks de todos los gráficos

# Callback Mapa GNP
@callback(Output('graph-gnp-choropleth', 'figure'), Input('graph-gnp-choropleth', 'id'))
def cargar_gnp_mapa(_):
    query = 'SELECT Code, Name, GNP FROM country WHERE GNP IS NOT NULL AND GNP > 0;'
    df = fetch_data(query)
    if df.empty: return px.choropleth(title='Error al cargar datos de GNP')
    fig = px.choropleth(df,
                        locations='Code',
                        color='GNP',
                        hover_name='Name',
                        color_continuous_scale=px.colors.sequential.Blues_r,
                        labels={'GNP': 'GNP (USD)'})
    fig.update_layout(
        title_x=0.5,
        title={
            'text': '<b>Producto Nacional Bruto (GNP) por País</b>',
            'font': {'size': 20, 'family': "'Roboto', sans-serif"}
        },
        margin={'r':0, 't':40, 'l':0, 'b':0},
        geo=dict(
            showframe=False,  # Ocultar el marco alrededor del mapa
            showcoastlines=False,  # Ocultar costas (opcional, a veces mejora claridad)
            bgcolor='rgba(240, 240, 240, 1)',  # Color de fondo del área geo (gris claro)
            landcolor='rgb(217, 217, 217)',  # Color para tierra sin datos (gris claro)
        )
    )
    return fig

# Callback top 15 paises
@callback(Output('graph-top-countries', 'figure'), Input('graph-top-countries', 'id'))
def cargar_top_paises(_):
    query = 'SELECT Name, Population, Continent FROM country ORDER BY Population DESC LIMIT 15;'
    df = fetch_data(query)
    if df.empty: return px.bar(title='Error al cargar los datos de los paises')
    fig = px.bar(df.sort_values('Population', ascending=True),
                 x='Population', y='Name', orientation='h',
                 labels={'Population': 'Población', 'Name': 'País'}, color='Continent', height=400)
    fig.update_layout(
        title_x=0.5,
        title={
            'text': '<b>Top 15 paises por población</b>',
            'font': {'size': 20, 'family': "'Roboto', sans-serif"}
        },
        margin={'r':0, 't':40, 'l':0, 'b':0}
    )
    return fig

# población por continente
@callback(Output('graph-pop-continent-pie', 'figure'), Input('graph-pop-continent-pie', 'id'))
def cargar_poblacion_por_continente(_):
    query = 'SELECT Continent, SUM(Population) as TotalPopulation FROM country GROUP BY Continent ORDER BY TotalPopulation DESC;'
    df = fetch_data(query)
    if df.empty: return px.pie(title='Error al cargar datos de población')
    fig = px.pie(df, values='TotalPopulation', names='Continent', hole=0.3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        title_x=0.5,
        title={
            'text': '<b>Población por continente</b>',
            'font': {'size': 20, 'family': "'Roboto', sans-serif"}
        },
        margin={'r': 0, 't': 40, 'l': 0, 'b': 0},
        height=400
    )
    return fig

# top 10 de ciudades por población
@callback(Output('graph-top-cities', 'figure'), Input('graph-top-cities', 'id'))
def cargar_top_paises(_):
    query = 'SELECT Name, Population, CountryCode FROM city ORDER BY Population DESC LIMIT 10;'
    df = fetch_data(query)
    if df.empty: return px.bar(title='Error al cargar los datos de las ciudades')
    fig = px.bar(df.sort_values('Population', ascending=True),
                 x='Population', y='Name', orientation='h',
                 labels={'Population': 'Población', 'Name': 'Ciudad'}, color='CountryCode', height=380)
    fig.update_layout(
        title_x=0.5,
        title={
            'text': '<b>Top 10 ciudades por población</b>',
            'font': {'size':20, 'family': "'Roboto', sans-serif"}
        },
        margin={'r':0, 't':40, 'l':0, 'b':0},
        showlegend=False
    )
    return fig

# top 10 distribución de idiomas
@callback(Output('graph-language-dist', 'figure'), Input('graph-language-dist', 'id'))
def cargar_distribucion_idiomas(_):
    query = '''
    SELECT Language, SUM(Percentage)/100 * SUM(c.Population/1000000) AS WeightedSpeakersM
    FROM countrylanguage cl
    JOIN country c ON cl.CountryCode = c.code
    WHERE cl.Percentage > 0
    GROUP BY Language
    ORDER BY WeightedSpeakersM DESC
    LIMIT 10;
    '''
    df = fetch_data(query)
    if df.empty: return px.bar(title='Error al cargar datos de idiomas')
    fig = px.bar(df.sort_values('WeightedSpeakersM', ascending=True),
                 x='WeightedSpeakersM', y='Language', orientation='h',
                 labels={'WeightedSpeakersM': 'Hablantes Estimados (M)', 'Language': 'Idioma'}, height=380)
    fig.update_layout(
        title_x=0.5,
        title={
            'text': '<b>Top 10 idiomas (Estimación en Millones)</b>',
            'font': {'size':20, 'family': "'Roboto', sans-serif"}
        },
        margin={'r': 0, 't': 40, 'l': 0, 'b': 0},
    )
    return fig

#  Esperanza de vida versus GNP
@callback(Output('graph-lifeexp-vs-gnp', 'figure'), Input('graph-lifeexp-vs-gnp', 'id'))
def cargar_esperanza_vida_vs_gnp(_):
    query = '''
    SELECT Name, LifeExpectancy, GNP, Population, Continent
    FROM country
    WHERE LifeExpectancy IS NOT NULL AND GNP IS NOT NULL AND GNP > 0 AND Population > 0;
    '''
    df = fetch_data(query)
    if df.empty: return px.scatter(title='Error al cargar datos Esperanza de vida/GNP')
    fig = px.scatter(df, x='GNP', y='LifeExpectancy', size='Population', color='Continent',
                     hover_name='Name', log_x=True, size_max=60,
                     labels={'GNP': 'GNP (USD, log)', 'LifeExpectancy': 'Esperanza de Vida (años)'})
    fig.update_layout(
        title_x=0.5,
        title={
            'text': '<b>Esperanza de vida vs GNP (Tamaño = Población)</b>',
            'font': {'size': 20, 'family': "'Roboto', sans-serif"}
        },
        margin={'r': 0, 't': 40, 'l': 0, 'b': 0},
    )
    return fig

# Formas de Gobierno
@callback(Output('graph-govform-dist', 'figure'), Input('graph-govform-dist', 'id'))
def cargar_forma_govierno_distribucion(_):
    query = 'SELECT GovernmentForm, COUNT(*) as Count FROM country GROUP BY GovernmentForm ORDER BY Count DESC LIMIT 15;'
    df = fetch_data(query)
    if df.empty: return px.bar(title='Error al cargar formas de govierno')
    fig = px.bar(df.sort_values('Count', ascending=False),
                 x= 'GovernmentForm', y='Count',
                 labels={'Count': 'Nº Paises', 'GovernmentForm': 'Forma de Gobierno'}, height=400)
    fig.update_layout(
        title_x=0.5,
        title={
            'text': '<b>Distribución Formas de Gobierno (Top 15)</b>',
            'font': {'size': 20, 'family': "'Roboto', sans-serif"}
        },
        margin={'r': 0, 't': 40, 'l': 0, 'b': 0},
    )
    return fig

# Superficie por continente
@callback(Output('graph-surface-continent', 'figure'), Input('graph-surface-continent', 'id'))
def cargar_superficie_por_continente(_):
    query = 'SELECT Continent, SUM(SurfaceArea) as TotalSurface FROM country GROUP BY Continent ORDER BY TotalSurface DESC;'
    df = fetch_data(query)
    if df.empty: return px.bar(title='Error al cargar datos de superficie')
    fig = px.bar(df.sort_values('TotalSurface', ascending=False),
                 x='Continent', y='TotalSurface',
                 labels={'TotalSurface': 'Superficie (Km²)', 'Continent': 'Continente'}, height=400)
    fig.update_layout(
        title_x=0.5,
        title={
            'text': '<b>Superficie total por continente</b>',
            'font': {'size': 20, 'family': "'Roboto', sans-serif"}
        },
        margin={'r': 0, 't': 40, 'l': 0, 'b': 0},
    )
    return fig