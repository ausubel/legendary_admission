import os
import pandas as pd

from config import CAREER_PATHS
from data_loader import load_dbf_to_dataframe, extract_answers, load_answer_keys_from_dbf, get_career_path_for_exam_type
from score_calculator import calculate_score
from report_generator import generate_pdf_report, display_results_table

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
        student_answers = extract_answers(row)
        
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
    display_results_table(results_df)

if __name__ == "__main__":
    main()
