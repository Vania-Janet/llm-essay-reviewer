from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from io import BytesIO
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=colors.HexColor('#1a365d')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            leading=14,
            spaceBefore=10,
            spaceAfter=5,
            textColor=colors.HexColor('#2c5282'),
            borderPadding=2,
            borderColor=colors.HexColor('#e2e8f0'),
            borderWidth=0,
            borderBottomWidth=1
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompactNormal',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.HexColor('#2d3748')
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompactBold',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.HexColor('#2d3748'),
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='TableText',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#4a5568'),
            alignment=TA_JUSTIFY
        ))
        
        self.styles.add(ParagraphStyle(
            name='ScoreText',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

    def generate_essay_report(self, essay_data, judge_evaluation=None):
        buffer = BytesIO()
        # Margins reduced to 0.5 inch to fit more content
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        story = []

        # Title
        story.append(Paragraph("Reporte de Evaluación de Ensayo", self.styles['ReportTitle']))
        
        # Essay Info & Total Score in a single row table
        eval_date = essay_data.get('fecha_evaluacion', datetime.now().isoformat())
        try:
            if isinstance(eval_date, str):
                date_obj = datetime.fromisoformat(eval_date.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
            else:
                formatted_date = eval_date.strftime("%d/%m/%Y %H:%M")
        except:
            formatted_date = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Determine final score
        final_score = essay_data.get('puntuacion_total', 0)
        if judge_evaluation:
            final_score = judge_evaluation.get('puntuacion_total', final_score)
            
        score_color = colors.HexColor('#48bb78') if final_score >= 4 else \
                     colors.HexColor('#ecc94b') if final_score >= 3 else \
                     colors.HexColor('#f56565')

        # Header Table: Info on Left, Score on Right
        header_data = [
            [
                Paragraph(f"<b>Título:</b> {essay_data.get('nombre_archivo', 'N/A')}<br/>"
                          f"<b>Autor:</b> {essay_data.get('autor', 'Desconocido')}<br/>"
                          f"<b>Fecha:</b> {formatted_date}", self.styles['CompactNormal']),
                Paragraph(f"<font color='{score_color}' size=16><b>{final_score:.2f}/5.00</b></font><br/>"
                          f"<font size=8>Puntuación Total</font>", 
                          ParagraphStyle('HeaderScore', parent=self.styles['Normal'], alignment=TA_CENTER))
            ]
        ]
        
        header_table = Table(header_data, colWidths=[5.5*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f7fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0'))
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))

        # Criteria Table
        story.append(Paragraph("Desglose por Criterios", self.styles['SectionHeader']))
        
        criteria_map = [
            ('calidad_tecnica', 'Calidad Técnica (25%)'),
            ('creatividad', 'Creatividad (20%)'),
            ('vinculacion_tematica', 'Vinculación Temática (15%)'),
            ('bienestar_colectivo', 'Bienestar Colectivo (20%)'),
            ('uso_responsable_ia', 'Uso Resp. IA (15%)'),
            ('potencial_impacto', 'Impacto (10%)')
        ]
        
        # Table Header
        table_data = [[
            Paragraph("<b>Criterio</b>", self.styles['CompactBold']),
            Paragraph("<b>Puntaje</b>", self.styles['CompactBold']),
            Paragraph("<b>Comentarios y Observaciones</b>", self.styles['CompactBold'])
        ]]

        for key, title in criteria_map:
            score = 0
            comment = ""
            
            if judge_evaluation:
                puntajes = judge_evaluation.get('puntajes', {})
                comentarios = judge_evaluation.get('comentarios', {})
                short_key_map = {
                    'calidad_tecnica': 'tecnica',
                    'creatividad': 'creatividad',
                    'vinculacion_tematica': 'vinculacion',
                    'bienestar_colectivo': 'bienestar',
                    'uso_responsable_ia': 'uso_ia',
                    'potencial_impacto': 'impacto'
                }
                short_key = short_key_map.get(key)
                score = puntajes.get(short_key, 0)
                comment = comentarios.get(short_key, "")
            else:
                # AI data structure
                # Check if keys are at top level or inside 'evaluacion'
                if key in essay_data:
                    criterion_data = essay_data.get(key, {})
                else:
                    criterion_data = essay_data.get('evaluacion', {}).get(key, {})

                if isinstance(criterion_data, dict):
                    score = criterion_data.get('calificacion', 0)
                    comment = criterion_data.get('comentario', "")
                else:
                    score = 0
                    comment = str(criterion_data)

            table_data.append([
                Paragraph(title, self.styles['CompactNormal']),
                Paragraph(f"{score}/5", self.styles['ScoreText']),
                Paragraph(comment, self.styles['TableText'])
            ])

        # Create Criteria Table
        criteria_table = Table(table_data, colWidths=[1.8*inch, 0.8*inch, 4.9*inch])
        criteria_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#edf2f7')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#2d3748')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(criteria_table)
        story.append(Spacer(1, 10))

        # General Comment
        story.append(Paragraph("Comentarios Generales", self.styles['SectionHeader']))
        general_comment = ""
        if judge_evaluation:
            general_comment = judge_evaluation.get('comentario_general', "")
        else:
            general_comment = essay_data.get('comentario_general', "")
            if not general_comment:
                general_comment = essay_data.get('evaluacion', {}).get('comentario_general', "")
            
        story.append(Paragraph(general_comment, self.styles['TableText']))

        # Footer
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            f"Generado por Essay Agent el {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
            ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=7, textColor=colors.gray, alignment=TA_CENTER)
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer
