from flask import Blueprint, request, send_file, jsonify
from services.excel_service import generar_excel_gastos
from services.pdf_service import generar_pdf_gastos
import traceback # <--- Agregamos esto para ver errores reales en la terminal

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/export-excel', methods=['POST'])
def export_excel():
    try:
        payload = request.json
        excel_file = generar_excel_gastos(payload) 

        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='Reporte_Finanzas.xlsx'
        )
    except Exception as e:
        traceback.print_exc() # Imprime el error exacto en la terminal de Ubuntu
        return jsonify({"error": str(e)}), 500

@reports_bp.route('/export-pdf', methods=['POST'])
def export_pdf():
    try:
        payload = request.json
        # Verificamos que lleguen movimientos
        if not payload or 'movimientos' not in payload:
            return jsonify({"error": "No se recibieron movimientos"}), 400

        pdf_file = generar_pdf_gastos(payload)

        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='Reporte_Finanzas.pdf'
        )
    except Exception as e:
        traceback.print_exc() # Esto te dirá en la terminal si falta una librería o falló el PDF
        return jsonify({"error": str(e)}), 500