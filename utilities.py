import boto3
import json
import os
import logging


# Obtener parametros desde el Parameter Store del Systems Manager
# Recibe una lista de nombres de parámetros, ejemplo:
# db_config = get_parameters(["/dev/postgresql/13/globals", "/dev/postgresql/13/kraks"])
# Estructura Propuesta para las configuraciones
# /dev/postgresql/13/globals = {
#    "query-timeout": 20,
#    "pool-size": 10
# }
# /dev/postgresql/13/kraks = {
#    "host": "aws-ewinnersports-dev.chwrzzubpg1x.us-east-1.rds.amazonaws.com",
#    "port": 5432,
#    "database": "ewinnersports_",
#    "username": "postgres_ewinner",
#    "password": "<See Keepass or Systems Manager>",
#    "query-timeout": 25,
#    "pool-size": 15
# }
def get_parameters(parameter_name_list):
    ssm = boto3.client('ssm', region_name=os.environ.get('AWS_REGION', 'us-east-2'))
    configuration_list = ssm.get_parameters(Names=parameter_name_list, WithDecryption=True)
    conn_props = dict()
    # Al diccionario global_config se le hace merge de último,
    # para habilitar el override de parámetros específicos
    # por encima de los globales
    global_config = dict()
    for config in configuration_list['Parameters']:
        param_json = json.loads(config['Value'])
        if config['Name'].find('globals') == -1:
            conn_props = {**param_json, **conn_props}
        else:
            global_config = param_json
    conn_props = {**global_config, **conn_props}
    return conn_props


def get_parameters2(parameter_name_list):
    ssm_client = boto3.client('ssm', region_name=os.environ.get('AWS_REGION', 'us-east-2'))
    encrypted_credentials = ssm_client.get_parameters(Names=parameter_name_list, WithDecryption=True)

    # Divide la cadena en una lista
    credentials = encrypted_credentials['Parameters']['Value']

    credentials_list = credentials.split(',')
    print(credentials_list)

    # # Si el usuario y la contraseña están encriptados, descifralos antes de usarlos
    # if ssm_client.get_parameter(Name='username')['Parameter']['Type'] == 'SecureString':
    #     db_username = boto3.client('kms').decrypt(CiphertextBlob=db_username)['Plaintext']
    #
    # if ssm_client.get_parameter(Name='password')['Parameter']['Type'] == 'SecureString':
    #     db_password = boto3.client('kms').decrypt(CiphertextBlob=db_password)['Plaintext']

    # Conecta a PostgreSQL usando las variables de entorno
    # connection_string = f"host={db_host} dbname={db_name} user={db_username} password={db_password}"
    # return connection_string
    # conn = psycopg2.connect(connection_string)


log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO':  logging.INFO,
    'WARN':  logging.WARN,
    'ERROR': logging.ERROR,
    'FATAL': logging.FATAL
}


def get_log_level(log_level_name: str) -> int:
    if log_level_name is None:
        return logging.INFO
    if log_level_name in log_levels:
        return log_levels[log_level_name]
    else:
        return logging.INFO


def get_logger(log_level_name):
    log_level = get_log_level(log_level_name)
    # Esta configuración de "basicConfig" no tiene efecto en AWS ??!!??
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger()
    logger.setLevel(log_level)
    return logger