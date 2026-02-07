from flask import Flask
from flask_cors import CORS

print("--- Iniciando carga de módulos ---")

try:
    from routes.reports import reports_bp
    print("✅ Módulo de rutas cargado")
except Exception as e:
    print(f"❌ Error importando rutas: {e}")
    reports_bp = None

app = Flask(__name__)
CORS(app)

if reports_bp:
    app.register_blueprint(reports_bp, url_prefix='/api')

@app.route('/test')
def test():
    return {"status": "ok", "message": "Si ves esto, Flask vive"}

if __name__ == '__main__':
    print("📡 Servidor levantándose en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)