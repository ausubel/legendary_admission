# Exam structure 
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
