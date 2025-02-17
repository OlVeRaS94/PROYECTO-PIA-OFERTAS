import os
import asyncio
import json
from pydantic import BaseModel, Field
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy

INSTRUCTION_TO_LLM = """
Analiza la tabla HTML de especificaciones técnicas y extrae la siguiente información específica:

1. Para el procesador:
   - Busca "Modelo del procesador" y extrae su valor
   
2. Para la memoria:
   - Busca "Memoria interna" y extrae su valor en GB

3. Para el almacenamiento:
   - Busca "Capacidad total de almacenaje" y extrae su valor

4. Para los gráficos:
   - Busca "Modelo de adaptador gráfico incorporado" y extrae su valor

5. Para la pantalla:
   - Combina "Diagonal de la pantalla" y "Resolución de la pantalla"

6. Para el sistema operativo:
   - Busca "Sistema operativo instalado" y extrae su valor

7. Para la batería:
   - Busca "Capacidad de batería" y extrae su valor

Devuelve los datos extraídos en un único objeto JSON con los campos exactamente como se definen en el esquema:
{
    "procesador": "valor",
    "memoria": "valor",
    "almacenamiento": "valor",
    "graficos": "valor",
    "pantalla": "valor",
    "sistema_operativo": "valor",
    "bateria": "valor"
}
"""

class Product(BaseModel):
    procesador: str = Field(description="Modelo del procesador")
    memoria: str = Field(description="Memoria interna en GB")
    almacenamiento: str = Field(description="Capacidad total de almacenaje")
    graficos: str = Field(description="Modelo de adaptador gráfico incorporado")
    pantalla: str = Field(description="Diagonal y resolución de la pantalla")
    sistema_operativo: str = Field(description="Sistema operativo instalado")
    bateria: str = Field(description="Capacidad de batería")

async def main():
    # 1. Define the LLM extraction strategy
    llm_strategy = LLMExtractionStrategy(
        provider="ollama/deepseek-custom",            # e.g. "ollama/llama2"
        api_token="",
        schema=Product.model_json_schema(),            # Or use model_json_schema()
        extraction_type="schema",
        instruction=INSTRUCTION_TO_LLM,
        chunk_token_threshold=2048,
        overlap_rate=0.1,
        apply_chunking=True,
        input_format="html",   # or "html", "fit_markdown"
        extra_args={
        "temperature": 0.0,
        "max_tokens": 8192,     # Aumentado
        "top_p": 0.1
        }
    )

    # 2. Build the crawler config
    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS,
        process_iframes=False,
        remove_overlay_elements=True,
        exclude_external_links=True,
        css_selector="tr.vtex-table-description-content",
        excluded_selector="div.vtex-render__container-id-product-comparator"
    )

    # 3. Create a browser config if needed
    browser_cfg = BrowserConfig(headless=True, verbose=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # 4. Let's say we want to crawl a single page
        result = await crawler.arun(
            url="https://www.pcbox.com/ht5306qa-lx004w-portatil-asus-proart-ht5306qa-lx004w--13-3--2k--snapdragon-x1-p/p",
            config=crawl_config
        )

        if result.success:
            # 5. The extracted content is presumably JSON
            data = json.loads(result.extracted_content)
            print("Extracted items:", data)

            # 6. Show usage stats
            llm_strategy.show_usage()  # prints token usage
        else:
            print("Error:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())