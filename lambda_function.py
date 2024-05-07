import os
import utilities
import psycopg2
import traceback

# Crear la conexión con la BD
location = os.environ.get('DB_CONNECTION_PARAMS', 'devpostgresql')

conn_params = utilities.get_parameters([location])

# Crear el logger
logger = utilities.get_logger(os.environ.get('LOG_LEVEL', 'DEBUG'))


def connectdb():
    try:
        with psycopg2.connect(host=conn_params['host'],
                              user=conn_params['username'],
                              password=conn_params['password']) as conn:
            return conn
    except Exception as error:
        print(f'Error connecting to database: {error}')
        return None


def lambda_handler(event, context):
    logger.debug(f"Input: {event}")
    conn = connectdb()
    try:
        with conn.cursor() as cur:
            # usar SPs por seguridad
            cur.execute(f'SELECT * FROM public.employee where id =\'{event["id"]}\'')
            results = cur.fetchall()
            cur.close()
            # conexion.close()   ## Por qué no la cierro?
    except (Exception, psycopg2.DatabaseError) as error:
        # Escribir la verdadera causa del error en CloudWatch
        logger.error(f'Error en public.get_pools_search: {error}')
        # Stack dump
        traceback.print_exc()
        #  Realizamos rollback en caso de que el query  falle, para poder seguir haciendo querys con la conexion
        conn.rollback()
        # Levantar una excepción más genérica para que frontend no conozca la causa precisa del error
        # para evitar que los hackers obtengan información
        raise RuntimeError('HTTP 500. Error de ejecución')
    return results