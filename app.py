import streamlit as st
import os
from dotenv import load_dotenv
from src.utils.helpers import QuizManager, rerun
from src.generator.question_generator import QuestionGenerator

from src.common.logger import get_logger


load_dotenv()

logger = get_logger(__name__)


def main():
    st.set_page_config(page_title="Study Buddy AI", page_icon=":book:", layout="wide")

    if "quiz_manager" not in st.session_state:
        st.session_state.quiz_manager = QuizManager()

    if "topic" not in st.session_state:
        st.session_state.topic = "math"

    if "question_type" not in st.session_state:
        st.session_state.question_type = "mcq"

    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "medium"
    if "quiz_generated" not in st.session_state:
        st.session_state.quiz_generated = False
    if "quiz_attempted" not in st.session_state:
        st.session_state.quiz_attempted = False
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "rerun_trigger" not in st.session_state:
        st.session_state.rerun_trigger = False

    st.title("Study Buddy AI Agent")
    st.sidebar.title("Quiz Settings")

    question_type = st.sidebar.selectbox(
        "Select the type of question",
        ["MCQ", "Fill in the Blank"],
        index=0,
        key="question_type_selectbox",
    )
    topic = st.sidebar.text_input(
        "Enter the topic for the quiz", value=st.session_state.topic
    )
    difficulty = st.sidebar.selectbox(
        "Select the difficulty level",
        ["Easy", "Medium", "Hard"],
        index=1,
        key="difficulty_selectbox",
    )
    num_questions = st.sidebar.number_input(
        "Enter the number of questions",
        value=10,
        min_value=1,
        max_value=20,
        step=1,
        key="num_questions_input",
    )

    if st.sidebar.button("Generate Quiz", key="generate_button"):
        st.session_state.quiz_submitted = False
        generator = QuestionGenerator()
        success = st.session_state.quiz_manager.generate_questions(
            generator, topic, question_type, difficulty, num_questions
        )
        st.session_state.quiz_generated = success
        rerun()
    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        st.markdown("## Quiz Questions")
        st.session_state.quiz_manager.attempt_quiz()
        if st.button("Submit Quiz", key="submit_button"):
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            rerun()
    if st.session_state.quiz_submitted and st.session_state.quiz_manager.results:
        st.markdown("## Quiz Results")
        df_results = st.session_state.quiz_manager.generate_results_dataframe()
        if not df_results.empty:
            correct_answers = df_results[df_results["is_correct"] == True][
                "question_number"
            ].count()
            correct_count = df_results["is_correct"].sum()
            total_questions = len(df_results)
            score_percentage = (correct_count / total_questions) * 100
            st.write(f"Socre: {score_percentage:.2f}%")

            for _, result in df_results.iterrows():
                question_number = result.question_number

                if result["is_correct"]:
                    st.success(
                        f"Question {question_number}: {result['question']} - Correct Answer: {result['correct_answer']}"
                    )
                else:
                    st.error(f"Question {question_number}: {result['question']}")
                    st.write(f"Your Answer: {result['user_answer']}")
                    st.write(f"Correct Answer: {result['correct_answer']}")

            st.markdown("--------------------------------")

            if st.button("Save Results", key="save_results_button"):
                filename = st.text_input(
                    "Enter the filename to save the results", value="quiz_results"
                )
                if filename:
                    saved_file = st.session_state.quiz_manager.save_to_csv(filename)
                    if saved_file:
                        with open(saved_file, "r") as file:
                            st.download_button(
                                f"Download {filename}",
                                file_name=os.path.basename(saved_file),
                                mime="text/csv",
                                data=file.read(),
                                key=f"download_button_{filename}",
                            )
                    else:
                        st.warning("No results to save!")
                else:
                    st.error("Please enter a filename to save the results")


if __name__ == "__main__":
    main()
