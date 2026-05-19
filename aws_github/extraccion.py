import os
import time
from curl_cffi import requests
import pandas as pd
import random
import boto3 # Necesario para conectarse a S3


def extraer_datos_pccom_api():
    bag_products = []
    
# 1. EL GRAN ARMARIO DE DISFRACES AMPLIADO Y COMPATIBLE (100% Operativo)
    identidades = [
        # --- El escudo VIP (Safari de escritorio) ---
        "safari15_5", 
        "safari17_0", 
        "safari18_0",
        
        # --- La flota de Chrome (Versiones estables y compatibles) ---
        "chrome124",
        "chrome120", 
        "chrome119", 
        "chrome117",
        "chrome114",
        "chrome110",
        
        # --- El escuadrón Edge (Versiones estables y compatibles) ---
        "edge120",
        "edge114",
        "edge101", 
        "edge99"
    ]
    
    # ⚡ OPTIMIZACIÓN: Sacamos las cabeceras fijas fuera de todos los bucles
    # Eliminamos la línea del User-Agent para que curl_cffi lo ponga dinámicamente
    cabeceras_tienda = {
        "x-selected-language": "es",
        "x-channel": "e24bd484-e84d-4051-8c51-551bf17a0610",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.pccomponentes.com/aniversario",
        "Origin": "https://www.pccomponentes.com",
    }
    
    # Añado mas paginas para tener mas productos de cada categoria 
    for page in range(1, 101):
        print(f"\n--- 📄 EXTRAYENDO PÁGINA {page} VIA API ---")
        exito = False
        intentos = 0
        
        # 2. MEZCLAMOS LAS IDENTIDADES PARA CADA PÁGINA
        random.shuffle(identidades) 

        while not exito and intentos < 7: 
            url_api_change = f'https://www.pccomponentes.com/api/dynamic-view?url=https%3A%2F%2Fwww.pccomponentes.com%2Fofertas-especiales%3Fsort%3Ddiscount%26page%3D{page}' 
            
            try:
                identidad_actual = identidades[intentos % len(identidades)]
                print(f"🕵️ Intentando conexión (Identidad: {identidad_actual})...")
                
                repuesta = requests.get(
                    url_api_change,
                    impersonate=identidad_actual, 
                    headers=cabeceras_tienda, # Usa el diccionario fijo de arriba
                    timeout=15 
                )

                if repuesta.status_code == 200:
                    date = repuesta.json()
                    lista_articles = date.get('dynamicData', {}).get('articles', [])
                    
                    for producto in lista_articles:
                        # 1. Le inyectamos la fecha actual al diccionario original 
                        producto['Fecha_Extraccion'] = time.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # 2. Añadimos el producto COMPLETO a nuestra bolsa
                        bag_products.append(producto)
                    
                    print(f"✅ ¡Éxito! Extraídos {len(lista_articles)} productos de la página {page}.")
                    exito = True
                else:
                    print(f"⚠️ Código {repuesta.status_code}. Reintentando...")
                    intentos += 1
                    # Pausa aleatoria humana entre reintentos fallidos para despistar
                    tiempo_reintento = random.uniform(4.0, 8.0)
                    time.sleep(tiempo_reintento)
            
            except Exception as e:
                print(f"❌ Error en la conexión: {e}")
                intentos += 1
                time.sleep(6)

        # 3. PAUSA ALEATORIA ENTRE PÁGINAS (Corregida para las 100 páginas)
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
