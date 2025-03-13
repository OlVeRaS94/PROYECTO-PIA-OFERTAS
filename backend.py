from flask import Flask, request, jsonify
import pandas as pd
import joblib
import numpy as np

app = Flask(__name__)

# Cargar modelo y preprocesador
try:
    model = joblib.load('/home/aluvesprada/Documentos/PROYECTO_PIA/PROYECTO-PIA-OFERTAS/model/model_chollo.pkl')
    preprocesador = joblib.load('/home/aluvesprada/Documentos/PROYECTO_PIA/PROYECTO-PIA-OFERTAS/model/preprocessor.pkl')
    print("✅ Modelo y preprocesador cargados correctamente")
except Exception as e:
    print(f"❌ Error cargando modelos: {str(e)}")
    raise

@app.route('/search_offers', methods=['POST'])
def search_offers():
    try:
        # 1. Cargar datos y parámetros
        df = pd.read_csv('chollos.csv')
        filters = request.json
        print("\n🔍 Filtros recibidos:", filters)
        
        # 2. Aplicar filtros básicos
        filtered_df = df.copy()
        
        # Filtro por procesador
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
                if key in ["ram", "storage", "battery", "price"]:
                    filtered_df = filtered_df[filtered_df[col] <= float(filters[key])]
                else:
                    filtered_df = filtered_df[filtered_df[col] == filters[key]]
        
        print("📊 Datos después de filtros básicos:", filtered_df.shape[0])
        
        # 3. Aplicar IA si hay resultados
        if not filtered_df.empty:
            try:
                # Preprocesamiento
                X_pred = preprocesador.transform(filtered_df)
                
                # Predicción
                probabilidades = model.predict_proba(X_pred)[:, 1]
                predicciones = model.predict(X_pred)
                
                # Añadir resultados
                filtered_df['Prediccion_IA'] = predicciones.astype(int)
                filtered_df['Probabilidad_IA'] = np.round(probabilidades * 100, 1)
                
                # Filtrar por IA
                filtered_df = filtered_df[filtered_df['Prediccion_IA'] == 1]
                print("🎯 Ofertas después de IA:", filtered_df.shape[0])
                
            except Exception as e:
                print(f"❌ Error en IA: {str(e)}")
                return jsonify({"error": f"Error en IA: {str(e)}"}), 500
        
        # 4. Formatear respuesta
        result_df = filtered_df.replace({np.nan: None})
        return jsonify({
            "offers": result_df.to_dict(orient='records')
        })
    
    except Exception as e:
        print(f"🔥 Error crítico: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)