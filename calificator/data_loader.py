import pandas as pd
from dbfread import DBF

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

def load_student_identifications(identifi_path):
    """
    Load student identification data from IDENTIFI.DBF
    Returns a dictionary mapping student codes to their DNIs
    """
    try:
        # Load the identification data
        identifi_df = load_dbf_to_dataframe(identifi_path)
        
        # Create a dictionary to map student codes to DNIs
        student_ids = {}
        
        for _, row in identifi_df.iterrows():
            student_code = row.get('LITHO', '')
            student_dni = row.get('CODIGO', '')  # Changed from 'DNI' to 'CODIGO'
            
            if student_code and student_dni:
                student_ids[student_code] = student_dni
        
        print(f"Loaded {len(student_ids)} student identifications")
        return student_ids
    except Exception as e:
        print(f"Error loading student identifications from {identifi_path}: {e}")
        return {}

def get_career_path_for_exam_type(exam_type):
    """Get the career path for a given exam type"""
    # Ciencias (A)
    if exam_type in ['M', 'N']:
        return 'A'  # Ciencias
    # Humanidades (B)
    elif exam_type in ['O', 'X']:
        return 'B'  # Humanidades
    # Ingeniería (C)
    elif exam_type in ['Y', 'Z']:
        return 'C'  # Ingeniería
