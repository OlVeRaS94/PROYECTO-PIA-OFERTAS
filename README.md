# PROYECTO-PIA-OFERTAS

*Analiza y compara ofertas de portátiles de diversas fuentes para facilitar decisiones de compra informadas.*

## 📌 Descripción
PROYECTO-PIA-OFERTAS es una aplicación diseñada para analizar ofertas de portátiles obtenidas desde diferentes fuentes, utilizando APIs y técnicas de scraping. Permite a los usuarios consultar, evaluar y comparar ofertas para tomar decisiones informadas antes de comprar un portátil.

## 🛠️ Tecnologías Utilizadas
- **Frontend:** [HTML](https://developer.mozilla.org/es/docs/Web/HTML), [CSS](https://developer.mozilla.org/es/docs/Web/CSS), [JavaScript](https://developer.mozilla.org/es/docs/Web/JavaScript)
- **Backend:** [Python](https://www.python.org/) ([Flask](https://flask.palletsprojects.com/) / [FastAPI](https://fastapi.tiangolo.com/))
- **Scraping/API:** [Selenium](https://www.selenium.dev/), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/), [Requests](https://docs.python-requests.org/)
- **Base de datos:** [SQLite](https://www.sqlite.org/index.html) / [MongoDB](https://www.mongodb.com/)
- **Otros:** [Pandas](https://pandas.pydata.org/)

## 🚀 Instalación y Uso

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/OlVeRaS94/PROYECTO-PIA-OFERTAS.git
cd PROYECTO-PIA-OFERTAS
```

### 2️⃣ Crear y activar un entorno virtual
```bash
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Ejecutar el backend
```bash
python backend.py  # O el archivo principal del backend
```

### 5️⃣ Ejecutar el frontend con Flet
```bash
python app.py
```

### 6️⃣ Abrir el frontend
Abre `index.html` en tu navegador o usa un servidor local:
```bash
python -m http.server 8000
```
Luego accede a `http://localhost:8000/` en tu navegador.

## 📊 Características del Dataset
El dataset utilizado contiene las siguientes características:

| Característica       | Descripción                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| Procesador           | Tipo y velocidad del procesador (e.g., Intel Core i7, 2.6 GHz)              |
| Memoria RAM          | Cantidad de memoria RAM (e.g., 16 GB)                                       |
| Almacenamiento       | Tipo y capacidad de almacenamiento (e.g., SSD 512 GB)                       |
| Tarjeta Gráfica      | Modelo y memoria de la tarjeta gráfica (e.g., NVIDIA GeForce GTX 1650, 4 GB)|
| Pantalla             | Tamaño y resolución de la pantalla (e.g., 1920x1080)                        |
| Tamaño de Pantalla   | Dimensiones de la pantalla en pulgadas (e.g., 15.6")                        |
| Batería              | Duración de la batería (e.g., 10 horas)                                     |
| Peso                 | Peso del portátil (e.g., 1.5 kg)                                            |
| Sistema Operativo    | Sistema operativo preinstalado (e.g., Windows 10)                           |
| Conectividad         | Puertos y opciones de conectividad (e.g., USB-C, Wi-Fi 6)                   |

## 📬 Contribuciones
Las contribuciones son bienvenidas. Si deseas contribuir:
1. Haz un **fork** del repositorio.
2. Crea una **nueva rama** (`git checkout -b mi-nueva-funcionalidad`).
3. Realiza tus cambios y haz un **commit** (`git commit -m 'Añadir nueva funcionalidad'`).
4. Envía un **pull request**.

## 📩 Contacto
🔗 **GitHub:** [OlVeRaS94](https://github.com/OlVeRaS94), [LuisRosello01](https://github.com/LuisRosello01)

## 📝 Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [`LICENSE`](./LICENSE) para más detalles.
