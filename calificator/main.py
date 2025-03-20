import os
import pandas as pd
from dbfread import DBF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

# Define the structure of the exam based on the images
EXAM_STRUCTURE = {
    "Matemática": {
        "start": 0,  # 0-indexed (corresponds to PREG_001 to PREG_020)
        "end": 19,
        "weights": {"A": 2, "B": 2, "C": 6}
    },
    "Ciencias Naturales": {
        "start": 20,  # 0-indexed (corresponds to PREG_021 to PREG_040)
        "end": 39,
        "weights": {"A": 6, "B": 2, "C": 2}
    },
    "Humanidades": {
        "start": 40,  # 0-indexed (corresponds to PREG_041 to PREG_060)
        "end": 59,
        "weights": {"A": 2, "B": 6, "C": 2}
    },
    "Aptitud Académica": {
        "start": 60,  # 0-indexed (corresponds to PREG_061 to PREG_100)
        "end": 99,
        "weights": {"A": 4, "B": 4, "C": 4}
    }
}

# Career paths
CAREER_PATHS = {
    "A": "Ciencias",  # Science
    "B": "Humanidades",  # Humanities
    "C": "Ingeniería"  # Engineering
}

def load_dbf_to_dataframe(file_path):
    """Load a DBF file into a pandas DataFrame"""
    try:
        # Read the DBF file
        dbf = DBF(file_path, encoding='latin-1')
        df = pd.DataFrame(list(dbf))
        return df
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def extract_answers(row):
    """Extract answers from a row (PREG_001 to PREG_100)"""
    answers = []
    for i in range(1, 101):
        field_name = f'PREG_{i:03d}'
        if field_name in row and row[field_name] is not None and row[field_name] != '':
            answers.append(row[field_name])
        else:
            answers.append('')  # Empty if missing
    return answers

def calculate_score(student_answers, correct_answers, career_path):
    """
    Calculate the score for a student based on their answers and the correct answers,
    using the formula: Puntaje = Ponderación × [Nº Respuestas Buenas - 1/4 (Nº Resp. Malas)]
    """
    # Count correct and incorrect answers for the entire exam
    total_correct = 0
    total_incorrect = 0
    total_unanswered = 0
    section_counts = {}
    
    # Count correct and incorrect answers for each section
    for section, details in EXAM_STRUCTURE.items():
        start_idx = details["start"]
        end_idx = details["end"]
        
        # Calculate the number of correct and incorrect answers in this section
        correct_count = 0
        incorrect_count = 0
        unanswered_count = 0
        
        for i in range(start_idx, end_idx + 1):
            if i < len(student_answers) and i < len(correct_answers):
                # Skip unanswered questions
                if student_answers[i] == '':
                    unanswered_count += 1
                # Count correct answers
                elif correct_answers[i] != '' and student_answers[i] == correct_answers[i]:
                    correct_count += 1
                # Count incorrect answers (only if the student provided an answer)
                elif student_answers[i] != '':
                    incorrect_count += 1
        
        # Store section counts for reporting
        section_counts[section] = {
            "correct": correct_count,
            "incorrect": incorrect_count,
            "unanswered": unanswered_count,
            "weight": details["weights"][career_path]
        }
        
        # Accumulate totals
        total_correct += correct_count
        total_incorrect += incorrect_count
        total_unanswered += unanswered_count
    
    # Calculate the adjusted score using the formula for the entire exam
    # Formula: [Nº Respuestas Buenas - 1/4 (Nº Resp. Malas)]
    adjusted_total = total_correct - (0.25 * total_incorrect)
    adjusted_total = max(0, adjusted_total)  # Ensure it's not negative
    
    # Calculate weighted scores for each career path
    career_scores = {}
    section_scores = {}
    
    for path in CAREER_PATHS.keys():
        path_score = 0
        
        # Calculate section scores for this career path
        for section, counts in section_counts.items():
            # Get the weight for this section and career path
            weight = EXAM_STRUCTURE[section]["weights"][path]
            
            # Apply the formula to the entire exam's adjusted score, then weight by section
            section_proportion = counts["correct"] / total_correct if total_correct > 0 else 0
            section_adjusted = adjusted_total * section_proportion
            section_score = section_adjusted * weight
            
            # Add to the path score
            path_score += section_score
            
            # Store section score if this is the student's career path
            if path == career_path:
                section_scores[section] = {
                    "correct": counts["correct"],
                    "incorrect": counts["incorrect"],
                    "unanswered": counts["unanswered"],
                    "weight": weight,
                    "score": section_score
                }
        
        # Store the career path score
        career_scores[path] = path_score
    
    return career_scores, section_scores, {
        "total_correct": total_correct,
        "total_incorrect": total_incorrect,
        "total_unanswered": total_unanswered,
        "adjusted_total": adjusted_total
    }

def load_answer_keys_from_dbf(claves_path):
    """Load answer keys from the CLAVES.DBF file"""
    try:
        # Load the answer keys from the CLAVES.DBF file
        claves_df = load_dbf_to_dataframe(claves_path)
        
        # Create a dictionary to store the answer keys
        answer_keys = {}
        
        for _, row in claves_df.iterrows():
            exam_type = row.get('TEMA', '')
            if exam_type:
                # Extract answers from the row
                answers = []
                for i in range(1, 101):
                    field_name = f'PREG_{i:03d}'
                    if field_name in row and row[field_name]:
                        answers.append(row[field_name])
                    else:
                        answers.append('')
                
                answer_keys[exam_type] = answers
        
        return answer_keys
    except Exception as e:
        print(f"Error loading answer keys from {claves_path}: {e}")
        return {}

def get_career_path_for_exam_type(exam_type):
    """Get the career path for a given exam type"""
    # Ciencias (A)
    if exam_type in ['M', 'N']:
        return 'A'  # Ciencias
    # Humanidades (B)
    elif exam_type in ['O', 'X', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
        return 'B'  # Humanidades
    # Ingeniería (C)
    elif exam_type in ['Y', 'Z']:
        return 'C'  # Ingeniería
    else:
        # Default to a balanced approach if exam type is unknown
        print(f"Warning: Unknown exam type '{exam_type}', defaulting to 'B' (Humanidades)")
        return 'B'

def grade_exams(respuestas_path, claves_path, output_path):
    """Grade the exams and save the results"""
    # Load the student responses
    respuestas_df = load_dbf_to_dataframe(respuestas_path)
    
    # Load the answer keys from CLAVES.DBF
    answer_keys = load_answer_keys_from_dbf(claves_path)
    
    # Create lists to store the results
    results = []
    detailed_results = []
    
    # Process each student's responses
    for idx, row in respuestas_df.iterrows():
        # Get the student code (LITHO field) or generate one if not present
        student_code = row.get('LITHO', f"{idx + 1:06d}")
        
        # Get the exam type
        exam_type = row.get('TEMA', '')
        
        # Extract student answers
        student_answers = []
        for i in range(1, 101):
            field_name = f'PREG_{i:03d}'
            if field_name in row and row[field_name]:
                student_answers.append(row[field_name])
            else:
                student_answers.append('')
        
        # Get the correct answers for this exam type
        correct_answers = answer_keys.get(exam_type, [])
        
        # Determine the career path based on exam type
        career_path = get_career_path_for_exam_type(exam_type)
        
        # Calculate scores for each career path
        career_scores, section_scores, totals = calculate_score(student_answers, correct_answers, career_path)
        
        # Find career based on the career_path
        best_career = career_scores.get(career_path, 0)
        
        # Add to results
        results.append({
            'codigo_estudiante': student_code,
            'puntajes_correctos': best_career
        })
        
        # Add to detailed results
        if correct_answers:
            detailed_results.append({
                'codigo_estudiante': student_code,
                'tipo_examen': exam_type,
                'carrera_asignada': career_path,
                'puntaje_matematica': section_scores['Matemática']['score'],
                'puntaje_ciencias': section_scores['Ciencias Naturales']['score'],
                'puntaje_humanidades': section_scores['Humanidades']['score'],
                'puntaje_aptitud': section_scores['Aptitud Académica']['score'],
                'puntaje_ciencias_carrera': career_scores['A'],
                'puntaje_humanidades_carrera': career_scores['B'],
                'puntaje_ingenieria_carrera': career_scores['C'],
                'area_postulada': CAREER_PATHS[career_path],
                'puntaje_total': best_career
            })
        else:
            print(f"Warning: No answer key found for exam type {exam_type}")
    
    # Create DataFrames with the results
    results_df = pd.DataFrame(results)
    detailed_results_df = pd.DataFrame(detailed_results)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the results to CSV files
    results_df.to_csv(output_path, index=False)
    detailed_path = os.path.join(os.path.dirname(output_path), "resultados_detallados.csv")
    detailed_results_df.to_csv(detailed_path, index=False)
    
    # Generate PDF report with logo - use a timestamp in the filename to avoid permission issues
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    pdf_path = os.path.join(os.path.dirname(output_path), f"resultados_{timestamp}.pdf")
    generate_pdf_report(results_df, pdf_path)
    
    print(f"Results saved to {output_path}")
    print(f"Detailed results saved to {detailed_path}")
    print(f"PDF report saved to {pdf_path}")
    
    # Display the results
    print("\nResults:")
    print(results_df)
    
    return results_df

def generate_pdf_report(results_df, output_path):
    """Generate a PDF report with the results"""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib.units import inch
    
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
                data = [["Estudiante", "Puntaje", "Nota (20)"]]
                
                # Sort by score in descending order
                career_students = career_students.sort_values(by='puntaje_total', ascending=False)
                
                # Limit to first 50 students per career to avoid memory issues
                for i, (_, row) in enumerate(career_students.iterrows()):
                    if i >= 50:  # Limit to first 50 students per career
                        break
                    # Calculate the vigesimal score
                    vigesimal_score = (20 * (row['puntaje_total'] + 45)) / (360 + 45)
                    vigesimal_score = round(vigesimal_score, 2)  # Round to 2 decimal places
                    data.append([str(row['codigo_estudiante']), str(row['puntaje_total']), str(vigesimal_score)])
                
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
        data = [["Estudiante", "Puntaje", "Nota (20)"]]
        for i, (_, row) in enumerate(results_df.iterrows()):
            if i >= 100:  # Limit to first 100 students
                break
            # Calculate the vigesimal score
            vigesimal_score = (20 * (row['puntajes_correctos'] + 45)) / (360 + 45)
            vigesimal_score = round(vigesimal_score, 2)  # Round to 2 decimal places
            data.append([str(row['codigo_estudiante']), str(row['puntajes_correctos']), str(vigesimal_score)])
        
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

def main():
    # Define file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    claves_path = os.path.join(script_dir, "data", "CLAVES.DBF")
    respuestas_path = os.path.join(script_dir, "data", "RESPUEST.DBF")
    output_path = os.path.join(script_dir, "output", "resultados.csv")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Grade the exams
    results_df = grade_exams(respuestas_path, claves_path, output_path)
    
    # Display the results in the requested format
    if results_df is not None and not results_df.empty:
        print("\nResultados Finales:")
        print("+" + "-" * 30 + "+" + "-" * 20 + "+")
        print("|" + "codigo_estudiante".center(30) + "|" + "puntajes_correctos".center(20) + "|")
        print("+" + "-" * 30 + "+" + "-" * 20 + "+")
        
        for _, row in results_df.iterrows():
            print("|" + str(row['codigo_estudiante']).center(30) + "|" + str(row['puntajes_correctos']).center(20) + "|")
        
        print("+" + "-" * 30 + "+" + "-" * 20 + "+")

if __name__ == "__main__":
    main()
