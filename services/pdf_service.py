from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

def generar_pdf_gastos(payload):
    # Extraemos con seguridad
    data = payload.get('movimientos', [])
    titulo_ciclo = payload.get('titulo', 'REPORTE DE MOVIMIENTOS')
    
    # 1. Cálculos de Totales (Asegurando que sean números)
    def clean_num(val):
        try: return float(val) if val is not None else 0.0
        except: return 0.0

    total_ingresos = sum(clean_num(item.get('amount')) for item in data if item.get('type') == 'ingreso')
    total_gastos = sum(clean_num(item.get('amount')) for item in data if item.get('type') == 'gasto')
    total_ahorro = sum(clean_num(item.get('amount')) for item in data if item.get('type') == 'ahorro')
    saldo_final = total_ingresos - total_gastos - total_ahorro

    output = io.BytesIO()
    # Usamos márgenes un poco más amplios para evitar cortes
    doc = SimpleDocTemplate(output, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    # --- ESTILOS ---
    style_titulo = ParagraphStyle(
        'TituloPremium',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.white,
        backColor=colors.HexColor("#374151"),
        alignment=1, # Centro
        spaceAfter=20,
        borderPadding=10
    )

    # --- ENCABEZADO ---
    elements.append(Paragraph(titulo_ciclo, style_titulo))
    elements.append(Spacer(1, 15))

    # --- TABLA DE MOVIMIENTOS ---
    # Encabezados de la tabla
    table_data = [['Fecha', 'Descripción', 'Categoría', 'Monto']]
    
    for item in data:
        raw_monto = clean_num(item.get('amount'))
        tipo = item.get('type', 'gasto')
        
        # Lógica de signos para el PDF
        monto_display = raw_monto * -1 if tipo in ['gasto', 'ahorro'] else raw_monto
        
        # Fecha limpia
        fecha_raw = item.get('created_at', '')
        fecha_corta = fecha_raw[:10] if fecha_raw else "S/F"

        table_data.append([
            fecha_corta,
            str(item.get('description_user', 'Sin desc.'))[:25], # Truncamos descripción
            str(item.get('category', 'General')),
            f"${monto_display:,.0f}"
        ])

    # Configuración de anchos: Total 530 puntos aprox para tamaño Letter
    t = Table(table_data, colWidths=[80, 200, 130, 90])
    
    # Estilo base de la tabla
    estilo_tabla = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#374151")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]

    # Colores dinámicos por fila para la columna Monto
    for i in range(1, len(table_data)):
        tipo = data[i-1].get('type', 'gasto')
        color_fila = colors.HexColor("#15803D") # Verde
        if tipo == 'gasto': color_fila = colors.HexColor("#E11D48") # Rojo
        elif tipo == 'ahorro': color_fila = colors.HexColor("#1D4ED8") # Azul
        
        estilo_tabla.append(('TEXTCOLOR', (3, i), (3, i), color_fila))
        estilo_tabla.append(('FONTNAME', (3, i), (3, i), 'Helvetica-Bold'))

    t.setStyle(TableStyle(estilo_tabla))
    elements.append(t)
    
   # --- SALDO FINAL (TEXTO GRIS CON MONTO DINÁMICO) ---
    elements.append(Spacer(1, 40))
    
    # Definimos el color del monto (verde o rojo)
    color_monto = colors.HexColor("#15803D") if saldo_final >= 0 else colors.HexColor("#E11D48")
    hex_monto = "#15803D" if saldo_final >= 0 else "#E11D48"

    # Estilo base en gris oscuro #374151
    style_saldo = ParagraphStyle(
        'SaldoFinal',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor("#374151"), # El color que pediste para el texto
        alignment=2, # Alineado a la derecha
        fontName='Helvetica-Bold'
    )
    
    # Usamos tags de HTML internos de ReportLab para darle color solo al número
    texto_label = "SALDO NETO FINAL DEL CICLO: "
    monto_formateado = f"${saldo_final:,.0f}"
    
    # Construimos el párrafo con el número en color dinámico
    p_html = f'{texto_label}<font color="{hex_monto}">{monto_formateado}</font>'
    
    elements.append(Paragraph(p_html, style_saldo))

    # Construir PDF
    try:
        doc.build(elements)
    except Exception as e:
        print(f"Error construyendo el doc: {e}")
        raise e

    output.seek(0)
    return output