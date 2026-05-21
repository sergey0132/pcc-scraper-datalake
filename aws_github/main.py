import time
import pandas as pd
from extraccion import extraer_datos_pccom_api, extraer_datos_coolmod_produccion
from subir_s3 import subir_a_s3
import os


if __name__ == "__main__":
    print("🚀 Iniciando Pipeline ETL de Coolmod en Entorno Producción...")
    
    # 1. Extracción
    datos = extraer_datos_coolmod_produccion()
    
    # 2. Validación temprana
    if not datos:
        print("\n❌ Error Crítico: No se han extraído datos. El proceso se detiene aquí.")
        exit(1) # Finaliza el script con código de error para que GitHub Actions lo detecte
        
    # 3. Transformación y Limpieza
    try:
        df = pd.DataFrame(datos)
        
        # Eliminar filas donde el 'Nombre' sea nulo (esto limpia los "productos fantasma")
        df = df.dropna(subset=['Nombre'])
        
        # Asegurar que la columna Tienda exista (por si acaso)
        if 'Tienda' not in df.columns:
            df['Tienda'] = 'Coolmod'
            
        print(f"\n📊 TOTAL DE PRODUCTOS LIMPIOS: {len(df)}")
        
        # 4. Carga
        nombre_archivo = "chollos_coolmod_produccion.csv"
        df.to_csv(nombre_archivo, index=False, encoding='utf-8')
        
        print(f"\n💾 ¡Datos generados correctamente! Archivo '{nombre_archivo}' listo.")
        
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento o guardado: {e}")
        exit(1)
