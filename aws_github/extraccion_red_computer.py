from curl_cffi import requests
import time
import random
import pandas as pd
import ast
import boto3
import io
import os
from datetime import datetime

# ==========================================
# 1. FUNCIONES DE LIMPIEZA Y NORMALIZACIÓN
# ==========================================
def extraer_imagen(cover_text):
    try:
        diccionario = ast.literal_eval(str(cover_text))
        return diccionario.get('bySize', {}).get('large_default', {}).get('url', '')
    except:
        return ''

def estandarizar_categoria(texto_sucio):
    texto = str(texto_sucio).lower()
    
    # 1. Informática y Componentes Principales
    if 'gráfica' in texto or 'grafica' in texto: return 'Tarjetas Gráficas'
    if 'procesador' in texto or 'cpu' in texto: return 'Procesadores'
    if 'placa' in texto or 'base' in texto: return 'Placas' 
    if 'ram' in texto or 'memoria' in texto: return 'Memorias RAM'
    if 'fuente' in texto or 'alimentación' in texto or 'alimentacion' in texto: return 'Fuentes de Alimentación'
    if 'caja' in texto or 'torre' in texto: return 'Cajas para PC'
    
    # 2. Refrigeración y Almacenamiento
    if 'refrigeración' in texto or 'refrigeracion' in texto or 'ventilador' in texto or 'disipador' in texto or 'líquida' in texto: return 'Refrigeración'
    if 'disco' in texto or 'ssd' in texto or 'hdd' in texto or 'almacenamiento' in texto: return 'Almacenamiento'
    
    # 3. Ordenadores y Pantallas
    if 'portátil' in texto or 'portatil' in texto: return 'Portátiles'
    if 'monitor' in texto: return 'Monitores'
    if 'sobremesa' in texto or 'pc gaming' in texto or 'mini pc' in texto: return 'Ordenadores Sobremesa'
    
    # 4. Periféricos y Accesorios
    if 'teclado' in texto: return 'Teclados'
    if 'ratón' in texto or 'raton' in texto or 'ratones' in texto: return 'Ratones'
    if 'auricular' in texto: return 'Auriculares'
    
    # 5. Redes, Smartwatches y Sistemas
    if 'router' in texto or 'wifi' in texto or 'punto de acceso' in texto or 'red' in texto: return 'Redes y Routers'
    if 'smartwatch' in texto or 'reloj' in texto or 'pulsera' in texto: return 'Smartwatches'
    if 'sistema' in texto or 'windows' in texto or 'so' in texto: return 'Sistemas'
    
    # EL SALVAVIDAS DINÁMICO (Limpiando comas y barras)
    texto_limpio = str(texto_sucio).replace(',', '').replace('/', ' ')
    palabras = texto_limpio.split()
    if len(palabras) > 0:
        return palabras[0].capitalize()
    else:
        return "Otros"


# ==========================================
# 2. MOTOR DE EXTRACCIÓN (SCRAPER API)
# ==========================================
def extraer_datos_redcomputer_api():
    bag_products = []
    safaris = ["safari15_5", "safari17_0", "safari18_0"]
    chromes = ["chrome120", "chrome119", "chrome116"]
    edges = ["edge101", "edge99"]
    
    cabeceras_redcomputer = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8,ru;q=0.7",
        "Referer": "https://www.redcomputer.es/bajamos-precios",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    # EXTRAEMOS 25 PÁGINAS IGUAL QUE EN PC COMPONENTES
    for page in range(1, 26):
        print(f"\n--- 📄 EXTRAYENDO PÁGINA {page} VIA API ---")
        exito = False
        intentos = 0
        
        identidades_pagina = random.sample(safaris, 2) + random.sample(chromes, 2) + random.sample(edges, 2)
        random.shuffle(identidades_pagina)
        
        while not exito and intentos < 6: 
            url_api_change = f'https://www.redcomputer.es/bajamos-precios?page={page}&from-xhr'
            try:
                identidad_actual = identidades_pagina[intentos]
                print(f"🕵️ Intentando conexión (Identidad: {identidad_actual})...")
                
                repuesta = requests.get(
                    url_api_change,
                    impersonate=identidad_actual,
                    headers=cabeceras_redcomputer,
                    timeout=15
                )

                if repuesta.status_code == 200:
                    date = repuesta.json()
                    lista_articles = date.get('products', [])
                    
                    for producto in lista_articles:
                        producto['Fecha_Extraccion'] = time.strftime("%Y-%m-%d %H:%M:%S")
                        bag_products.append(producto)
                    
                    print(f"✅ ¡Éxito! Extraídos {len(lista_articles)} productos de la página {page}.")
                    exito = True
                else:
                    print(f"⚠️ Código {repuesta.status_code}. Reintentando...")
                    intentos += 1
                    time.sleep(random.uniform(4.0, 8.0))
            except Exception as e:
                print(f"❌ Error en la conexión: {e}")
                intentos += 1
                time.sleep(6)

        if page < 25:
            tiempo_espera = random.randint(8, 15)
            print(f"⏳ Descansando {tiempo_espera} segundos para enfriar la IP...")
            time.sleep(tiempo_espera)

    return bag_products


# ==========================================
# 3. EJECUCIÓN PRINCIPAL (MAIN)
# ==========================================
if __name__ == "__main__":
    print("🚀 Iniciando Scraper de Red Computer (End-to-End)...")
    
    # 1. Extracción
    datos = extraer_datos_redcomputer_api()
    if not datos:
        print("❌ Error Crítico: No se extrajeron datos de Red Computer.")
        exit(1)
        
    try:
        # 2. Transformación y Limpieza (Data Engineering)
        print("🧹 Limpiando datos y aplicando Traductor Universal...")
        df = pd.DataFrame(datos)
        
        # Limpiar vacíos
        df = df.dropna(subset=['name'])
        
        # Extraer imágenes limpias
        df['URL_Imagen'] = df['cover'].apply(extraer_imagen)
        
        # Corregir el bug matemático de los porcentajes de Red Computer
        df['Descuento'] = 100 - ((df['price_amount'] * 100) / df['regular_price_amount'])
        df['Descuento'] = df['Descuento'].round(0).astype(int)
        
        # APLICAR TRADUCTOR UNIVERSAL
        df['Categoria_nombre'] = df['category_name'].apply(estandarizar_categoria)
        
        # CONSTRUIR EL "MOLDE MAESTRO" (Igual a PcComponentes)
        df_limpio = pd.DataFrame({
            'Nombre': df['Categoria_nombre'] + ' - ' + df['name'],
            'Precio_Actual': df['price_amount'],
            'Precio_Original': df['regular_price_amount'],
            'Descuento': df['Descuento'],
            'URL_Completa': df['url'],
            'URL_Imagen': df['URL_Imagen'],
            'Tienda': 'Red Computer',
            'Categoria_nombre': df['Categoria_nombre'],
            'Fecha': df['Fecha_Extraccion'].str.split(' ').str[0],
            'Hora': df['Fecha_Extraccion'].str.split(' ').str[1]
        })
        
        # Filtrar ofertas reales (mínimo 10% de descuento)
        df_limpio = df_limpio[df_limpio['Descuento'] >= 10]
        
        # Ordenar (Cazachollos)
        df_limpio.sort_values(by=['Descuento', 'Precio_Actual'], ascending=[False, True], inplace=True)
        
        print(f"📊 Total de CHOLLOS listos para la Capa Silver: {len(df_limpio)}")
        
        # 3. Subir a S3 (Directamente a Silver)
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"redcomputer_offers_{fecha_str}_clean.csv"
        
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        bucket_name = os.environ.get('MY_S3_BUCKET')
        
        if aws_access_key and aws_secret_key and bucket_name:
            print("☁️ Subiendo a Amazon S3 (Capa Silver)...")
            s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
            
            # Guardamos a CSV en la memoria RAM
            csv_buffer = io.StringIO()
            df_limpio.to_csv(csv_buffer, index=False)
            
            # Lo mandamos a la carpeta silver
            ruta_s3 = f"silver/{nombre_archivo}"
            
            s3_client.put_object(Bucket=bucket_name, Key=ruta_s3, Body=csv_buffer.getvalue())
            print(f"✅ ¡Éxito! Archivo subido a S3: {ruta_s3}")
        else:
            print("⚠️ Faltan credenciales AWS. Guardando archivo en local para pruebas...")
            df_limpio.to_csv(nombre_archivo, index=False)
            
    except Exception as e:
        print(f"❌ Error crítico en el procesamiento: {e}")
        exit(1)
