from config import EXAM_STRUCTURE, CAREER_PATHS

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
    
    # Calculate weighted scores for each career path
    career_scores = {'A': 0, 'B': 0, 'C': 0}
    section_scores = {}
    
    # Process each section separately
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
        
        # Apply the formula for this section: [Nº Respuestas Buenas - 1/4 (Nº Resp. Malas)]
        section_adjusted = correct_count - (0.25 * incorrect_count)
        section_adjusted = max(0, section_adjusted)  # Ensure it's not negative
        
        # Store section counts and adjusted score for reporting
        section_counts[section] = {
            "correct": correct_count,
            "incorrect": incorrect_count,
            "unanswered": unanswered_count,
            "adjusted": section_adjusted,
            "weight": details["weights"][career_path]
        }
        
        # Calculate weighted scores for each career path for this section
        for path in CAREER_PATHS.keys():
            # Get the weight for this section and career path
            weight = EXAM_STRUCTURE[section]["weights"][path]
            
            # Apply the weight to get the section score for this career path
            section_weighted_score = section_adjusted * weight
            
            # Add to the career path total score
            career_scores[path] += section_weighted_score
            
            # Store detailed section score if this is the student's career path
            if path == career_path:
                section_scores[section] = {
                    "correct": correct_count,
                    "incorrect": incorrect_count,
                    "unanswered": unanswered_count,
                    "adjusted": section_adjusted,
                    "weight": weight,
                    "score": section_weighted_score
                }
        
        # Accumulate totals for reporting
        total_correct += correct_count
        total_incorrect += incorrect_count
        total_unanswered += unanswered_count
    
    # Calculate the overall adjusted score (for reporting purposes)
    adjusted_total = total_correct - (0.25 * total_incorrect)
    adjusted_total = max(0, adjusted_total)  # Ensure it's not negative
    
    return career_scores, section_scores, {
        "total_correct": total_correct,
        "total_incorrect": total_incorrect,
        "total_unanswered": total_unanswered,
        "adjusted_total": adjusted_total
    }

def calculate_vigesimal_score(raw_score):
    """
    Convert raw score to vigesimal scale (0-20) using the formula:
    Nota(20) = [20 × (Puntaje Total del Área + 45)] / (360 + 45)
    """
    vigesimal_score = (20 * (raw_score + 45)) / (360 + 45)
    return round(vigesimal_score, 2)  # Round to 2 decimal places
