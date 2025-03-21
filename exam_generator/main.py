import os
import pandas as pd
import random
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from config import FILE_MAPPING, EXAM_STRUCTURE, EXAM_TYPES

def load_questions(questions_dir):
    """Load all question files into a dictionary"""
    questions = {}
    for subject, filename in FILE_MAPPING.items():
        file_path = os.path.join(questions_dir, filename)
        if os.path.exists(file_path):
            try:
                # First try to read with headers
                df = pd.read_csv(file_path, encoding='utf-8')
                
                # Check if the expected columns exist
                if 'question' not in df.columns:
                    # If not, try reading without headers and assign column names
                    column_names = ['question', 'alternative_a', 'alternative_b', 'alternative_c', 'alternative_d', 'answer']
                    df = pd.read_csv(file_path, header=None, names=column_names, encoding='utf-8')
                
                questions[subject] = df
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        else:
            print(f"Warning: File {filename} not found")
    return questions

def generate_exam(questions, exam_structure, exam_type, output_dir):
    """Generate an exam based on the given structure"""
    answers = []
    question_number = 1
    
    # Create PDF document
    pdf_file = os.path.join(output_dir, f"exam_type_{exam_type}.pdf")
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = styles["Title"]
    heading_style = styles["Heading1"]
    subheading_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    # Create a list to hold the flowables
    elements = []
    
    # Add exam title
    elements.append(Paragraph(f"EXAMEN TIPO {exam_type}", title_style))
    elements.append(Spacer(1, 12))
    
    # For each main section
    for section_name, subjects in exam_structure.items():
        # Add section heading
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(section_name, heading_style))
        elements.append(Spacer(1, 6))
        
        # For each subject in the section
        for subject, num_questions in subjects.items():
            if subject not in questions:
                print(f"Warning: No questions available for {subject}")
                continue
                
            # Get available questions for this subject
            available_questions = questions[subject]
            if len(available_questions) < num_questions:
                print(f"Warning: Not enough questions for {subject}. Requested {num_questions}, but only {len(available_questions)} available.")
                num_questions = len(available_questions)
            
            # Select random questions
            selected_indices = random.sample(range(len(available_questions)), num_questions)
            selected_questions = available_questions.iloc[selected_indices]
            
            # Add subject subheading
            elements.append(Paragraph(f"--- {subject} ---", subheading_style))
            elements.append(Spacer(1, 6))
            
            # Add questions
            for _, row in selected_questions.iterrows():
                # Question text
                question_text = f"{question_number}. {row['question']}"
                elements.append(Paragraph(question_text, normal_style))
                elements.append(Spacer(1, 6))
                
                # Alternatives
                alternatives = [
                    ListItem(Paragraph(f"A) {row['alternative_a']}", normal_style)),
                    ListItem(Paragraph(f"B) {row['alternative_b']}", normal_style)),
                    ListItem(Paragraph(f"C) {row['alternative_c']}", normal_style)),
                    ListItem(Paragraph(f"D) {row['alternative_d']}", normal_style))
                ]
                elements.append(ListFlowable(alternatives, bulletType='bullet', start=''))
                elements.append(Spacer(1, 12))
                
                # Store answer
                answers.append(str(row['answer']))
                question_number += 1
    
    # Build the PDF
    doc.build(elements)
    
    print(f"Exam Type {exam_type} generated successfully and saved to {pdf_file}")
    return answers

def generate_answer_keys(all_answers, output_dir):
    """Generate answer keys in the requested format"""
    keys_file = os.path.join(output_dir, "keys.txt")
    with open(keys_file, 'w', encoding='utf-8') as f:
        for exam_type, answers in all_answers.items():
            answer_string = exam_type + ''.join(answers)
            f.write(answer_string + '\n')
    
    print(f"Answer keys generated successfully and saved to {keys_file}")

def main():
    # Create output directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the questions directory
    questions_dir = os.path.join(script_dir, "data", "questions")
    
    # Load all questions
    print(f"Loading questions from {questions_dir}...")
    questions = load_questions(questions_dir)
    
    # Generate exams for each type
    all_answers = {}
    for exam_type in EXAM_TYPES:
        print(f"\nGenerating exam type {exam_type}...")
        # Set a different random seed for each exam type to ensure they're different
        random.seed(ord(exam_type))
        answers = generate_exam(questions, EXAM_STRUCTURE, exam_type, output_dir)
        all_answers[exam_type] = answers
    
    # Generate answer keys
    print("\nGenerating answer keys...")
    generate_answer_keys(all_answers, output_dir)
    
    print("\nAll exams and answer keys generated successfully!")

if __name__ == "__main__":
    main()