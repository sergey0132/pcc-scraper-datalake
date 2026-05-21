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

import time # Librería nativa para controlar los tiempos de espera y pausas
import random # Librería nativa para generar números aleatorios (vital para las pausas y rotar disfraces)
import pandas as pd # Librería estrella de Data Engineering para manejar datos en formato tabla (DataFrames)
import re # Librería de Expresiones Regulares, sirve para buscar patrones de texto (como los códigos PROD-)
from curl_cffi import requests # Librería avanzada que suplanta las huellas digitales (JA3/TLS) del navegador

def extraer_datos_coolmod_produccion():
    # Inicializamos una lista vacía que actuará como nuestra "bolsa" temporal de datos
    bag_products = []
    
    # --- 1. EL ARMARIO DE ORO (Configuración de Identidades) ---
    # Lista de versiones de Safari estables para el entorno Linux de GitHub Actions
    safaris = ["safari15_5", "safari17_0", "safari18_0"]
    # Lista de versiones de Chrome que sabemos que no dan el error 'not supported'
    chromes = ["chrome120", "chrome119", "chrome116"]
    # Lista de versiones de Edge compatibles
    edges = ["edge101", "edge99"]
    
    # Cabeceras HTTP estándar para simular la petición de un navegador web normal (HTML)
    cabeceras_html = {
        # Le decimos al servidor qué formatos de archivo aceptamos (HTML, imágenes, etc.)
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        # Indicamos que nuestro idioma preferido es español
        "Accept-Language": "es-ES,es;q=0.9",
        # Fingimos que venimos navegando desde la página principal de la tienda
        "Referer": "https://www.coolmod.com/",
    }
    
    # --- BUCLE PRINCIPAL DE PAGINACIÓN ---
    # Ejecutamos el bucle desde la página 1 hasta la 20 (el range termina en el límite menos 1)
    for page in range(1, 21):
        # Imprimimos en consola en qué página estamos para monitorizar el progreso
        print(f"\n--- 🧊 EXTRAYENDO COOLMOD - PÁGINA {page}/20 ---")
        # Variable de control: asume que no hemos tenido éxito al empezar la página
        exito = False
        # Contador de intentos fallidos para esta página concreta
        intentos = 0
        
        # --- SELECCIÓN ALEATORIA DE DISFRACES ---
        # Escogemos 2 versiones de Safari al azar de nuestra lista
        safaris_elegidos = random.sample(safaris, 2)
        # Escogemos 2 versiones de Chrome al azar
        chromes_elegidos = random.sample(chromes, 2)
        # Escogemos 2 versiones de Edge al azar
        edges_elegidos = random.sample(edges, 2)
        
        # Juntamos los 6 disfraces seleccionados en una sola lista (2 + 2 + 2)
        identidades_pagina = safaris_elegidos + chromes_elegidos + edges_elegidos
        # Barajamos la lista de disfraces para que el orden de uso sea totalmente impredecible
        random.shuffle(identidades_pagina)
        
        # --- BUCLE DE RESILIENCIA (Anti-Bloqueos) ---
        # Mientras no hayamos tenido éxito y no hayamos gastado los 6 intentos permitidos...
        while not exito and intentos < 6: 
            # Construimos la URL pública de la página de ofertas con el número de página actual
            url_publica = f'https://www.coolmod.com/descuentos/?ordenacion=descuento&pagina={page}'
            
            try:
                # Seleccionamos el disfraz correspondiente al número de intento actual
                identidad_actual = identidades_pagina[intentos]
                # Avisamos por consola de qué identidad estamos usando
                print(f"🕵️ Intentando conexión (Identidad: {identidad_actual})...")
                
                # Hacemos la petición GET a la web pública disfrazando la huella TLS
                repuesta_html = requests.get(url_publica, impersonate=identidad_actual, headers=cabeceras_html, timeout=15)

                # Si el servidor responde con un código 200 (Todo OK, página encontrada)
                if repuesta_html.status_code == 200:
                    # Extraemos el código fuente de la página web como texto bruto
                    html_recibido = repuesta_html.text
                    
                    # --- PASO 2: ROBO DE CÓDIGOS (El truco del Regex) ---
                    # Usamos Regex para buscar 'PROD-' seguido de uno o más números (\d+) en todo el HTML
                    codigos_encontrados = re.findall(r'PROD-\d+', html_recibido)
                    # Convertimos la lista a un 'set' para borrar duplicados, y luego de vuelta a 'list'
                    codigos_unicos = list(set(codigos_encontrados))
                    
                    # Si la lista de códigos está vacía (no encontró nada en el HTML)
                    if not codigos_unicos:
                        # Avisamos por consola del problema
                        print("⚠️ Entramos a la web, pero no encontramos códigos PROD- en el HTML.")
                        # Sumamos 1 al contador de intentos fallidos
                        intentos += 1
                        # Pausa obligatoria antes de quemar el siguiente intento
                        time.sleep(3)
                        # Saltamos el resto del código del 'while' y volvemos a empezar el bucle
                        continue
                        
                    # Imprimimos cuántos códigos únicos logramos extraer con éxito
                    print(f"✅ ¡Extraídos {len(codigos_unicos)} códigos! Consultando API oculta...")
                    
                    # --- PASO 3: ATAQUE AL JSON SECRETO ---
                    # Formateamos los códigos uniéndolos con comas y metiéndolos entre %22 (formato URL)
                    codigos_formateados = ",".join([f"%22{c}%22" for c in codigos_unicos])
                    # Construimos la URL de la API secreta insertando los códigos formateados
                    url_json = f"https://www.coolmod.com/view_v2/ajax/category/newAjaxPricesForProductsWithCode.php?productCodes=[{codigos_formateados}]&DayId=PM&ZoneCode=PENINSULA&VatId=NV&TarId=1"
                    
                    # Creamos las cabeceras específicas para fingir que somos una petición AJAX legítima de la web
                    cabeceras_ajax = {
                        # Aceptamos recibir un JSON de vuelta
                        "Accept": "application/json, text/javascript, */*; q=0.01",
                        # ESTA ES LA CLAVE: Le dice al servidor que es una petición interna generada por su web
                        "X-Requested-With": "XMLHttpRequest",
                        # Le decimos que la petición viene desde la URL pública que visitamos antes
                        "Referer": url_publica
                    }
                    
                    # Hacemos la segunda petición (a la API JSON oculta) usando el MISMO disfraz que antes
                    repuesta_json = requests.get(url_json, impersonate=identidad_actual, headers=cabeceras_ajax, timeout=15)
                    
                    # --- PASO 4: PARSEO DE DATOS BLINDADO ---
                    # Convertimos la respuesta cruda directamente a un objeto JSON (lista de diccionarios)
                    datos_crudos = repuesta_json.json()
                    
                    # Filtro de seguridad: Si lo que nos devuelve no es una lista (ej. devuelve la palabra "false")
                    if not isinstance(datos_crudos, list):
                        # Avisamos de que nos han bloqueado en el segundo paso
                        print(f"⚠️ El servidor bloqueó la petición AJAX. Reintentando...")
                        # Sumamos un intento fallido
                        intentos += 1
                        # Pausamos por seguridad
                        time.sleep(3)
                        # Volvemos a empezar el intento completo
                        continue
                        
                    # Si pasamos el filtro, iteramos sobre cada diccionario de producto en el JSON recibido
                    for prod in datos_crudos:
                        try:
                            # Extraemos el 'Slug', forzándolo a texto plano por si viniera como nulo (None)
                            slug = str(prod.get('Slug', ''))
                            # Limpiamos el slug: quitamos barras, guiones, y ponemos la primera letra en mayúscula
                            nombre_limpio = slug.replace('/', '').replace('-', ' ').title().strip()
                            
                            # Si después de limpiar el nombre nos quedamos sin nada (cadena vacía), ignoramos el producto
                            if not nombre_limpio:
                                continue
                                
                            # Extraemos el precio actual, lo forzamos a texto y cambiamos la coma por punto (para decimales)
                            precio_str = str(prod.get('Price', '0')).replace(',', '.')
                            # Lo convertimos a número decimal (Float) si existe el dato, si no, le asignamos 0.0
                            precio_actual = float(precio_str) if precio_str else 0.0
                            
                            # Hacemos exactamente el mismo proceso de limpieza con el precio antiguo
                            precio_orig_str = str(prod.get('OldPrice', '0')).replace(',', '.')
                            precio_original = float(precio_orig_str) if precio_orig_str else 0.0
                            
                            # Extraemos el porcentaje de descuento tal cual viene del JSON
                            desc_crudo = prod.get('PercentageDiscount', 0)
                            # Lo convertimos a número entero (Int) de forma segura
                            descuento_num = int(desc_crudo) if desc_crudo else 0
                            
                            # Construimos el enlace final funcional sumando el dominio base y el slug limpio
                            url_completa = f"https://www.coolmod.com{slug}"
                            
                            # Creamos el diccionario estandarizado (Capa Silver) listo para fusionarse con PcComponentes
                            producto_mapeado = {
                                "Nombre": nombre_limpio,            # Nombre en formato título limpio
                                "Precio_Actual": precio_actual,     # Número decimal limpio para hacer cálculos
                                "Precio_Original": precio_original, # Número decimal limpio
                                "Descuento": descuento_num,         # Número entero para poder ordenar de mayor a menor
                                "Valoracion": 5,                    # Número por defecto para rellenar huecos
                                "URL_Completa": url_completa,       # Enlace definitivo del producto
                                "Tienda": "Coolmod",                # Etiqueta que tu bot SQL utilizará para filtrar
                                "Fecha_Extraccion": time.strftime("%Y-%m-%d %H:%M:%S") # Momento exacto de la descarga
                            }
                            # Metemos este producto completamente limpio en nuestra bolsa general de chollos
                            bag_products.append(producto_mapeado)
                            
                        # Si algún campo de este producto provoca un fallo, capturamos el error
                        except Exception as err:
                            # Imprimimos el error, pero el bucle sigue iterando el siguiente producto sin crashear
                            print(f"⚠️ Error procesando producto: {err}")
                            
                    # Al terminar de procesar todos los productos de la página, confirmamos éxito
                    print(f"🎉 ¡Triunfo total! Chollos unificados de la página {page}.")
                    # Cambiamos la bandera a True para romper el 'while' de intentos y pasar a la página siguiente
                    exito = True
            
            # Capturamos errores globales (como un corte de internet o timeout en el server)
            except Exception as e:
                # Mostramos en consola por qué ha fallado la conexión
                print(f"❌ Error en la red o parseo: {e}")
                # Gastamos un intento
                intentos += 1
                # Esperamos un poco más para que la conexión de red se estabilice
                time.sleep(5)

        # --- SISTEMA DE ENFRIAMIENTO (Anti-Ban IP) ---
        # Entramos en este bloque siempre que no estemos en la última página
        if page < 20:
            # Calculamos un tiempo de espera aleatorio entre 3 y 7 segundos (Ideal para no gastar minutos de GitHub)
            tiempo_espera = random.randint(3, 7)
            # Imprimimos el mensaje de pausa
            print(f"⏳ Enfriando IP durante {tiempo_espera} segundos...")
            # Congelamos la ejecución del script temporalmente para simular comportamiento humano
            time.sleep(tiempo_espera)

    # Terminadas las 20 páginas, devolvemos la bolsa con todos los chollos de todas las iteraciones
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


