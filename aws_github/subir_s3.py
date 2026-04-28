import os
import boto3

# --- CONFIGURACIÓN DE AWS ---
# Estos valores los configuraremos en los Secrets de GitHub
S3_BUCKET_NAME = os.getenv('MY_S3_BUCKET')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = "us-east-1" # O la región donde esté tu bucket


# --- FUNCIÓN DE SUBIR A S3 ---
def subir_a_s3(archivo_local, bucket, carpeta):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    ruta_s3 = f"{carpeta}/{archivo_local}"
    try:
        s3.upload_file(archivo_local, bucket, ruta_s3)
        print(f"☁️ ¡Subido a S3 con éxito!: s3://{bucket}/{ruta_s3}")
    except Exception as e:
        print(f"❌ Error al subir a S3: {e}")
