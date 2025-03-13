from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/search_offers', methods=['POST'])
def search_offers():
    try:
        filters = request.json
        df = pd.read_csv('chollos.csv')

        # Aplicar filtros
        filtered_df = df.copy()
        
        # Filtro por procesador (búsqueda parcial insensible a mayúsculas)
        if filters.get("processor"):
            filtered_df = filtered_df[
                filtered_df["Procesador"].str.contains(
                    filters["processor"], 
                    case=False, 
                    na=False
                )
            ]

        # Filtros numéricos/exactos
        exact_filters = {
            "ram": "RAM",
            "ramType": "Tipo RAM",
            "storage": "Almacenamiento",
            "graphics": "Graficos",
            "screen": "Pantalla",
            "resolution": "Resolucion",
            "os": "Sistema Operativo",
            "battery": "Bateria",
            "price": "Precio"
        }

        for key, col in exact_filters.items():
            if filters.get(key):
                if key in ["ram", "storage", "battery", "price"]:  # Campos numéricos
                    filtered_df = filtered_df[filtered_df[col] <= float(filters[key])]
                else:  # Campos de texto exacto
                    filtered_df = filtered_df[filtered_df[col] == filters[key]]

        # Filtrar SOLO ofertas buenas (Chollo = 1)
        filtered_df = filtered_df[filtered_df["Chollo"] == 1]
        
        # Formatear resultados
        filtered_df.fillna("N/A", inplace=True)
        filtered_df["es_buena_oferta"] = "✅ Buena oferta"
        
        return jsonify({
            "offers": filtered_df.astype(str).to_dict(orient='records')
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)