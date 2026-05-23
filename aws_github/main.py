import time
import os
import pandas as pd
from extraccion import extraer_datos_pccom_api
from datetime import datetime
import boto3 

if __name__ == "__main__":
    print("🚀 Iniciando Pipeline ETL de PcComponentes en Entorno Producción...")
    
    # 1. Extracción
    datos = extraer_datos_pccom_api()
    
    # 2. Validación temprana
    if not datos:
        print("\n❌ Error Crítico: No se han extraído datos de PcComponentes.")
        exit(1)
        
    # 3. Transformación Básica
    try:
        df = pd.DataFrame(datos)
        
        if 'name' in df.columns:
            df = df.dropna(subset=['name'])
        
        if 'Tienda' not in df.columns:
            df['Tienda'] = 'PcComponentes'
            
        print(f"\n📊 TOTAL DE PRODUCTOS EXTRAÍDOS: {len(df)}")
        
        # 4. Guardado Local Temporal
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"pcc_offers_{fecha_str}.csv"
        df.to_csv(nombre_archivo, index=False, encoding='utf-8')
        
        # 5. Carga a AWS S3 DIRECTA (Sin el archivo subir_s3.py)
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        bucket_name = os.environ.get('MY_S3_BUCKET')
        
        if aws_access_key and aws_secret_key and bucket_name:
            print("☁️ Subiendo a Amazon S3 (Capa Bronze)...")
            s3_client = boto3.client(
                's3', 
                aws_access_key_id=aws_access_key, 
                aws_secret_access_key=aws_secret_key
            )
            
            ruta_s3 = f"bronze/{nombre_archivo}"
            s3_client.upload_file(nombre_archivo, bucket_name, ruta_s3)
            
            print(f"✅ ¡Éxito Total! Archivo subido a S3: {ruta_s3}")
        else:
            print("⚠️ Faltan credenciales AWS.")
            
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento o subida a S3: {e}")
        exit(1)
