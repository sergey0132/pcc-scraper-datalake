# 🤖 PC Componentes Serverless Data Pipeline & Telegram Bot

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![AWS](https://img.shields.io/badge/AWS-S3_%7C_Lambda-FF9900?style=for-the-badge&logo=amazon-aws)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?style=for-the-badge&logo=github-actions)
![Telegram](https://img.shields.io/badge/Telegram_API-Bot-2CA5E0?style=for-the-badge&logo=telegram)

## 📌 Descripción del Proyecto
Este proyecto es un **Data Pipeline 100% Serverless** diseñado para extraer, procesar y servir las mejores ofertas tecnológicas de la web de PC Componentes. 

En lugar de un simple script, he implementado una **Arquitectura Medallion** (Bronze / Silver) alojada en AWS, donde los datos son extraídos automáticamente, limpiados en la nube y servidos bajo demanda a través de una interfaz interactiva de Telegram.

## 🏗️ Arquitectura y Flujo de Datos

El sistema se divide en tres fases principales:

1. **Extracción Automática (Capa Bronze) - *GitHub Actions***
   * Un bot programado mediante CRON jobs en GitHub Actions se ejecuta automáticamente.
   * Utiliza la librería `curl_cffi` para suplantar identidades de navegadores (Chrome, Edge, Safari) y evadir las medidas de seguridad Anti-Bot (Cloudflare).
   * Los datos crudos (formato JSON/CSV) se suben directamente a un bucket de **Amazon S3 (Bronze)**.

2. **Procesamiento y Limpieza (Capa Silver) - *AWS Lambda***
   * La llegada de un nuevo archivo al bucket dispara un evento (S3 Trigger) que despierta una función de **AWS Lambda**.
   * Mediante `pandas`, los datos se limpian, se estructuran, se eliminan nulos y se reconstruyen las URLs completas de los productos.
   * El DataFrame procesado se guarda en la carpeta **S3 (Silver)**, listo para el consumo.

3. **Consumo de Datos (Interfaz) - *Telegram Bot***
   * Una segunda función **AWS Lambda** actúa como Webhook para el bot de Telegram.
   * Lee el archivo más reciente de la capa Silver y se lo sirve al usuario a través de un chat interactivo, utilizando menús dinámicos y botones *Inline*.

## 🚀 Retos Técnicos Resueltos
* **Evasión de Sistemas Anti-Bots (Código 403):** Superación de los bloqueos de Cloudflare implementando rotación dinámica de `User-Agents`, *impersonation* de TLS y pausas aleatorias de conexión.
* **Seguridad de Credenciales:** Inyección de claves de AWS y Tokens de Telegram mediante *GitHub Secrets* y variables de entorno (`os.environ`), manteniendo el repositorio público completamente seguro.
* **Tolerancia a Fallos:** Implementación de funciones "escudo" (`safe_eval`) en el procesamiento de datos para evitar que la Lambda se rompa ante cambios inesperados en la estructura del JSON de origen.

## 💻 Tecnologías Utilizadas
* **Lenguaje:** Python
* **Librerías principales:** `pandas`, `boto3`, `curl_cffi` (Requests), `pyTelegramBotAPI` (Telebot).
* **Infraestructura (Cloud):** Amazon S3 (Data Lake), AWS Lambda (Computación serverless).
* **Orquestación:** GitHub Actions (CI/CD y Cron Jobs).

## 📱 Demostración
Puedes probar el bot buscando en Telegram: **@Ofertas_componentes_bot** 

---
*Proyecto creado como demostración de habilidades en Data Engineering y automatización en la nube.*
