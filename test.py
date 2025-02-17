import asyncio
from crawl4ai import AsyncWebCrawler

async def extract_laptop_features(url):
    """
    Extrae características de portátiles de una página con la estructura VTEX.
    Se definen reglas para localizar:
      - Procesador: se combinan "Modelo del procesador" y "Frecuencia del procesador"
      - Memoria RAM: se extrae "Memoria interna"
      - Almacenamiento: se combinan "SDD, capacidad" y "Unidad de almacenamiento"
      - Tarjeta Gráfica: se extrae "Modelo de adaptador gráfico incorporado"
      - Pantalla: se extrae "Resolución de la pantalla"
      - Tamaño de Pantalla: se extrae "Diagonal de la pantalla"
      - Batería: se extrae "Capacidad de batería"
      - Peso: se extrae "Peso" (dentro de "Peso y dimensiones")
      - Sistema Operativo: se extrae "Sistema operativo instalado"
    """
    extraction_rules = {
        # Procesador: se extrae modelo y frecuencia para luego combinarlos
        "procesador_modelo": {
            "selector": "tr.vtex-table-description-row:has(td.vtex-table-description-key b:contains('Modelo del procesador')) td.vtex-table-description-value",
            "attribute": "text"
        },
        "procesador_frecuencia": {
            "selector": "tr.vtex-table-description-row:has(td.vtex-table-description-key b:contains('Frecuencia del procesador')) td.vtex-table-description-value",
            "attribute": "text"
        },
        # Memoria RAM: se extrae la "Memoria interna"
        "memoria_ram": {
            "selector": "tr.vtex-table-description-row:has(td.vtex-table-description-key b:contains('Memoria interna')) td.vtex-table-description-value",
            "attribute": "text"
        },
        # Almacenamiento: se extraen capacidad y tipo
        "almacenamiento_capacidad": {
            "selector": "tr.vtex-table-description-row:has(td.vtex-table-description-key b:contains('SDD, capacidad')) td.vtex-table-description-value",
            "attribute": "text"
        },
        "almacenamiento_tipo": {
            "selector": "tr.vtex-table-description-row:has(td.vtex-table-description-key b:contains('Unidad de almacenamiento')) td.vtex-table-description-value",
            "attribute": "text"
        },
        # Tarjeta Gráfica: se extrae el modelo del adaptador gráfico incorporado
        "tarjeta_grafica": {
            "selector": "tr.vtex-table-description-row:has(td.vtex-table-description-key b:contains('Modelo de adaptador gráfico incorporado')) td.vtex-table-description-value",
            "attribute": "text"
        },
        # Pantalla: se extrae la resolución de la pantalla
        "pantalla": {
            "selector": "tr.vtex-table-description-row:has(td.vtex-table-description-key b:contains('Resolución de la pantalla')) td.vtex-table-description-value",
            "attribute": "text"
        },
        # Tamaño de Pantalla: se extrae la diagonal de la pantalla
        "tamano_pantalla": {
            "selector": "tr.vtex-table-description-row:has(td.vtex-table-description-key b:contains('Diagonal de la pantalla')) td.vtex-table-description-value",
            "attribute": "text"
        },
        # Batería: se extrae la capacidad de la batería
        "bateria": {
            "selector": "tr.vtex-table-description-row:has(td.vtex-table-description-key b:contains('Capacidad de batería')) td.vtex-table-description-value",
            "attribute": "text"
        },
        # Peso: se extrae la fila que contiene "Peso"
        "peso": {
            "selector": "tr.vtex-table-description-row:has(td.vtex-table-description-key b:contains('Peso')) td.vtex-table-description-value",
            "attribute": "text"
        },
        # Sistema Operativo: se extrae el sistema operativo instalado
        "sistema_operativo": {
            "selector": "tr.vtex-table-description-row:has(td.vtex-table-description-key b:contains('Sistema operativo instalado')) td.vtex-table-description-value",
            "attribute": "text"
        }
    }

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, extraction=extraction_rules)
        # Supongamos que result.markup o result.dict() nos da un diccionario con los valores extraídos.
        # Para este ejemplo asumimos que podemos acceder a los resultados como un diccionario:
        data = result.dict() if hasattr(result, "dict") else result

        # Post-procesado: combinar campos para "procesador" y "almacenamiento"
        modelo = data.get("procesador_modelo", "").strip()
        frecuencia = data.get("procesador_frecuencia", "").strip()
        data["procesador"] = f"{modelo} - {frecuencia}" if modelo and frecuencia else modelo or frecuencia

        alm_tipo = data.get("almacenamiento_tipo", "").strip()
        alm_capacidad = data.get("almacenamiento_capacidad", "").strip()
        data["almacenamiento"] = f"{alm_tipo} {alm_capacidad}" if alm_tipo and alm_capacidad else alm_tipo or alm_capacidad

        # Opcional: eliminar las claves intermedias si no se necesitan
        for key in ["procesador_modelo", "procesador_frecuencia", "almacenamiento_tipo", "almacenamiento_capacidad"]:
            data.pop(key, None)

        return data

async def main():
    url = "https://www.pcbox.com/ht5306qa-lx004w-portatil-asus-proart-ht5306qa-lx004w--13-3--2k--snapdragon-x1-p/p"  # Reemplaza por la URL real del producto
    features = await extract_laptop_features(url)
    print("Características extraídas:")
    for key, value in features.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
