import time
import pandas as pd
from extraccion import extraer_datos_pccom
from subir_s3 import subir_a_s3
import os
from extraccion import url_objetivo

if __name__ == "__main__":
    print("🚀 Iniciando el proceso completo...")
    
    # 1. Extraer
    lista_productos = extraer_datos_pccom(url_objetivo)
    
    if lista_productos:
        # 2. Procesar a DataFrame
        df = pd.DataFrame(lista_productos)
        
        # 3. Guardar temporalmente
        filename = f"pcc_offers_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        
        # 4. Subir a S3
        # Cogemos las variables que configuramos en los Secrets de GitHub
        bucket = os.getenv('MY_S3_BUCKET')
        subir_a_s3(filename, bucket, "bronze")
        
        print(f"🏁 ¡Todo listo! Datos en S3.")
    else:
        print("⚠️ No se obtuvieron datos en esta ejecución.")
