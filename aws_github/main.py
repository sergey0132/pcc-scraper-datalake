import time
import pandas as pd
from extraccion import extraer_datos_pccom_api, extraer_datos_coolmod_produccion
from subir_s3 import subir_a_s3
import os


if __name__ == "__main__":
    # Mensaje de inicio para los logs de GitHub Actions
    print("🚀 Iniciando el proceso completo Multi-Tienda...")
    
    # --- 1. FASE DE EXTRACCIÓN (Ingesta) ---
    # Llamamos a la función de PcComponentes y guardamos su lista de diccionarios
    lista_products_pccomponentes = extraer_datos_pccom_api()
    print(f"DEBUG: PcComponentes me ha dado {len(lista_products_pccomponentes)} productos.")
    
    # Llamamos a la función de Coolmod y guardamos su li
    lista_productos_coolmod = extraer_datos_coolmod_produccion()
    print(f"DEBUG: Coolmod me ha dado {len(lista_productos_coolmod)} productos.")
    
    # Fusionamos ambas listas con el operador +. Si una tienda falla y devuelve [], no rompe nada.
    bolsa_total = lista_products_pccomponentes + lista_productos_coolmod
    
    # Comprobamos si, al menos, una de las dos tiendas ha devuelto productos
    if bolsa_total:
        # --- 2. FASE DE TRANSFORMACIÓN (Capa Bronze/Silver) ---
        # Pasamos la super-lista unificada a Pandas para crear una única tabla (DataFrame)
        df = pd.DataFrame(bolsa_total)
        
        # --- 3. FASE DE ESCRITURA LOCAL (Almacenamiento Temporal) ---
        # Generamos un nombre dinámico para el archivo usando la fecha y hora exactas
        # Le cambiamos el nombre a 'chollos_unificados' para reflejar que hay 2 tiendas
        filename = f"chollos_unificados_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Guardamos la tabla en el disco duro virtual de GitHub Actions en formato CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"📦 Archivo local '{filename}' generado con {len(df)} productos totales.")
        
        # --- 4. FASE DE CARGA EN LA NUBE (Upload a AWS S3) ---
        # Leemos el nombre secreto de tu bucket desde las variables de entorno de GitHub
        bucket = os.getenv('MY_S3_BUCKET')
        
        # Comprobación de seguridad: Verificamos que el Secret se leyó correctamente
        if bucket:
            # Llamamos a tu función de subida pasando el archivo, el bucket y la carpeta "bronze"
            subir_a_s3(filename, bucket, "bronze")
            print(f"🏁 ¡Pipeline Completado! {len(df)} datos inyectados en S3 con éxito.")
        else:
            # Si el entorno no encuentra la variable, lo avisamos para no volvernos locos buscando el error
            print("❌ Error Crítico: No se encontró la variable de entorno 'MY_S3_BUCKET' en GitHub Secrets.")
            
    else:
        # Si ambas funciones fallaron y las listas están vacías, terminamos el script en paz
        print("⚠️ No se obtuvieron datos de ninguna de las dos tiendas en esta ejecución.")
