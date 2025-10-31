import dash
from dash import html, dcc

google_font_roboto = "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap"

app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True, external_stylesheets=[google_font_roboto ,'assets/styles.css'])
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1('Explorados Base de Datos Mundial', className='titulo-principal'),

        # nav
        html.Div([
            dcc.Link('Tablas', href='/', className='nav-link'),
            dcc.Link('Dashboard', href='/dashboard', className='nav-link'),
        ], className='opciones')
    ], className='nav'),

    dash.page_container
], className='body')

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8050)