# 🚀 Portfolio Web Dinámico - Django

![Estado](https://img.shields.io/badge/DESARROLLO-COMPLETADO-brightgreen?style=for-the-badge&logo=check-circle&logoColor=white)

Este es un proyecto de **Portafolio Web Profesional** diseñado para ser altamente personalizable y fácil de desplegar. Construido con **Django 6.0**, permite a los desarrolladores y creativos gestionar su marca personal de forma dinámica a través de un panel administrativo intuitivo.


---

## ✨ Características Principales

-   **🎨 Personalización en Tiempo Real:** Cambia los colores de fondo, botones, navbar y secciones directamente desde el panel administrativo sin tocar una línea de código.
-   **💼 Gestión de Experiencia:** Sección de trayectoria profesional con soporte para texto enriquecido (CKEditor).
-   **🛠️ Vitrina de Proyectos:** Muestra tus trabajos con enlaces a GitHub, descripciones detalladas y etiquetas de tecnologías.
-   **⚡ Optimizado para Rendimiento:** Uso de **WhiteNoise** para archivos estáticos y **Gunicorn** para producción.
-   **🐳 Docker Ready:** Configuración completa con Docker y Docker Compose para un desarrollo y despliegue consistentes.
-   **📱 Diseño Responsivo:** Adaptable a cualquier dispositivo mediante Bootstrap Icons y CSS moderno.

---

## 🛠️ Tech Stack

![Django](https://img.shields.io/badge/django-%23092e20.svg?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511fa.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![Render](https://img.shields.io/badge/Render-%23430098.svg?style=for-the-badge&logo=render&logoColor=white)

---

## 🚀 Instalación y Uso Local

### Requisitos Previos
- Python 3.12+
- Docker (opcional para desarrollo, recomendado para producción)

### Pasos para Configuración Manual
1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd Web_Portafolio
    ```

2.  **Configurar el entorno virtual:**
    ```bash
    python -m venv env
    .\env\Scripts\activate  # En Windows
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r portafolio/requirements.txt
    ```

4.  **Configurar variables de entorno:**
    Crea un archivo `.env` en la raíz (puedes basarte en el ejemplo existente) con tus credenciales de base de datos.

5.  **Ejecutar migraciones y servidor:**
    ```bash
    cd portafolio
    python manage.py migrate
    python manage.py runserver
    ```

### Uso con Docker 🐳
Si prefieres usar Docker, simplemente ejecuta:
```bash
docker-compose up --build
```
Esto levantará el servidor de Django y la base de datos PostgreSQL automáticamente.

---

## ⚙️ Personalización

El portafolio incluye un modelo de **Personalización** único. Desde `/admin`, puedes modificar:
-   **Paleta de Colores:** Botones, títulos, fondos y cartas.
-   **Secciones:** Colores específicos para "Sobre Mí", "Experiencia", "Proyectos" y "Contacto".
-   **Iconos:** Soporte integrado para Bootstrap Icons.

---

## 📂 Estructura del Proyecto

```text
Web_Portafolio/
├── portafolio/          # Directorio raíz de Django
│   ├── App/             # Lógica de la aplicación (Modelos, Vistas)
│   ├── portafolio/      # Configuración del proyecto (Settings, URLs)
│   └── manage.py
├── Dockerfile           # Configuración de imagen Docker
├── docker-compose.yml   # Orquestación de contenedores
├── render.yaml          # Configuración para despliegue en Render
└── nginx.conf           # Configuración del servidor web
```

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Siéntete libre de usarlo y mejorarlo.

---
Creado con ❤️ por [Tu Nombre/GitHub]
