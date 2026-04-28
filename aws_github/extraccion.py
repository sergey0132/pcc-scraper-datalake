import os
import time
from curl_cffi import requests
import pandas as pd
import boto3 # Necesario para conectarse a S3


# --- FUNCIÓN DE EXTRACCIÓN (API) ---
def extraer_datos_pccom_api():
    bag_products = []
    identidades = ["chrome110", "chrome116", "chrome120", "chrome101"]

    for page in range(1, 6):
        print(f"\n--- 📄 EXTRAYENDO PÁGINA {page} VIA API ---")
        exito = False
        intentos = 0

        while not exito and intentos < 3: 
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
                print(f"🕵️ Intentando conexión (Identidad: {identidades[intentos % len(identidades)]})...")
                repuesta = requests.get(
                    url_api_change,
                    impersonate=identidades[intentos % len(identidades)], 
                    headers=cabeceras_tienda,
                    timeout=15 
                )

                if repuesta.status_code == 200:
                    date = repuesta.json()
                    lista_articles = date.get('dynamicData', {}).get('articles', [])
                    
                    for producto in lista_articles:
                        bag_products.append({
                            "Nombre": producto.get('name', 'Sin nombre'),
                            "Precio_Actual": producto.get('price', 0),
                            "Precio_Original": producto.get('referencePrice', 0),
                            "Descuento": producto.get('discount', 0),
                            "Valoracion": producto.get('ratingAvg', 'N/A'),
                            "Opiniones": producto.get('ratingCount', '0'),
                            "URL": "https://www.pccomponentes.com" + producto.get('url', ''),
                            "Fecha": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                    
                    print(f"✅ ¡Éxito! Extraídos {len(lista_articles)} productos.")
                    exito = True
                else:
                    print(f"⚠️ Código {repuesta.status_code}. Reintentando...")
                    intentos += 1
                    time.sleep(5)
            except Exception as e:
                print(f"❌ Error en la conexión: {e}")
                intentos += 1
                time.sleep(5)

        time.sleep(3) 
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
