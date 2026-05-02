import os
import time
from curl_cffi import requests
import pandas as pd
import random
import boto3 # Necesario para conectarse a S3


def extraer_datos_pccom_api():
    bag_products = []
    
    # 1. EL GRAN ARMARIO DE DISFRACES (Chrome, Edge y Safari)
    identidades = [
        "chrome120", "chrome119", "chrome116", 
        "edge101", "edge99", 
        "safari17_0", "safari15_5"
    ]

    for page in range(1, 6):
        print(f"\n--- 📄 EXTRAYENDO PÁGINA {page} VIA API ---")
        exito = False
        intentos = 0
        
        # 2. MEZCLAMOS LAS IDENTIDADES PARA CADA PÁGINA
        random.shuffle(identidades) 

        while not exito and intentos < 4: 
            url_api_change = f'https://www.pccomponentes.com/api/dynamic-view?url=https%3A%2F%2Fwww.pccomponentes.com%2Fofertas-especiales%3Fsort%3Ddiscount%26page%3D{page}'
            
            cabeceras_tienda = {
                "x-selected-language": "es",
                "x-channel": "e24bd484-e84d-4051-8c51-551bf17a0610",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.pccomponentes.com/ofertas-especiales",
                "Origin": "https://www.pccomponentes.com",
            }

            try:
                identidad_actual = identidades[intentos % len(identidades)]
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
                        # 1. Le inyectamos la fecha actual al diccionario original 
                        # (Esto es vital para saber cuándo sacamos la foto a los datos)
                        producto['Fecha_Extraccion'] = time.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # 2. Añadimos el producto COMPLETO a nuestra bolsa
                        bag_products.append(producto)
                    
                    print(f"✅ ¡Éxito! Extraídos {len(lista_articles)} productos de la página {page}.")
                    exito = True
                else:
                    print(f"⚠️ Código {repuesta.status_code}. Reintentando...")
                    intentos += 1
                    time.sleep(6) # Pausa corta entre reintentos fallidos
            
            except Exception as e:
                print(f"❌ Error en la conexión: {e}")
                intentos += 1
                time.sleep(6)

        # 3. PAUSA ALEATORIA ENTRE PÁGINAS (Para engañar a Cloudflare)
        # Solo hacemos la pausa si no es la última página
        if page < 5:
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
