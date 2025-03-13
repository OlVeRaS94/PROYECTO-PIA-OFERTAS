import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Buscador de Ofertas de Portátiles"
    page.window_width = 1000
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT

    def format_offer(offer):
        return f"""
        🖥️ {offer.get('Procesador', 'N/A')}
        💾 {offer.get('RAM', 'N/A')}GB {offer.get('Tipo RAM', 'N/A')}
        💽 {offer.get('Almacenamiento', 'N/A')}GB | 🎮 {offer.get('Graficos', 'N/A')}
        📺 {offer.get('Pantalla', 'N/A')}\" {offer.get('Resolucion', 'N/A')}
        🔋 {offer.get('Bateria', 'N/A')}Wh | 💰 {offer.get('Precio', 'N/A')}€
        🔍 IA: {'✅ CH0LLO' if offer.get('Prediccion_IA') == 1 else '❌ Regular'} 
        📊 Prob: {offer.get('Probabilidad_IA', 'N/A')}%
        {'='*40}
        """

    def search_offers(e):
        params = {
            "processor": processor.value,
            "ram": ram.value,
            "ramType": ram_type.value,
            "storage": storage.value,
            "graphics": graphics.value,
            "screen": screen.value,
            "resolution": resolution.value,
            "os": os.value,
            "battery": battery.value,
            "price": price.value
        }

        result_text.value = "Buscando ofertas..."
        page.update()

        try:
            response = requests.post(
                "http://localhost:5000/search_offers",
                json=params,
                timeout=15
            )

            if response.status_code == 200:
                offers = response.json().get("offers", [])
                result_text.value = "\n".join([format_offer(o) for o in offers]) if offers else "⚠️ No se encontraron resultados"
            else:
                result_text.value = f"❌ Error del servidor ({response.status_code})"

        except Exception as e:
            result_text.value = f"🚨 Error de conexión: {str(e)}"
        
        page.update()

    # Componentes UI
    processor = ft.TextField(label="Procesador", expand=True)
    ram = ft.TextField(label="RAM mínima (GB)", width=150, input_filter=ft.NumbersOnlyInputFilter())
    ram_type = ft.TextField(label="Tipo RAM", width=150)
    storage = ft.TextField(label="Almacenamiento (GB)", width=150)
    graphics = ft.TextField(label="Tarjeta gráfica", width=150)
    screen = ft.TextField(label="Tamaño pantalla", width=150)
    resolution = ft.TextField(label="Resolución", width=150)
    os = ft.TextField(label="Sistema operativo", width=150)
    battery = ft.TextField(label="Batería (Wh)", width=150)
    price = ft.TextField(label="Precio máximo (€)", input_filter=ft.NumbersOnlyInputFilter())
    
    result_text = ft.Text(selectable=True, size=14)

    page.add(
        ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("FILTROS", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_800),
                    ft.Row([processor]),
                    ft.Row([ram, ram_type, storage]),
                    ft.Row([graphics, screen, resolution]),
                    ft.Row([os, battery, price]),
                    ft.ElevatedButton(
                        "Buscar Ofertas",
                        on_click=search_offers,
                        icon=ft.icons.SEARCH,
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_600,
                        height=50
                    )
                ], spacing=15),
                padding=20,
                border_radius=10,
                bgcolor=ft.colors.GREY_100
            ),
            ft.Divider(height=20),
            ft.Container(
                content=ft.Column([
                    ft.Text("RESULTADOS", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=result_text,
                        padding=10,
                        border_radius=10,
                        bgcolor=ft.colors.GREY_50,
                        expand=True
                    )
                ]),
                expand=True
            )
        ], expand=True)
    )

ft.app(target=main)