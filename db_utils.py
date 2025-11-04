import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT'))

MARIADB_URI = f"mariadb+mariadbconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    engine = create_engine(MARIADB_URI)
    print(f"SQLAlchemy engine creado para {DB_HOST}:{DB_PORT}/{DB_NAME}")
except ImportError:
    print("Error: El conector 'mariadb' no está instalado. Ejecuta: pip install mariadb")
    engine = None
except Exception as e:
    print(f"Error al crear el engine de SQLAlchemy: {e}")
    engine = None


def fetch_data(query: str, params: dict = None) -> pd.DataFrame:
    if engine is None:
        print("Error: El engine de SQLAlchemy no está inicializado.")
        return pd.DataFrame()

    # Si no se pasan parámetros, inicializa como diccionario vacío
    if params is None:
        params = {}

    try:
        # Usar text() indica al engine que se va introducir SQL literal
        sql_text = text(query)
        df = pd.read_sql(sql_text, engine, params=params)
        return df
    except SQLAlchemyError as e:
        print(f"Error de SQLAlchemy: {e}\nQuery: {query}\nParams: {params}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error inesperado en fetch_data: {e}\nQuery: {query}\nParams: {params}")
        return pd.DataFrame()


def get_table_names() -> list:
    if engine is None: return []
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES;"))
            return [row[0] for row in result]
    except Exception as e:
        print(f"Error en get_table_names: {e}")
        return []


def get_table_columns(table_name: str) -> list:
    if engine is None: return []
    if not table_name.replace('_', '').isalnum(): return []
    try:
        with engine.connect() as connection:
            query = text(f'SHOW COLUMNS FROM `{table_name}`;')
            result = connection.execute(query)
            columns = [row[0] for row in result]
            if not columns: # Fallback
                query_desc = text(f'DESCRIBE `{table_name}`;')
                result_desc = connection.execute(query_desc)
                columns = [row[0] for row in result_desc]
            return columns
    except Exception as e:
        print(f"Error en get_table_columns para '{table_name}': {e}")
        return []

# Funcion para buscar info desde las tablas filtrando por valores
def parse_filter_query_named_params(query_string, valid_columns):
    """
    Convierte el string de filtro de dash_table a una cláusula WHERE SQL
    con parámetros nombrados (:param_0, :param_1...) y un diccionario de parámetros.
    """
    where_parts = []
    sql_params_dict = {}
    param_index = 0
    if query_string:
        filtering_expressions = query_string.split(' && ')
        for filter_part in filtering_expressions:
            # Operador 'contains'
            if ' contains ' in filter_part or ' scontains ' in filter_part:
                operator = ' contains ' if ' contains ' in filter_part else ' scontains '
                col_name, value = filter_part.split(operator, 1)
                col_name = col_name.strip().strip('{}')
                value = value.strip().strip('"').strip("'")
                if col_name in valid_columns:
                    param_name = f"filter_param_{param_index}"
                    where_parts.append(f"`{col_name}` LIKE :{param_name}")  # LIKE sigue siendo apropiado
                    sql_params_dict[param_name] = f"%{value}%"
                    param_index += 1
                else:
                    print(f"Advertencia: Columna de filtro inválida '{col_name}'.")

            # Operador '='
            """
            elif ' = ' in filter_part or ' s= ' in filter_part:
                col_name, value = filter_part.split(' s= ', 1)
                col_name = col_name.strip().strip('{}')
                value = value.strip().strip('"').strip("'")
                if col_name in valid_columns:
                    param_name = f"filter_param_{param_index}"
                    # Intentar conversión numérica (muy básica)
                    try:
                        numeric_value = float(value)
                        sql_params_dict[param_name] = numeric_value
                    except ValueError:
                        sql_params_dict[param_name] = value # Tratar como string
                    where_parts.append(f"`{col_name}` = :{param_name}")
                    param_index += 1
                else: print(f"Advertencia: Columna de filtro inválida '{col_name}'.")
            """

            # Añadir más 'elif' para otros operadores (>, <, >=, <=, !=) si es necesario...
            """
            Esto significa que en el en la tabla en el campo de filter data puedes filtrar por 
            = 1780000, > 1780000, < 1780000, >= 1780000 <= 1780000 o != 1780000 y hará la filtración correcta 
            pero hay que definir esta parte, por el momento esta desactivada o no completada
            """

    # Construir cláusula WHERE
    where_clause = " AND ".join(where_parts) if where_parts else "1=1"
    return where_clause, sql_params_dict


if __name__ == '__main__':
    print("\nProbando funciones con SQLAlchemy (parámetros nombrados)...")
    if engine:
        tables = get_table_names()
        if tables:
            print(f"\nTablas encontradas: {tables}")
            if len(tables) > 0:
                first_table = tables[0]
                cols = get_table_columns(first_table)
                if cols and len(cols) >= 2:
                    print(f"\nColumnas de '{first_table}': {cols}")
                    # Query con parámetros nombrados
                    test_query = f"SELECT `{cols[0]}`, `{cols[1]}` FROM `{first_table}` LIMIT :limit_val;"
                    # Parámetros como diccionario
                    df_test = fetch_data(test_query, params={'limit_val': 3})
                    if not df_test.empty:
                        print(f"\nPrimeras 3 filas de '{first_table}':")
                        print(df_test)
                    else:
                        print(f"\nNo se pudieron obtener datos de '{first_table}'.")
                else:
                    print(f"\nNo se pudieron obtener suficientes columnas para '{first_table}'.")