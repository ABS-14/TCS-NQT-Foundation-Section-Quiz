import streamlit as st
import json
import random
import sqlite3
import time

# --- Configuration and Constants ---
DATABASE_FILE = 'quiz.db'
NUM_QUESTIONS_PER_QUIZ = 10
# Set the duration for the quiz in minutes
QUIZ_DURATION_MINUTES = 10
QUIZ_DURATION_SECONDS = QUIZ_DURATION_MINUTES * 60

# --- Helper Functions ---

def load_questions_from_db():
    """
    Loads all questions from the SQLite database.
    Returns a list of questions or None if an error occurs.
    """
    try:
        # check_same_thread=False is required for Streamlit's threading model
        conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, question, options, answer FROM questions")
        rows = cursor.fetchall()
        conn.close()

        questions = []
        for row in rows:
            questions.append({
                "id": row[0],
                "category": row[1],
                "question": row[2],
                "options": json.loads(row[3]),
                "answer": row[4]
            })
        return questions

    except sqlite3.OperationalError:
        st.error(f"FATAL ERROR: Database file '{DATABASE_FILE}' not found.")
        st.info("Please run the `setup_database.py` script first to create and populate the database.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def calculate_score(user_answers, session_questions):
    """Calculate the user's score."""
    score = 0
    for i, q in enumerate(session_questions):
        user_ans = user_answers.get(i)
        if user_ans and user_ans == q['answer']:
            score += 1
    return score

# --- Main Application Logic ---

def main():
    """Main function to run the Streamlit app."""
    st.title("TCS NQT Foundation Section Quiz Simulator")

    all_questions = load_questions_from_db()
    if all_questions is None:
        return

    # --- Session State Initialization ---
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.quiz_finished = False
        st.session_state.current_q_index = 0
        st.session_state.user_answers = {}
        st.session_state.score = 0
        st.session_state.session_questions = []
        st.session_state.end_time = 0
        st.session_state.time_up = False

    # --- UI Rendering ---
    
    # Start Screen
    if not st.session_state.quiz_started:
        st.header("Welcome to the Quiz!")
        st.write(f"You will be presented with **{NUM_QUESTIONS_PER_QUIZ}** random questions.")
        st.write(f"You will have **{QUIZ_DURATION_MINUTES} minutes** to complete the test.")
        
        if st.button("Start Quiz"):
            st.session_state.session_questions = random.sample(all_questions, min(NUM_QUESTIONS_PER_QUIZ, len(all_questions)))
            st.session_state.end_time = time.time() + QUIZ_DURATION_SECONDS
            st.session_state.quiz_started = True
            st.session_state.quiz_finished = False
            st.session_state.current_q_index = 0
            st.session_state.user_answers = {}
            st.session_state.score = 0
            st.session_state.time_up = False
            st.rerun()

    # Quiz Interface
    elif not st.session_state.quiz_finished:
        # --- Timer Logic ---
        remaining_time = st.session_state.end_time - time.time()

        if remaining_time <= 0:
            st.session_state.quiz_finished = True
            st.session_state.time_up = True
            st.rerun() # Rerun immediately to go to the results page

        mins, secs = divmod(int(remaining_time), 60)
        timer_display = f"{mins:02d}:{secs:02d}"
        
        # Display the timer in a prominent way
        st.metric("Time Remaining", timer_display)
        st.markdown("---")

        # --- Question Display ---
        progress_text = f"Question {st.session_state.current_q_index + 1} of {len(st.session_state.session_questions)}"
        st.subheader(progress_text)
        st.progress((st.session_state.current_q_index + 1) / len(st.session_state.session_questions))
        
        q = st.session_state.session_questions[st.session_state.current_q_index]
        st.markdown(f"**Category:** `{q['category']}`")
        st.write(f"### {q['question']}")

        options = list(q['options'].values())
        user_choice = st.radio("Choose your answer:", options, key=f"q_{st.session_state.current_q_index}", index=None)

        if user_choice:
            for key, value in q['options'].items():
                if value == user_choice:
                    st.session_state.user_answers[st.session_state.current_q_index] = key
                    break

        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.current_q_index > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.current_q_index -= 1
                    st.rerun()
        with col2:
            if st.session_state.current_q_index < len(st.session_state.session_questions) - 1:
                if st.button("Next ➡️"):
                    st.session_state.current_q_index += 1
                    st.rerun()
            else:
                if st.button("Finish Quiz 🏁"):
                    st.session_state.quiz_finished = True
                    st.session_state.score = calculate_score(st.session_state.user_answers, st.session_state.session_questions)
                    st.rerun()

    # Results Screen
    else:
        if st.session_state.get('time_up', False):
            st.error("Time's up! The quiz has ended automatically.")
        
        st.header("🎉 Quiz Finished! 🎉")
        
        score = calculate_score(st.session_state.user_answers, st.session_state.session_questions)
        total_questions = len(st.session_state.session_questions)
        score_percent = (score / total_questions) * 100 if total_questions > 0 else 0
        
        st.subheader(f"Your Final Score: {score} / {total_questions} ({score_percent:.2f}%)")

        if score_percent >= 75: st.success("Excellent work!")
        elif score_percent >= 50: st.warning("Good effort!")
        else: st.error("Keep practicing! Review the answers below.")

        st.markdown("---")
        st.subheader("Review Your Answers")

        for i, q in enumerate(st.session_state.session_questions):
            user_ans_key = st.session_state.user_answers.get(i)
            user_ans_text = q['options'].get(user_ans_key, "Not Answered")
            correct_ans_text = q['options'][q['answer']]
            
            is_correct = user_ans_key == q['answer']
            icon = "✅" if is_correct else "❌"
            
            with st.expander(f"{icon} Question {i+1}: {q['question']}"):
                st.write(f"**Your Answer:** {user_ans_text}")
                if not is_correct:
                    st.write(f"**Correct Answer:** {correct_ans_text}")

        if st.button("Restart Quiz"):
            # Reset all relevant session state variables
            for key in list(st.session_state.keys()):
                if key != 'questions': # Don't reload questions
                    del st.session_state[key]
            st.rerun()

    # --- Auto-rerun for live timer ---
    if st.session_state.get('quiz_started', False) and not st.session_state.get('quiz_finished', True):
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    main()