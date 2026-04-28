import undetected_chromedriver as uc
import subprocess
import re

def get_chrome_version():
    # Truco para saber qué versión real de Chrome hay instalada en el sistema
    try:
        version = subprocess.check_output(['google-chrome', '--version']).decode('utf-8')
        # Extraemos solo el número principal (ej: 147)
        return int(re.search(r'Google Chrome (\d+)', version).group(1))
    except:
        return None

def configurar_driver():
    options = uc.ChromeOptions()
    
    options.add_argument('--headless') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-blink-features=AutomationControlled") 

    # Intentamos detectar la versión del sistema para que no haya fallos
    version_principal = get_chrome_version()

    # Inicializamos el navegador pasando la versión exacta que encontramos
    driver = uc.Chrome(options=options, version_main=version_principal)
    
    return driver
