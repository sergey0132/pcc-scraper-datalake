import undetected_chromedriver as uc
import subprocess
import re

def get_chrome_version():
    try:
        version = subprocess.check_output(['google-chrome', '--version']).decode('utf-8')
        return int(re.search(r'Google Chrome (\d+)', version).group(1))
    except:
        return None

def configurar_driver():
    options = uc.ChromeOptions()
    
    # ⚠️ NO QUITAR: Necesarios para el servidor
    options.add_argument('--headless') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # 🕵️ MODO NINJA ACTIVADO
    # 1. User-Agent: Fingimos ser Windows 11 (la clave del éxito)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    options.add_argument(f'user-agent={user_agent}')

    # 2. Resolución de pantalla real
    options.add_argument('--window-size=1920,1080')

    # 3. Evitar que sepan que somos automatizados
    options.add_argument("--disable-blink-features=AutomationControlled") 

    version_principal = get_chrome_version()
    driver = uc.Chrome(options=options, version_main=version_principal)
    
    return driver
