from langchain_core.output_parsers import PydanticOutputParser
from src.models.question_schemas import MCQQuestion, FillBlankQuestion
from src.prompts.templates import mcq_prompt_template, fill_blank_prompt_template
from src.llm.groq_client import get_groq_llm
from src.common.logger import get_logger
from src.common.custom_exception import CustomException
from src.config.settings import settings


class QuestionGenerator:
    def __init__(self):
        self.llm = get_groq_llm()
        self.logger = get_logger(__name__)
        self.mcq_parser = PydanticOutputParser(pydantic_object=MCQQuestion)
        self.fill_blank_parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)

    def retry_and_parse(
        self, prompt: str, parser: PydanticOutputParser, topic: str, difficulty: str
    ) -> PydanticOutputParser:
        for _ in range(settings.MAX_RETRIES):
            try:
                self.logger.info(
                    f"Generating question for topic: {topic} and difficulty: {difficulty}"
                )
                response = self.llm.invoke(
                    prompt.format(topic=topic, difficulty=difficulty)
                )

                parsed_response = parser.parse(response.content)
                if isinstance(parsed_response, MCQQuestion):
                    if (
                        len(parsed_response.options) == 4
                        and parsed_response.correct_answer in parsed_response.options
                    ):
                        return parsed_response
                    self.logger.error(f"Invalid MCQ response: {parsed_response}")
                elif isinstance(parsed_response, FillBlankQuestion):
                    if "____" in parsed_response.question and parsed_response.answer:
                        return parsed_response
                    self.logger.error(f"Invalid fill-blank response: {parsed_response}")
                else:
                    self.logger.error(f"Unknown schema: {type(parsed_response)}")

            except Exception as e:
                self.logger.error(f"Error generating question: {e}")
                raise CustomException(
                    "Failed to generate question after multiple retries"
                )

    def generate_mcq_question(
        self, topic: str, difficulty: str = "medium"
    ) -> MCQQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)
            question = self.retry_and_parse(
                mcq_prompt_template, parser, topic, difficulty
            )
            print(question.options, "xxxxxxxx>>>>>>>>>>>>>>>>>>>>>question.options")
            if len(question.options) != 4:
                self.logger.error(f"Invalid number of options: {question.options}")
                return None

            if question.correct_answer not in question.options:
                self.logger.error(
                    f"Correct answer not in options: {question.correct_answer}"
                )
                return None

            return question
        except Exception as e:
            self.logger.error(f"Error generating MCQ question: {str(e)}")
            raise CustomException(f"Error generating MCQ question: {str(e)}")

    def generate_fill_blank_question(
        self, topic: str, difficulty: str = "medium"
    ) -> FillBlankQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)
            question = self.retry_and_parse(
                fill_blank_prompt_template, parser, topic, difficulty
            )
            print(question.question, "11111111>>>>>>>>>>>>>>>>>>>>>question")
            if "____" not in question.question:
                self.logger.error(
                    f"Question does not contain ____: {question.question}"
                )
                raise ValueError("Fill in Blank Question does not contain ____")
            if not question.answer:
                self.logger.error(f"Answer is empty: {question.answer}")
                raise ValueError("Fill in Blank Question answer is empty")
            return question
        except Exception as e:
            self.logger.error(f"Error generating fill blank question: {str(e)}")
            raise CustomException(f"Error generating fill blank question: {str(e)}")
