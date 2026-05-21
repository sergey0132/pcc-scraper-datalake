import os
import time
from curl_cffi import requests
import pandas as pd
import random
import boto3 # Necesario para conectarse a S3


def extraer_datos_pccom_api():
    bag_products = []
    
    # --- 1. EL ARMARIO DE ORO (Configuración de Identidades) ---
    # Lista de versiones de Safari estables para el entorno Linux de GitHub Actions
    safaris = ["safari15_5", "safari17_0", "safari18_0"]
    # Lista de versiones de Chrome que sabemos que no dan el error 'not supported'
    chromes = ["chrome120", "chrome119", "chrome116"]
    # Lista de versiones de Edge compatibles
    edges = ["edge101", "edge99"]

    
    # Cabeceras fijas fuera de los bucles (sin User-Agent)
    cabeceras_tienda = {
        "x-selected-language": "es",
        "x-channel": "e24bd484-e84d-4051-8c51-551bf17a0610",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.pccomponentes.com/aniversario",
        "Origin": "https://www.pccomponentes.com",
    }
    
    for page in range(1, 26):
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
        if page < 25:
            tiempo_espera = random.randint(8, 15)
            print(f"⏳ Descansando {tiempo_espera} segundos para enfriar la IP...")
            time.sleep(tiempo_espera)

    return bag_products


def extraer_datos_coolmod_produccion():
    bag_products = []
    
    safaris = ["safari15_5", "safari17_0", "safari18_0"]
    chromes = ["chrome120", "chrome119", "chrome116"]
    edges = ["edge101", "edge99"]
    
    cabeceras_html = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.coolmod.com/",
    }
    
    for page in range(1, 21):
        print(f"\n--- 🧊 EXTRAYENDO COOLMOD - PÁGINA {page}/20 ---")
        exito = False
        intentos = 0
        
        safaris_elegidos = random.sample(safaris, 2)
        chromes_elegidos = random.sample(chromes, 2)
        edges_elegidos = random.sample(edges, 2)
        identidades_pagina = safaris_elegidos + chromes_elegidos + edges_elegidos
        random.shuffle(identidades_pagina)
        
        while not exito and intentos < 6:
            url_publica = f'https://www.coolmod.com/descuentos/?ordenacion=descuento&pagina={page}'
            
            try:
                identidad_actual = identidades_pagina[intentos]
                print(f"🕵️ Intentando conexión (Identidad: {identidad_actual})...")
                
                repuesta_html = requests.get(
                    url_publica,
                    impersonate=identidad_actual,
                    headers=cabeceras_html,
                    timeout=15
                )
 
                if repuesta_html.status_code != 200:
                    print(f"⚠️ Código {repuesta_html.status_code} en HTML. Reintentando...")
                    intentos += 1
                    time.sleep(random.uniform(4, 8))
                    continue  # ← Vuelve al while correctamente
 
                html_recibido = repuesta_html.text
                codigos_encontrados = re.findall(r'PROD-\d+', html_recibido)
                codigos_unicos = list(set(codigos_encontrados))
                
                # BUG 1 CORREGIDO: break en vez de continue
                if not codigos_unicos:
                    print("⚠️ No se encontraron productos en esta página. Saltando.")
                    exito = True
                    break  # ← Sale del while y avanza al siguiente for
                
                codigos_formateados = ",".join([f"%22{c}%22" for c in codigos_unicos])
                url_json = (
                    f"https://www.coolmod.com/view_v2/ajax/category/"
                    f"newAjaxPricesForProductsWithCode.php"
                    f"?productCodes=[{codigos_formateados}]"
                    f"&DayId=PM&ZoneCode=PENINSULA&VatId=NV&TarId=1"
                )
                
                cabeceras_ajax = {
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": url_publica
                }
                
                # BUG 2 CORREGIDO: try/except propio para la segunda petición
                try:
                    repuesta_json = requests.get(
                        url_json,
                        impersonate=identidad_actual,
                        headers=cabeceras_ajax,
                        timeout=15
                    )
                    repuesta_json.raise_for_status()  # Lanza excepción si no es 200
                    lista_productos = repuesta_json.json()
                except Exception as e:
                    print(f"❌ Error en petición JSON de precios: {e}")
                    intentos += 1
                    time.sleep(random.uniform(4, 8))
                    continue  # ← Reintenta con otra identidad
                
                if isinstance(lista_productos, list) and len(lista_productos) > 0:
                    for prod in lista_productos:
                        prod['Fecha_Extraccion'] = time.strftime("%Y-%m-%d %H:%M:%S")
                        prod['Tienda'] = 'Coolmod'
                        bag_products.append(prod)
                    
                    print(f"✅ ¡Éxito! Extraídos {len(lista_productos)} productos de la página {page}.")
                    exito = True
                    # BUG 3 CORREGIDO: break explícito para salir del while
                    break
                else:
                    print(f"⚠️ JSON vacío o bloqueado. Reintentando...")
                    intentos += 1
                    time.sleep(random.uniform(4, 8))
                    continue  # ← Reintenta con otra identidad
            
            except Exception as e:
                print(f"❌ Error general en la conexión: {e}")
                intentos += 1
                time.sleep(6)
 
        if not exito:
            print(f"❌ Página {page} falló después de {intentos} intentos. Continuando...")
 
        if page < 20:
            tiempo_espera = random.randint(8, 15)
            print(f"⏳ Descansando {tiempo_espera} segundos para enfriar la IP...")
            time.sleep(tiempo_espera)
 
    return bag_products
# ==========================================
# BLOQUE DE EJECUCIÓN DEL SCRIPT
# ==========================================
# Comprueba si este archivo se está ejecutando directamente como programa principal
if __name__ == "__main__":
    # Imprimimos aviso de inicio de programa
    print("🚀 Iniciando Pipeline ETL de Coolmod en Entorno Producción...")
    
    # Ejecutamos toda la función de arriba y guardamos el resultado devuelto en la variable 'datos'
    datos = extraer_datos_coolmod_produccion()
    
    # Comprobamos si la variable 'datos' contiene información (es decir, no está vacía)
    if datos:
        # Usamos la librería Pandas para convertir nuestra lista de diccionarios en un DataFrame (Tabla)
        df = pd.DataFrame(datos)
        
        # Mostramos un resumen con la cantidad total de filas extraídas
        print(f"\n📊 TOTAL DE PRODUCTOS EXTRAÍDOS: {len(df)}")
        
        # 🚨 CAMBIO VITAL: Guardamos en el mismo directorio (carpeta) donde se ejecuta el archivo. Vital para GitHub.
        nombre_archivo = "chollos_coolmod_produccion.csv"
        
        # Ordenamos a Pandas que genere un archivo CSV. index=False evita guardar la columna de números de fila. encoding asegura los acentos.
        df.to_csv(nombre_archivo, index=False, encoding='utf-8')
        
        # Confirmamos que el archivo se ha escrito en disco correctamente
        print(f"\n💾 ¡Datos generados! Archivo '{nombre_archivo}' listo para el siguiente paso del pipeline.")
        
    # Si la variable 'datos' llegó vacía (hubo un problema técnico insalvable o cero productos)
    else:
        # Avisamos de que el programa finalizó pero no generó base de datos
        print("\n❌ Error Crítico: No se han extraído datos.")


