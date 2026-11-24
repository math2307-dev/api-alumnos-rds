import boto3
import pymysql
import os
import json

def lambda_handler(event, context):
    # 1. Obtener el entorno (dev, test, prod)
    stage = os.environ.get('STAGE', 'dev')
    
    # 2. Conectar a Secrets Manager
    secret_name = f"/alumnos/{stage}/credenciales"
    region_name = "us-east-1"
    
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        
        # Extraer datos
        host = secret['host']
        user = secret['username']
        password = secret['password']
        database = secret['dbname']
        
    except Exception as e:
        return {
            "statusCode": 500,
            "error": f"Error obteniendo el secreto: {str(e)}"
        }

    # 3. Conectar a MySQL y consultar
    connection = None
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=database,
            connect_timeout=5
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM alumnos;")
            results = cursor.fetchall()

        return {
            "statusCode": 200,
            "body": results
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }

    finally:
        if connection:
            connection.close()