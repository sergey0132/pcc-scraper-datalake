import time
import pandas as pd
from extraccion import extraer_datos_pccom_api, extraer_datos_coolmod_produccion
from subir_s3 import subir_a_s3
import os


import pandas as pd

if __name__ == "__main__":
    print("🚀 Iniciando Pipeline ETL de PcComponentes en Entorno Producción...")
    
    # 1. Extracción
    # Llama a la función principal de tu scraper de PcComponentes
    datos = extraer_datos_pccomponentes()
    
    # 2. Validación temprana
    if not datos:
        print("\n❌ Error Crítico: No se han extraído datos de PcComponentes. El proceso se detiene aquí.")
        exit(1) # Finaliza el script con código de error para que GitHub Actions lo detecte
        
    # 3. Transformación y Limpieza
    try:
        df = pd.DataFrame(datos)
        
        # Eliminar filas donde el nombre sea nulo (limpia "productos fantasma")
        # ⚠️ IMPORTANTE: Si el JSON de PcComponentes llama al nombre 'name' o 'articulo', 
        # cambia 'Nombre' por la palabra exacta que use su API.
        if 'Nombre' in df.columns:
            df = df.dropna(subset=['Nombre'])
        
        # Asegurar que la columna Tienda exista para diferenciar los datos
        if 'Tienda' not in df.columns:
            df['Tienda'] = 'PcComponentes'
            
        print(f"\n📊 TOTAL DE PRODUCTOS LIMPIOS: {len(df)}")
        
        # 4. Carga
        nombre_archivo = "chollos_pccomponentes_produccion.csv"
        df.to_csv(nombre_archivo, index=False, encoding='utf-8')
        
        print(f"\n💾 ¡Datos generados correctamente! Archivo '{nombre_archivo}' listo para GitHub Actions.")
        
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento o guardado del DataFrame: {e}")
        exit(1)
