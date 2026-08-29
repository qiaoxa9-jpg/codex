from .answer_generator import AnswerGenerator
from .schemas import AnswerMode, AnswerSection, Classification, Evidence, UILanguage


class EngineeringAgent:
    def __init__(self, generator: AnswerGenerator):
        self.generator = generator

    async def run(
        self,
        question: str,
        classification: Classification,
        evidences: list[Evidence],
        language: UILanguage = UILanguage.ZH,
    ) -> tuple[list[AnswerSection], str, list[str]]:
        return await self.generator.generate(
            question, AnswerMode.ENGINEERING, classification, evidences, language
        )
