# Legendary Admission System

This system handles the generation and grading of admission exams for educational institutions.

## Project Structure

```
legendary_admision/
├── calificator/         # Grading system for exams
│   ├── data/            # Input data (DBF files with answers and responses)
│   ├── output/          # Generated results (CSV and PDF reports)
│   └── main.py          # Main grading script
├── exam_generator/      # Exam generation system
│   ├── data/questions/  # Questions
│   ├── output/          # Generated exams and answer keys
│   └── main.py          # Main exam generation script
└── requirements.txt     # Project dependencies
```

## Features

### Exam Generation
- Generates 9 different exam types (I-Q)
- Each exam includes the institution logo
- Proper formatting and support for Spanish characters

### Exam Grading
- Reads student responses from DBF files
- Compares responses against answer keys
- Calculates scores based on career path weights:
  - **Ciencias (A)**: Emphasizes Natural Sciences
  - **Humanidades (B)**: Emphasizes Humanities
  - **Ingeniería (C)**: Emphasizes Mathematics
- Generates detailed reports in CSV and PDF formats

## Exam Structure

Exams are divided into sections with different weights for each career path:

| Section | Questions | Weight A | Weight B | Weight C |
|---------|-----------|----------|----------|----------|
| Matemática | 1-20 | 2 | 2 | 6 |
| Ciencias Naturales | 21-40 | 6 | 2 | 2 |
| Humanidades | 41-60 | 2 | 6 | 2 |
| Aptitud Académica | 61-100 | 4 | 4 | 4 |

## Usage

### Running the Grading System

```bash
python calificator/main.py
```

This will:
1. Read student responses from `calificator/data/RESPUEST.DBF`
2. Compare with answer keys from `calificator/data/CLAVES.DBF`
3. Generate results in `calificator/output/` directory:
   - `resultados.csv`: Summary of student scores
   - `resultados_detallados.csv`: Detailed results by career path
   - `resultados_[timestamp].pdf`: PDF report with formatted results

## Dependencies

All required dependencies are listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```
