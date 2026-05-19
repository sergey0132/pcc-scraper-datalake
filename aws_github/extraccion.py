import os
import time
from curl_cffi import requests
import pandas as pd
import random
import boto3 # Necesario para conectarse a S3


def extraer_datos_pccom_api():
    bag_products = []
    
    # --- 1. EL ALMACÉN CLASIFICADO DE DISFRACES ---
    safaris = ["safari15_5", "safari17_0", "safari18_0"]
    chromes = ["chrome124", "chrome120", "chrome119", "chrome117", "chrome114", "chrome110"]
    edges = ["edge120", "edge114", "edge101", "edge99"]
    
    # Cabeceras fijas fuera de los bucles (sin User-Agent)
    cabeceras_tienda = {
        "x-selected-language": "es",
        "x-channel": "e24bd484-e84d-4051-8c51-551bf17a0610",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.pccomponentes.com/aniversario",
        "Origin": "https://www.pccomponentes.com",
    }
    
    for page in range(1, 101):
        print(f"\n--- 📄 EXTRAYENDO PÁGINA {page} VIA API ---")
        exito = False
        intentos = 0
        
        # --- 2. SELECCIÓN FORZADA DE DIVERSIDAD (Mínimo 2 de cada uno) ---
        # Elegimos muestras aleatorias sin repetir dentro del mismo grupo
        safaris_elegidos = random.sample(safaris, 2)
        chromes_elegidos = random.sample(chromes, 2)
        edges_elegidos = random.sample(edges, 2)
        
        # Juntamos los 6 disfraces elegidos (2 + 2 + 2 = 6)
        identidades_pagina = safaris_elegidos + chromes_elegidos + edges_elegidos
        
        # Los mezclamos entre sí para que el orden de ejecución varíe en cada página
        random.shuffle(identidades_pagina)
        
        # Permitimos hasta 6 intentos para poder exprimir los 6 disfraces si hace falta
        while not exito and intentos < 6: 
            url_api_change = f'https://www.pccomponentes.com/api/dynamic-view?url=https%3A%2F%2Fwww.pccomponentes.com%2Fofertas-especiales%3Fsort%3Ddiscount%26page%3D{page}' 
            
            try:
                identidad_actual = identidades_pagina[intentos]
                print(f"🕵️ Intentando conexión (Identidad: {identidad_actual})...")
                
                repuesta = requests.get(
                    url_api_change,
                    impersonate=identidad_actual, 
                    headers=cabeceras_tienda,
                    timeout=15 
                )

                if repuesta.status_code == 200:
                    date = repuesta.json()
                    lista_articles = date.get('dynamicData', {}).get('articles', [])
                    
                    for producto in lista_articles:
                        producto['Fecha_Extraccion'] = time.strftime("%Y-%m-%d %H:%M:%S")
                        bag_products.append(producto)
                    
                    print(f"✅ ¡Éxito! Extraídos {len(lista_articles)} productos de la página {page}.")
                    exito = True
                else:
                    print(f"⚠️ Código {repuesta.status_code}. Reintentando...")
                    intentos += 1
                    tiempo_reintento = random.uniform(4.0, 8.0)
                    time.sleep(tiempo_reintento)
            
            except Exception as e:
                print(f"❌ Error en la conexión: {e}")
                intentos += 1
                time.sleep(6)

        # 3. PAUSA ALEATORIA ENTRE PÁGINAS
        if page < 100:
            tiempo_espera = random.randint(8, 15)
            print(f"⏳ Descansando {tiempo_espera} segundos para enfriar la IP...")
            time.sleep(tiempo_espera)

    return bag_products

# --- FLUJO PRINCIPAL ---
if __name__ == "__main__":
    print("🚀 Iniciando extracción ninja (API)...")
    lista_productos = extraer_datos_pccom_api()
    
    if lista_productos:
        df = pd.DataFrame(lista_productos)
        filename = f"pcc_offers_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"💾 Guardado localmente como {filename}")
        
        # Leemos el nombre del bucket de los secretos de GitHub
        S3_BUCKET_NAME = os.environ.get("MY_S3_BUCKET")
        
        if S3_BUCKET_NAME:
            subir_a_s3(filename, S3_BUCKET_NAME, "bronze")
        else:
            print("❌ Error: No se encontró la variable MY_S3_BUCKET.")
            
        print(f"🏁 Scraping exitoso. {len(df)} productos recolectados en total.")
    else:
        print("⚠️ No se obtuvieron datos finales.")
