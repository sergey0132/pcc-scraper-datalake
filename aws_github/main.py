import time
import os
import pandas as pd
from extraccion import extraer_datos_pccom_api
from subir_s3 import subir_a_s3
from datetime import datetime

if __name__ == "__main__":
    print("🚀 Iniciando Pipeline ETL de PcComponentes en Entorno Producción...")
    
    # 1. Extracción
    # Usamos el nombre exacto de la función que hemos importado
    datos = extraer_datos_pccom_api()
    
    # 2. Validación temprana
    if not datos:
        print("\n❌ Error Crítico: No se han extraído datos de PcComponentes. El proceso se detiene aquí.")
        exit(1)
        
    # 3. Transformación Básica (Capa Bronze)
    try:
        df = pd.DataFrame(datos)
        
        # PcComponentes devuelve el nombre del producto en la llave 'name'
        if 'name' in df.columns:
            df = df.dropna(subset=['name'])
        
        if 'Tienda' not in df.columns:
            df['Tienda'] = 'PcComponentes'
            
        print(f"\n📊 TOTAL DE PRODUCTOS EXTRAÍDOS: {len(df)}")
        
        # 4. Guardado Local Temporal
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"pcc_offers_{fecha_str}.csv"
        df.to_csv(nombre_archivo, index=False, encoding='utf-8')
        print(f"\n💾 Archivo local '{nombre_archivo}' generado temporalmente.")
        
        # 5. Carga a AWS S3 (Capa Bronze)
        # Aquí usamos tu función importada para enviarlo a la nube
        print("☁️ Subiendo a Amazon S3 (Capa Bronze)...")
        subir_a_s3(nombre_archivo, f"bronze/{nombre_archivo}")
        
        print("✅ ¡Pipeline completado con éxito!")
        
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento o subida a S3: {e}")
        exit(1)
