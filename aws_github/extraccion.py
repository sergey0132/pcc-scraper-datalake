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
            url_api_change = f'https://www.pccomponentes.com/api/dynamic-view?url=https%3A%2F%2Fwww.pccomponentes.com%2Fpcdays%3Fsort%3Ddiscount%26page%3D{page}}' 
            
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


def extraer_datos_redcomputer_api():
    # Esta es nuestra "mochila". Aquí guardaremos todos los chollos que vayamos recolectando.
    bag_products = []
    
    # --- 1. EL ARMARIO DE DISFRACES ---
    # Tenemos listas con diferentes versiones de navegadores para engañar al sistema antibots.
    safaris = ["safari15_5", "safari17_0", "safari18_0"]
    chromes = ["chrome120", "chrome119", "chrome116"]
    edges = ["edge101", "edge99"]
    
    # Nuestras cabeceras básicas y limpias. 
    # Ya NO ponemos el User-Agent aquí porque de eso se encarga el parámetro 'impersonate' más abajo.
    cabeceras_redcomputer = {
        "Accept": "application/json, text/javascript, */*; q=0.01", # Queremos los datos crudos (JSON), no la web visual.
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8,ru;q=0.7",      # Hablamos español.
        "Referer": "https://www.redcomputer.es/bajamos-precios",    # Fingimos venir navegando desde esta sección.
        "X-Requested-With": "XMLHttpRequest",                       # Confirmamos que es una llamada interna de la web.
    }
    
    # --- 2. BUCLE PRINCIPAL (Recorriendo el catálogo) ---
    # Vamos a raspar desde la página 1 hasta la 16.
    for page in range(1, 17):
        print(f"\n--- 📄 EXTRAYENDO PÁGINA {page} VIA API ---")
        exito = False
        intentos = 0
        
        # Preparamos los disfraces para esta página en concreto.
        # Cogemos 2 aleatorios de cada navegador para tener variedad.
        safaris_elegidos = random.sample(safaris, 2)
        chromes_elegidos = random.sample(chromes, 2)
        edges_elegidos = random.sample(edges, 2)
        
        # Juntamos los 6 disfraces en una sola lista (2+2+2).
        identidades_pagina = safaris_elegidos + chromes_elegidos + edges_elegidos
        # Los mezclamos (barajamos) para que el orden sea totalmente impredecible para Cloudflare.
        random.shuffle(identidades_pagina)
        
        # --- 3. BUCLE DE REINTENTOS (A prueba de fallos) ---
        # Si fallamos (por baneo temporal o fallo de red), tenemos hasta 6 balas en la recámara.
        while not exito and intentos < 6: 
            # Inyectamos el número de la página actual en la URL limpia de la API.
            
            url_api_change = f'https://www.redcomputer.es/bajamos-precios?page={page}&from-xhr'
            
            try:
                # Nos ponemos el disfraz que toque en este intento (ej: 'safari17_0').
                identidad_actual = identidades_pagina[intentos]
                print(f"🕵️ Intentando conexión (Identidad: {identidad_actual})...")
                
                # Hacemos la llamada al servidor de Red Computer.
                repuesta = requests.get(
                    url_api_change,
                    impersonate=identidad_actual, # Magia antibots: simula la huella digital exacta del navegador.
                    headers=cabeceras_redcomputer,
                    timeout=15 # Si el servidor tarda más de 15 segundos en contestar, cortamos la llamada.
                )

                # Si el código de estado es 200 (OK), el servidor nos ha dejado pasar.
                if repuesta.status_code == 200:
                    date = repuesta.json()
                    
                    # --- EL CHIVATO ---
                    print("\n📦 LLAVES DEL JSON:")
                    print(date.keys())
                    # ------------------
                    
                    # Navegamos por el diccionario buscando la lista exacta de productos.
                    # Usamos .get() por si la llave no existe, así el código no explota (devuelve lista vacía []).
                    lista_articles = date.get('products', [])
                    
                    # Recorremos cada producto que nos ha devuelto esta página.
                    for producto in lista_articles:
                        # Le añadimos un sello con la fecha y hora exactas en las que lo capturamos.
                        producto['Fecha_Extraccion'] = time.strftime("%Y-%m-%d %H:%M:%S")
                        # Lo metemos en nuestra "mochila" principal.
                        bag_products.append(producto)
                    
                    print(f"✅ ¡Éxito! Extraídos {len(lista_articles)} productos de la página {page}.")
                    # Marcamos la página como exitosa para salir del bucle 'while' y pasar a la siguiente página.
                    exito = True
                else:
                    # Si devuelve 403 (baneo) o 500 (error del servidor), sumamos un intento y esperamos un poco.
                    print(f"⚠️ Código {repuesta.status_code}. Reintentando...")
                    intentos += 1
                    time.sleep(random.uniform(4.0, 8.0)) # Pausa aleatoria corta entre 4 y 8 segundos.
            
            except Exception as e:
                # Si se corta el internet o la librería da un error crítico, lo atrapamos aquí para que el script siga vivo.
                print(f"❌ Error en la conexión: {e}")
                intentos += 1
                time.sleep(6)

        # --- 4. ENFRIAMIENTO DE LA IP ---
        # Si hemos terminado con una página (y no es la última), hacemos una pausa larga.
        # Esto es vital para simular el comportamiento humano leyendo una web y evitar que baneen tu IP real.
        if page < 16:
            tiempo_espera = random.randint(8, 15)
            print(f"⏳ Descansando {tiempo_espera} segundos para enfriar la IP...")
            time.sleep(tiempo_espera)

    # Una vez acabadas las 16 páginas, devolvemos la mochila llena para volcarla en Pandas y limpiarla.
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


