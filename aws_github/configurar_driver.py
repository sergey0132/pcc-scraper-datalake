import undetected_chromedriver as uc

def configurar_driver():
    # Usamos las opciones especiales del driver indetectable
    options = uc.ChromeOptions()
    
    # 💡 TRUCO PRO: Cuando luchas contra Cloudflare, es mejor que el navegador 
    # SE VEA (no usar modo headless/oculto) al menos las primeras veces.
    options.add_argument('--headless') 
    options.add_argument('--no-sandbox')
    
    # Desactivamos el popup molesto de "Chrome está siendo controlado..."
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-blink-features=AutomationControlled") 

    # Inicializamos el navegador "Ninja"
    driver = uc.Chrome(options=options)
    
    return driver