import sqlite3
import json

# --- Configuration ---
DATABASE_FILE = 'quiz.db'

# --- The initial set of questions ---
# This data is the same as our old questions.json file
questions_data = [
    {
        "id": 1, "category": "Numerical Ability", "question": "The average of first 50 natural numbers is ?",
        "options": {"A": "25.30", "B": "25.5", "C": "25.00", "D": "12.25"}, "answer": "B"
    },
    {
        "id": 2, "category": "Numerical Ability", "question": "A fraction which bears the same ratio to 1/27 as 3/11 bear to 5/9 is equal to ?",
        "options": {"A": "1/55", "B": "55", "C": "3/11", "D": "1/27"}, "answer": "A"
    },
    {
        "id": 3, "category": "Reasoning Ability", "question": "Look at this series: 7, 10, 8, 11, 9, 12, ... What number should come next?",
        "options": {"A": "7", "B": "10", "C": "12", "D": "13"}, "answer": "B"
    },
    {
        "id": 4, "category": "Verbal Ability", "question": "Select the word which is the exact OPPOSITE of the word 'RELINQUISH'.",
        "options": {"A": "Abdicate", "B": "Renounce", "C": "Possess", "D": "Deny"}, "answer": "C"
    },
    {
        "id": 5, "category": "Verbal Ability", "question": "Find the correctly spelt word.",
        "options": {"A": "Ommineous", "B": "Ominous", "C": "Omenus", "D": "Omineous"}, "answer": "B"
    },
    {
        "id": 6, "category": "Numerical Ability", "question": "A clock is started at noon. By 10 minutes past 5, the hour hand has turned through:",
        "options": {"A": "145°", "B": "150°", "C": "155°", "D": "160°"}, "answer": "C"
    },
    {
        "id": 7, "category": "Reasoning Ability", "question": "In a certain code, 'TRIPPLE' is written as 'SQHOOKD'. How is 'DISPOSE' written in that code?",
        "options": {"A": "CHRONRD", "B": "ESJTPTF", "C": "ESOPSID", "D": "ESOJOV"}, "answer": "A"
    },
    {
        "id": 8, "category": "Verbal Ability", "question": "The students _______ their dialogues.",
        "options": {"A": "rehearsed", "B": "repeated", "C": "recited", "D": "replayed"}, "answer": "A"
    },
    {
        "id": 9, "category": "Numerical Ability", "question": "What is the value of (2.3³ - 0.027) / (2.3² + 0.69 + 0.09)?",
        "options": {"A": "2", "B": "2.273", "C": "2.33", "D": "2.6"}, "answer": "A"
    },
    {
        "id": 10, "category": "Reasoning Ability", "question": "If 'P' denotes 'multiplied by', 'T' denotes 'subtracted from', 'M' denotes 'added to' and 'B' denotes 'divided by', then 28 B 7 P 8 T 6 M 4 = ?",
        "options": {"A": "30", "B": "31", "C": "32", "D": "34"}, "answer": "A"
    },
    {
        "id": 11, "category": "Verbal Ability", "question": "Choose the word that best expresses the meaning of 'Candid'.",
        "options": {"A": "Biased", "B": "Frank", "C": "Devious", "D": "Secretive"}, "answer": "B"
    },
    {
        "id": 12, "category": "Numerical Ability", "question": "A vendor bought toffees at 6 for a rupee. How many for a rupee must he sell to gain 20%?",
        "options": {"A": "3", "B": "4", "C": "5", "D": "Cannot be determined"}, "answer": "C"
    },
    {
        "id": 13, "category": "Reasoning Ability", "question": "Arrange the words given below in a meaningful sequence: 1. Key 2. Door 3. Lock 4. Room 5. Switch on",
        "options": {"A": "5, 1, 2, 4, 3", "B": "4, 2, 1, 5, 3", "C": "1, 3, 2, 4, 5", "D": "1, 2, 3, 5, 4"}, "answer": "C"
    },
    {
        "id": 14, "category": "Verbal Ability", "question": "He is very good _______ making stories.",
        "options": {"A": "in", "B": "at", "C": "about", "D": "for"}, "answer": "B"
    },
    {
        "id": 15, "category": "Numerical Ability", "question": "The sum of ages of 5 children born at the intervals of 3 years each is 50 years. What is the age of the youngest child?",
        "options": {"A": "4 years", "B": "8 years", "C": "10 years", "D": "None of these"}, "answer": "A"
    }
]

def setup_database():
    """Create the database and table, then populate it with questions."""
    try:
        # Connect to the database (this will create the file if it doesn't exist)
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Create the 'questions' table
        # We store 'options' as a JSON string (TEXT) for flexibility
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        ''')

        # Insert each question into the table
        for q in questions_data:
            # We must convert the options dictionary to a JSON string to store it
            options_str = json.dumps(q['options'])
            
            # if the script is executed multiple times
            cursor.execute('''
                INSERT OR IGNORE INTO questions (id, category, question, options, answer)
                VALUES (?, ?, ?, ?, ?)
            ''', (q['id'], q['category'], q['question'], options_str, q['answer']))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        
        print(f"Database '{DATABASE_FILE}' setup complete.")
        print(f"{len(questions_data)} questions have been loaded.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    setup_database()
