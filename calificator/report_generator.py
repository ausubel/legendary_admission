import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from score_calculator import calculate_vigesimal_score

def generate_pdf_report(results_df, output_path, student_ids=None):
    """Generate a PDF report with the results"""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add title
    elements.append(Paragraph("Resultados de la Evaluación", styles["Title"]))
    elements.append(Spacer(1, 12))
    
    # Add explanation of scoring formula
    elements.append(Paragraph("Fórmula de puntuación:", styles["Heading3"]))
    elements.append(Paragraph("Puntaje = Ponderación × [Nº Respuestas Buenas - 1/4 (Nº Resp. Malas)]", styles["Normal"]))
    elements.append(Spacer(1, 12))
    
    # Add table showing weights
    elements.append(Paragraph("Ponderación por Área Profesional:", styles["Heading3"]))
    weights_data = [
        ["Unidades Académicas", "Preguntas", "A", "B", "C"],
        ["Matemática", "20", "2", "2", "6"],
        ["Ciencias Naturales", "20", "6", "2", "2"],
        ["Humanidades", "20", "2", "6", "2"],
        ["Aptitud Académica", "40", "4", "4", "4"],
        ["TOTAL", "100", "360", "360", "360"]
    ]
    weights_table = Table(weights_data, colWidths=[1.5*inch, 0.8*inch, 0.5*inch, 0.5*inch, 0.5*inch])
    weights_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.royalblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))
    elements.append(weights_table)
    elements.append(Spacer(1, 12))
    
    # Add conversion formula
    elements.append(Paragraph("Fórmula de conversión a escala vigesimal:", styles["Heading3"]))
    elements.append(Paragraph("Nota(20) = [20 × (Puntaje Total del Área + 45)] / (360 + 45)", styles["Normal"]))
    elements.append(Spacer(1, 20))
    
    # Load detailed results to get career recommendations
    detailed_results_path = os.path.join(os.path.dirname(output_path), "resultados_detallados.csv")
    try:
        detailed_df = pd.read_csv(detailed_results_path)
        print(f"Loaded {len(detailed_df)} records from detailed results")
        print(f"Areas postuladas encontradas: {detailed_df['area_postulada'].unique()}")
    except Exception as e:
        print(f"Warning: Could not load detailed results: {e}")
        detailed_df = None
    
    # If we have detailed results, create tables for each career area
    if detailed_df is not None and 'area_postulada' in detailed_df.columns:
        # Group by career area
        for career_name in ['Ciencias', 'Humanidades', 'Ingeniería']:
            # Filter students for this career
            career_students = detailed_df[detailed_df['area_postulada'] == career_name]
            
            if not career_students.empty:
                print(f"Found {len(career_students)} students for {career_name}")
                # Add career section header
                elements.append(Paragraph(f"Resultados para {career_name}", styles["Heading2"]))
                elements.append(Spacer(1, 6))
                
                # Create table data for this career group
                data = [["DNI", "Puntaje", "Nota (20)"]]
                
                # Sort by score in descending order
                career_students = career_students.sort_values(by='puntaje_total', ascending=False)
                
                # Limit to first 50 students per career to avoid memory issues
                for i, (_, row) in enumerate(career_students.iterrows()):
                    if i >= 50:  # Limit to first 50 students per career
                        break
                    
                    # Get student code and DNI
                    student_code = str(row['codigo_estudiante'])
                    student_dni = str(row.get('dni_estudiante', ''))
                    
                    # If DNI is not in the row data but we have student_ids dictionary, try to get it from there
                    if (not student_dni or student_dni == 'nan') and student_ids and student_code in student_ids:
                        student_dni = student_ids[student_code]
                    
                    # If still no DNI, use the student code
                    if not student_dni or student_dni == 'nan':
                        student_dni = student_code
                    
                    # Calculate the vigesimal score
                    vigesimal_score = calculate_vigesimal_score(row['puntaje_total'])
                    data.append([student_dni, str(row['puntaje_total']), str(vigesimal_score)])
                
                # Create table for this career
                table = Table(data, colWidths=[1.5*inch, 1*inch, 1*inch])
                
                # Style the table
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 12))
            else:
                print(f"No students found for {career_name}")
    else:
        # If we don't have detailed results, just show all students together
        elements.append(Paragraph("Resultados por Estudiante", styles["Heading2"]))
        elements.append(Spacer(1, 6))
        
        # Create table data - limit to first 100 students to avoid memory issues
        data = [["DNI", "Puntaje", "Nota (20)"]]
        for i, (_, row) in enumerate(results_df.iterrows()):
            if i >= 100:  # Limit to first 100 students
                break
            
            # Get student code and DNI
            student_code = str(row['codigo_estudiante'])
            student_dni = str(row.get('dni_estudiante', ''))
            
            # If DNI is not in the row data but we have student_ids dictionary, try to get it from there
            if (not student_dni or student_dni == 'nan') and student_ids and student_code in student_ids:
                student_dni = student_ids[student_code]
            
            # If still no DNI, use the student code
            if not student_dni or student_dni == 'nan':
                student_dni = student_code
            
            # Calculate the vigesimal score
            vigesimal_score = calculate_vigesimal_score(row['puntajes_correctos'])
            data.append([student_dni, str(row['puntajes_correctos']), str(vigesimal_score)])
        
        # Create table
        table = Table(data, colWidths=[1.5*inch, 1*inch, 1*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
    
    # Add footer
    elements.append(Spacer(1, 20))
    current_time = pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')
    elements.append(Paragraph(f"Generado el {current_time}", styles["Normal"]))
    
    # Build the PDF
    try:
        doc.build(elements)
        print(f"PDF report successfully generated at {output_path}")
    except Exception as e:
        print(f"Error generating PDF report: {e}")

def display_results_table(results_df):
    """Display the results in a formatted table"""
    if results_df is not None and not results_df.empty:
        print("\nResultados Finales:")
        print("+" + "-" * 30 + "+" + "-" * 30 + "+" + "-" * 20 + "+")
        print("|" + "codigo_estudiante".center(30) + "|" + "dni_estudiante".center(30) + "|" + "puntajes_correctos".center(20) + "|")
        print("+" + "-" * 30 + "+" + "-" * 30 + "+" + "-" * 20 + "+")
        
        for _, row in results_df.iterrows():
            print("|" + str(row['codigo_estudiante']).center(30) + "|" + str(row['dni_estudiante']).center(30) + "|" + str(row['puntajes_correctos']).center(20) + "|")
        
        print("+" + "-" * 30 + "+" + "-" * 30 + "+" + "-" * 20 + "+")
