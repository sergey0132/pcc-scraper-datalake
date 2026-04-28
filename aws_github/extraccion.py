import os
import time
import json
import pandas as pd
import boto3
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from configurar_driver import configurar_driver
from subir_s3 import subir_a_s3, S3_BUCKET_NAME




# --- LÓGICA DE SCRAPING ---
def extraer_datos_pccom():
    driver = configurar_driver()
    datos = []

    # 1. DEFINIMOS LA URL
    url_objetivo = "https://www.pccomponentes.com/ofertas-especiales?sort=discount"

    try:
        # 2. ENTRAMOS A LA PÁGINA
        driver.get(url_objetivo)

        # 3. CREAMOS EL "ESPERADOR"
        wait = WebDriverWait(driver, 15) # Espera máxima de 15 segundos para cada elemento

        # ---------------------------------------------------------
        # MODO HACKER: NAVEGACIÓN CON JAVASCRIPT
        # ---------------------------------------------------------
        
        # PASO A: Abrir el menú de categorías
        boton_menu = wait.until(EC.presence_of_element_located((By.ID, "menu-btn-text"))) 
        driver.execute_script("arguments[0].click();", boton_menu)
        print("✅ Menú abierto (JS)")
        time.sleep(2) 

        # PASO B: Clic en el botón general de Ofertas
        boton_ofertas = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='normal-link']")))
        driver.execute_script("arguments[0].click();", boton_ofertas)
        print("✅ Entrando a sección Ofertas (JS)")
        time.sleep(2)

        # PASO C: Clic en el banner des ofertas especiales
        selector_acer = 'a[href="/ofertas-especiales"]'
        boton_acer = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_acer)))
        driver.execute_script("arguments[0].click();", boton_acer)
        print("✅ Entrando a Acer Week (JS)")
        time.sleep(3) 

        # PASO D: Abrir el desplegable de ordenar
        boton_ordenar = wait.until(EC.presence_of_element_located((By.ID, "sort-select-listbox")))
        driver.execute_script("arguments[0].click();", boton_ordenar)
        print("✅ Desplegable de orden abierto (JS)")
        time.sleep(1)

        # PASO E: Seleccionar "Mayor descuento"
        boton_oferta = wait.until(EC.presence_of_element_located((By.ID, "sort-option-discount")))
        driver.execute_script("arguments[0].click();", boton_oferta)
        print("✅ Ordenando por descuento (JS)")
        time.sleep(3) 

        # ---------------------------------------------------------
        # 🔄 BUCLE DE PAGINACIÓN (Empezamos a navegar por páginas)
        # ---------------------------------------------------------
        max_paginas = 5 # Cambia este número si quieres extraer más o menos páginas

        for pagina in range(1, max_paginas + 1):
            print(f"\n--- 📄 EXTRAYENDO PÁGINA {pagina} ---")

            # 🔥 CAMBIO CLAVE: HACEMOS SCROLL PRIMERO PARA FORZAR LA CARGA 🔥
            print("⏬ Haciendo scroll inicial para cargar todos los productos (Lazy Loading)...")
            for i in range(1, 5):
                driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * ({i}/4));")
                time.sleep(1) # Esperamos 1 segundo por cada "bajón" para que las fotos carguen
            
            time.sleep(2) # Respiro extra antes de extraer

            # Buscamos todos los productos en la página actual ¡Ahora sí estarán todos!
            productos = driver.find_elements(By.CSS_SELECTOR, '[class="container-iTDhwB product-card productCard-Y_mbUE"]')
            print(f"🔍 Se encontraron {len(productos)} productos listos para extraer.")

            # BUCLE DE EXTRACCIÓN
            for p in productos:
                try:
                    nombre = p.find_element(By.CSS_SELECTOR, "h3").text 
                    precio_actual = p.find_element(By.CSS_SELECTOR, "[data-e2e='price-card']").text
                    precio_original = p.find_element(By.CSS_SELECTOR, "[data-e2e='crossedPrice']").text

                    try:
                        descuento = p.find_element(By.CSS_SELECTOR, "[class='discountContainer-JoBi1P']").text
                    except:
                        descuento = "Sin descuento"

                    try:
                        rating = p.find_element(By.CSS_SELECTOR, "[class='rating-module_text__WmVxK rating-module_bold__FFtZp']").text
                    except:
                        rating = "N/A"
                    
                    try:
                        opiniones = p.find_element(By.CSS_SELECTOR, "[class='rating-module_text__WmVxK']").text
                    except:
                        opiniones = "N/A"
                        # 5. Extraer la URL de la Imagen
                    try:
                        # Buscamos la etiqueta de imagen y sacamos su enlace (src)
                        imagen_url = p.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                    except:
                        imagen_url = "Sin imagen"

                    # --- INICIO BLOQUE URL NINJA ---
                    url_producto = "Sin URL" # Por defecto
                    url_bruta = None
                    
                    # --- INICIO BLOQUE URL JAVASCRIPT ---
                    try:
                        # Buscamos hacia arriba (ancestro) la primera etiqueta a
                        elemento_enlace = p.find_element(By.XPATH, "./ancestor::a | .//a[@href]")
                        url_bruta = elemento_enlace.get_attribute("href")
                        
                        if url_bruta:
                            if url_bruta.startswith("/"):
                                url_producto = "https://www.pccomponentes.com" + url_bruta
                            else:
                                url_producto = url_bruta
                        else:
                            url_producto = "Sin URL"
                    except Exception as e:
                        url_producto = "Sin URL"

                    # Guardamos todo en la lista de datos
                    datos.append({
                        "Nombre": nombre,
                        "Precio_Actual" : precio_actual,
                        "Precio_Original": precio_original,
                        "Descuento": descuento,
                        "Valoracion": rating,
                        "Opiniones": opiniones,
                        "Imagen_URL": imagen_url,
                        "Fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "URL" : url_producto
                    })
                except Exception as e:
                    print(f"⚠️ Error al extraer un producto: {e}")

                    # ---------------------------------------------------------
                    # PASAR A LA SIGUIENTE PÁGINA
                    # ---------------------------------------------------------
                    if pagina < max_paginas:
                        try:
                            print("➡️ Buscando el botón de Siguiente...")
                            selector_siguiente = '[data-testid="icon_right"]'
                            boton_siguiente = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_siguiente)))
                            
                            # Nos aseguramos de estar viendo el botón
                            print("⏬ Centrando el botón en pantalla...")
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton_siguiente)
                            time.sleep(2) 
                            
                            # CLIC HACKER
                            driver.execute_script("arguments[0].click();", boton_siguiente)
                            print(f"✅ Clic en 'Siguiente' realizado. Cargando página {pagina + 1}...")
                            
                            # Tiempo para que la nueva web cargue completa antes de volver a empezar el bucle
                            time.sleep(4) 
                            
                        except Exception as e:
                            print("🛑 No se encontró el botón de Siguiente. Llegamos al final de los resultados.")
                            break

    finally:
        # Cerramos el navegador
        driver.quit()
        
    return datos

# --- FLUJO PRINCIPAL ---
if __name__ == "__main__":
    lista_productos = extraer_datos_pccom()
    
    if lista_productos:
        df = pd.DataFrame(lista_productos)
        
        # Guardamos local y subimos a la carpeta BRONZE
        filename = f"pcc_offers_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        
        # Subimos a S3 (Asegúrate de tener la carpeta 'bronze' creada en tu bucket)
        subir_a_s3(filename, S3_BUCKET_NAME, "bronze")
        
        print(f"🏁 Scraping exitoso. {len(df)} productos en la capa Bronze.")
