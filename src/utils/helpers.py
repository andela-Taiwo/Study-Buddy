import os
import streamlit as st
import pandas as pd
from src.generator.question_generator import QuestionGenerator
from src.models.question_schemas import MCQQuestion, FillBlankQuestion
from src.common.logger import get_logger
from src.common.custom_exception import CustomException
from src.config.settings import settings

logger = get_logger(__name__)


def rerun():
    st.session_state["rerun_trigger"] = not st.session_state.get("rerun_trigger", False)


class QuizManager:
    def __init__(self):
        self.question_generator = QuestionGenerator()
        self.questions = []
        self.current_question = 0
        self.results = []
        self.user_answers = []
        self.score = 0
        self.total_questions = 0
        self.correct_answers = 0
        self.incorrect_answers = 0

    def generate_questions(
        self,
        generator: QuestionGenerator,
        topic: str,
        question_type: str,
        difficulty: str = "medium",
        num_questions: int = 10,
    ) -> bool:
        self.questions = []
        try:
            for _ in range(num_questions):
                if question_type.lower() == "mcq":
                    print("in mcq")
                    question = generator.generate_mcq_question(
                        topic, difficulty.lower()
                    )
                    print(question.question, ">>>>>>>>>>>>>>>>>>>>>question")
                    self.questions.append(
                        {
                            "type": "MCQ",
                            "question": question.question,
                            "options": question.options,
                            "correct_answer": question.correct_answer,
                        }
                    )
                elif question_type.lower() == "fill in the blank":
                    print("in fill in the blank")
                    question = generator.generate_fill_blank_question(
                        topic, difficulty.lower()
                    )
                    self.questions.append(
                        {
                            "type": "Fill in the Blank",
                            "question": question.question,
                            "correct_answer": question.answer,
                        }
                    )
                else:
                    raise ValueError(f"Invalid question type: {question_type}")
            return True
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return False

    def attempt_quiz(self) -> None:
        try:
            for i, q in enumerate(self.questions):
                st.markdown(f"**Question {i + 1}:** {q['question']}")
                self.user_answers = self.user_answers or [None] * len(self.questions)
                if q["type"] == "MCQ":
                    user_answer = st.selectbox(
                        f"Select your answer for Question {i + 1}",
                        q["options"],
                        index=None,
                        key=f"mcq_answer_{i}",
                    )
                else:
                    user_answer = st.text_input(
                        f"Answer the question for Question {i + 1}",
                        key=f"fill_blank_answer_{i}",
                    )
                if user_answer is not None and user_answer != "":
                    self.user_answers[i] = user_answer

        except Exception as e:
            logger.error(f"Error attempting quiz: {str(e)}")
            raise CustomException(f"Error attempting quiz: {str(e)}")

    def evaluate_quiz(self) -> None:
        self.results = []
        print(self.user_answers, "user_answers")
        print(len(self.questions), "results")
        print(len(self.user_answers), "user_answers")
        for i, (q, user_answer) in enumerate(zip(self.questions, self.user_answers)):
            print(user_answer, "user_answer", q["correct_answer"])
            result_dict = {
                "question_number": i + 1,
                "question": q["question"],
                "question_type": q["type"],
                "user_answer": user_answer,
                "correct_answer": q["correct_answer"],
                "is_correct": user_answer == q["correct_answer"],
            }
            if q["type"] == "MCQ":
                result_dict["options"] = q["options"]
                result_dict["is_correct"] = user_answer == q["correct_answer"]
            elif q["type"] == "Fill in the Blank":
                result_dict["options"] = []
                result_dict["is_correct"] = user_answer == q["correct_answer"]
            self.results.append(result_dict)

    def generate_results_dataframe(self) -> pd.DataFrame:
        if not self.results:
            return pd.DataFrame()
        return pd.DataFrame(self.results)

    def save_to_csv(self, filename: str = "quiz_results") -> None:
        if not self.results:
            st.warning("No results to save!")
            return

        df = self.generate_results_dataframe()

        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{filename}_{timestamp}.csv"
        os.makedirs("results", exist_ok=True)
        full_path = os.path.join("results", unique_filename)
        try:
            df.to_csv(full_path, index=False)
            st.success(f"Results saved to {full_path}")
            return full_path
        except Exception as e:
            logger.error(f"Error saving results to CSV: {str(e)}")
            raise CustomException(f"Error saving results to CSV: {str(e)}")

    def display_results(self) -> None:
        if not self.results:
            st.warning("No results to display!")
            return
        st.markdown("## Quiz Results")
        st.markdown(f"**Total Questions:** {len(self.questions)}")
        st.markdown(f"**Correct Answers:** {self.correct_answers}")
