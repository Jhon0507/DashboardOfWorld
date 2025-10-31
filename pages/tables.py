import dash
from dash import dcc, html, dash_table, callback, Input, Output, State
from db_utils import fetch_data, get_table_names, get_table_columns, parse_filter_query_named_params

dash.register_page(__name__, path='/', name='Tablas Detalladas')

PAGE_SIZE = 15 # limite de datos mostrados por tabla

# Generación Dinámica del Layout
def create_dynamic_layout():

    table_names = get_table_names()
    layout_children = [
        html.H2("Exploración Dinámica de Tablas de la Base de Datos", style={'textAlign': 'center', 'marginTop': '0', 'paddingTop': '110px'})
    ]
    if not table_names:
        layout_children.append(html.P("No se encontraron tablas o hubo error."))
        return html.Div(layout_children)

    print(f"Generando layout para tablas: {table_names}")
    for table_name in table_names:
        table_columns = get_table_columns(table_name)
        if not table_columns:
            layout_children.append(html.H3(f"Tabla: {table_name} (Error columnas)", style={'color': 'red'}))
            layout_children.append(html.Hr())
            continue

        dt_columns = [{'name': col, 'id': col} for col in table_columns]
        table_id = f"dynamic-table-{table_name}"
        count_id = f"{table_id}-row-count"

        layout_children.extend([
            html.H3(f"{table_name}", style={'text-align': 'center', 'fontSize': '20px'}),
            dash_table.DataTable(
                id=table_id,
                columns=dt_columns,
                page_current=0, page_size=PAGE_SIZE, page_action='custom',
                filter_action='custom', filter_query='',
                style_table={'overflowX': 'auto', 'width': '95%', 'fontFamily': "'Roboto', sans-serif", 'margin': '10px auto'},
                style_header={'backgroundColor': 'rgb(0, 39, 82)', 'fontWeight': 'bold', 'fontFamily': "'Roboto', sans-serif", 'color': 'white'},
                style_cell={'minWidth': '100px', 'width': '150px', 'maxWidth': '250px',
                            'overflow': 'hidden', 'textOverflow': 'ellipsis', 'textAlign': 'left',
                            'whiteSpace': 'normal', 'height': 'auto', 'padding': '5px', 'fontFamily': "'Roboto', sans-serif"},
                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
            ),
            html.Div(id=count_id, style={'marginTop': '10px', 'fontStyle': 'italic'}),
            html.Hr()
        ])
    return html.Div(layout_children)

layout = create_dynamic_layout

# Generación Dinámica de Callbacks
def generate_table_callback(table_id, table_name, columns_list):
    print(f"Definiendo callback para tabla: {table_name} (ID: {table_id})")

    @dash.callback(
        Output(table_id, 'data'),
        Output(f'{table_id}-row-count', 'children'),
        Input(table_id, "page_current"),
        Input(table_id, "page_size"),
        Input(table_id, "sort_by"),
        Input(table_id, "filter_query")
    )
    def update_dynamic_table(page_current, page_size, sort_by, filter_query):
        print(f"Callback disparado para tabla '{table_name}': page={page_current}, size={page_size}, sort={sort_by}, filter='{filter_query}'")
        offset = page_current * page_size

        # Ordenación
        order_by_clause = f"ORDER BY `{columns_list[0]}` ASC"
        if sort_by:
            orders = [f"`{col['column_id']}` {col['direction'].upper()}"
                      for col in sort_by if col['column_id'] in columns_list]
            if orders: order_by_clause = "ORDER BY " + ", ".join(orders)

        # Filtrado
        where_clause, sql_params_dict = parse_filter_query_named_params(filter_query, columns_list)

        # Query para Datos
        safe_columns_str = ", ".join([f"`{c}`" for c in columns_list])
        query = f"""
            SELECT {safe_columns_str}
            FROM `{table_name}`
            WHERE {where_clause}
            {order_by_clause}
            LIMIT :limit OFFSET :offset;
        """
        # Crear diccionario de parámetros combinando filtro y paginación
        params_dict_data = sql_params_dict.copy()
        params_dict_data['limit'] = page_size
        params_dict_data['offset'] = offset

        # Llamar a fetch_data con la query y el diccionario de parámetros
        df_page = fetch_data(query, params=params_dict_data)

        # Query para Conteo
        count_query = f"SELECT COUNT(*) as total FROM `{table_name}` WHERE {where_clause};"
        # Llamar a fetch_data con la query de conteo y SÓLO los params del filtro
        df_count = fetch_data(count_query, params=sql_params_dict) # Pasar params del filtro

        total_rows = 0
        if not df_count.empty:
            try: total_rows = int(df_count['total'].iloc[0])
            except: print(f"Error al obtener conteo para {table_name}")
        else: print(f"Consulta de conteo vacía para {table_name}")

        row_count_text = f"Mostrando filas {offset + 1} a {min(offset + page_size, total_rows)} de {total_rows}"
        return df_page.to_dict('records') if not df_page.empty else [], row_count_text

# Registrar Callbacks
all_table_names_for_callbacks = get_table_names()
if all_table_names_for_callbacks:
    print("-" * 30)
    print("Registrando callbacks dinámicos (estilo SQLAlchemy):")
    for t_name in all_table_names_for_callbacks:
        t_cols = get_table_columns(t_name)
        if t_cols:
            t_id = f"dynamic-table-{t_name}"
            generate_table_callback(t_id, t_name, t_cols)
            print(f" - Callback registrado para: {t_name}")
        else:
            print(f" ! Omitiendo callback para tabla '{t_name}' (sin columnas).")
    print("-" * 30)
else:
    print("Advertencia: No se encontraron tablas para registrar callbacks.")