import os
import boto3

# --- CONFIGURACIÓN DE AWS ---
# Estos valores los configuraremos en los Secrets de GitHub
S3_BUCKET_NAME = os.getenv('MY_S3_BUCKET')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = "us-east-1" # O la región donde esté tu bucket


def subir_a_s3(file_name, bucket, object_name=None):

    """Sube el archivo CSV a la capa Bronze de S3"""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
    try:
        s3_client.upload_file(file_name, bucket, object_name or file_name)
        print(f"✅ Archivo subido con éxito a s3://{bucket}/{object_name}")
    except Exception as e:
        print(f"❌ Error al subir a S3: {e}")