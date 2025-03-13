import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Buscador de Ofertas de Portátiles"
    page.window_width = 800
    page.window_height = 1000

    def format_offer(offer):
        return f"""
        🖥️ {offer.get('Procesador', 'N/A')}
        💾 RAM: {offer.get('RAM', 'N/A')}GB {offer.get('Tipo RAM', 'N/A')}
        💽 Almacenamiento: {offer.get('Almacenamiento', 'N/A')}GB
        🎮 Gráficos: {offer.get('Graficos', 'N/A')}
        📺 Pantalla: {offer.get('Pantalla', 'N/A')}" {offer.get('Resolucion', 'N/A')}
        🔋 Batería: {offer.get('Bateria', 'N/A')}Wh
        💰 Precio: {offer.get('Precio', 'N/A')}€
        🔍 Predicción IA: {'✅ CHOLLO' if offer.get('Prediccion_IA') == 1 else '❌ No recomendado'}
        📊 Probabilidad: {offer.get('Probabilidad_IA', 'N/A')}%
        -------------------------------
        """

    def search_offers(e):
        params = {
            "processor": processor_input.value,
            "ram": ram_input.value,
            "ramType": ram_type_input.value,
            "storage": storage_input.value,
            "graphics": graphics_input.value,
            "screen": screen_input.value,
            "resolution": resolution_input.value,
            "os": os_input.value,
            "battery": battery_input.value,
            "price": price_input.value
        }

        result_text.value = "Buscando..."
        page.update()

        try:
            response = requests.post(
                "http://localhost:5000/search_offers",
                json=params,
                timeout=10
            )

            if response.status_code == 200:
                offers = response.json().get("offers", [])
                if offers:
                    result_text.value = "\n".join([format_offer(offer) for offer in offers])
                else:
                    result_text.value = "⚠️ No se encontraron resultados"
            else:
                result_text.value = f"❌ Error del servidor: {response.status_code}"
                
        except Exception as e:
            result_text.value = f"🚨 Error: {str(e)}"
            
        page.update()

    # Componentes UI
    processor_input = ft.TextField(label="Procesador (ej: Intel Core i5)", expand=True)
    ram_input = ft.TextField(label="RAM (GB)", width=150)
    ram_type_input = ft.TextField(label="Tipo RAM (ej: DDR4)", width=150)
    storage_input = ft.TextField(label="Almacenamiento (GB)", width=150)
    graphics_input = ft.TextField(label="Tarjeta Gráfica", width=150)
    screen_input = ft.TextField(label="Tamaño Pantalla", width=150)
    resolution_input = ft.TextField(label="Resolución (ej: 1920x1080)", width=150)
    os_input = ft.TextField(label="Sistema Operativo", width=150)
    battery_input = ft.TextField(label="Batería (Wh)", width=150)
    price_input = ft.TextField(label="Precio Máximo (€)", input_filter=ft.NumbersOnlyInputFilter())
    
    result_text = ft.Text()

    main_content = ft.ListView(
        expand=True,
        spacing=10,
        padding=20,
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text("🔍 Buscador de Portátiles", 
                           size=24, 
                           weight=ft.FontWeight.BOLD,
                           color=ft.colors.BLUE_800),
                    ft.Row([processor_input]),
                    ft.Row([ram_input, ram_type_input]),
                    ft.Row([storage_input, graphics_input]),
                    ft.Row([screen_input, resolution_input]),
                    ft.Row([os_input, battery_input]),
                    ft.Row([price_input]),
                    ft.ElevatedButton(
                        "Buscar",
                        on_click=search_offers,
                        icon=ft.icons.SEARCH,
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_600
                    )
                ], spacing=15),
                padding=20,
                border_radius=10,
                bgcolor=ft.colors.GREY_100
            ),
            ft.Divider(),
            ft.Container(content=result_text, padding=20, expand=True)
        ]
    )

    page.add(main_content)

ft.app(target=main)