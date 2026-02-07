from flask import Flask
from flask_cors import CORS
import os

print("--- Iniciando carga de módulos ---")

try:
    from routes.reports import reports_bp
    print("✅ Módulo de rutas cargado")
except Exception as e:
    print(f"❌ Error importando rutas: {e}")
    reports_bp = None

# 1. Crear la instancia de Flask PRIMERO
app = Flask(__name__)

# 2. Configurar CORS (Sin la barra '/' al final de la URL de Vercel)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://dashboard-gastos-brown.vercel.app", 
            "http://localhost:5173"
        ]
    }
})
if reports_bp:
    app.register_blueprint(reports_bp, url_prefix='/api')

@app.route('/test')
def test():
    return {"status": "ok", "message": "Si ves esto, Flask vive"}

# 3. Preparar para el puerto de Render
if __name__ == '__main__':
    # Render usa una variable de entorno llamada PORT
    port = int(os.environ.get("PORT", 5000))
    print(f"📡 Servidor levantándose en el puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=True)