from pydantic import BaseModel
from typing import Optional


class QAQuestion(BaseModel):
    key: str
    text: str
    options: list[str] = []
    type: str = "choice"


class QAState(BaseModel):
    current_question_index: int = 0
    answers: dict[str, str] = {}
    is_complete: bool = False
    skipped_keys: list[str] = []


class QAEngine:
    def __init__(self):
        self.questions: list[QAQuestion] = [
            QAQuestion(key="audience", text="Who is your target audience for this presentation?",
                options=["Business executives", "Technical team", "Students/Academia", "General public", "Investors/Stakeholders"], type="choice"),
            QAQuestion(key="goal", text="What's the primary goal of this presentation?",
                options=["Inform/Educate", "Persuade/Convince", "Teach/Train", "Pitch/Sell", "Report/Update"], type="choice"),
            QAQuestion(key="tone", text="What tone should the presentation have?",
                options=["Formal & Professional", "Casual & Conversational", "Inspirational & Motivating", "Technical & Detailed", "Storytelling & Narrative"], type="choice"),
            QAQuestion(key="slide_count", text="How many slides do you want?",
                options=["5-10 (Quick overview)", "10-20 (Standard)", "20-30 (Detailed)", "30+ (Comprehensive)", "Let AI decide"], type="choice"),
            QAQuestion(key="key_message", text="What is the single most important message your audience should remember?", type="freetext"),
            QAQuestion(key="visual_style", text="What visual style do you prefer?",
                options=["Minimal & Clean", "Data-Heavy & Analytical", "Storytelling with Images", "Dark & Modern", "Corporate & Professional", "Vibrant & Creative"], type="choice"),
            QAQuestion(key="must_include", text="Are there any specific points, data, quotes, or sections that MUST be included?", type="freetext"),
            QAQuestion(key="time_limit", text="How long is the presentation?",
                options=["5 minutes", "10 minutes", "15 minutes", "20 minutes", "30 minutes", "45+ minutes", "No time limit"], type="choice"),
            QAQuestion(key="sections", text="What main sections or topics should the presentation cover? (List them in order)", type="freetext"),
            QAQuestion(key="data_viz", text="Do you need charts, graphs, or data visualizations?",
                options=["Yes, lots of data viz", "A few key charts", "Minimal — mostly text and images", "None needed"], type="choice"),
            QAQuestion(key="speaker_notes", text="Do you want detailed speaker notes for each slide?",
                options=["Yes, detailed notes", "Brief bullet points", "No speaker notes"], type="choice"),
            QAQuestion(key="call_to_action", text="What should the audience do after this presentation?", type="freetext"),
        ]

    def get_current_question(self, state: QAState, preferences: Optional[dict] = None) -> Optional[dict]:
        if state.is_complete or state.current_question_index >= len(self.questions):
            return None
        question = self.questions[state.current_question_index]
        result = {
            "key": question.key, "text": question.text, "options": question.options,
            "type": question.type, "question_number": state.current_question_index + 1,
            "total_questions": len(self.questions),
        }
        if preferences and question.key in preferences:
            pref_value = preferences[question.key]
            if isinstance(pref_value, dict) and max(pref_value.values(), default=0) > 0.8:
                result["suggested_default"] = max(pref_value, key=pref_value.get)
        return result

    def record_answer(self, state: QAState, answer: str) -> QAState:
        question = self.questions[state.current_question_index]
        new_answers = {**state.answers, question.key: answer}
        new_index = state.current_question_index + 1
        return QAState(current_question_index=new_index, answers=new_answers,
            is_complete=new_index >= len(self.questions), skipped_keys=state.skipped_keys)

    def build_context(self, state: QAState) -> dict:
        keys = ["audience", "goal", "tone", "slide_count", "key_message", "visual_style",
                "must_include", "time_limit", "sections", "data_viz", "speaker_notes", "call_to_action"]
        return {k: state.answers.get(k, "") for k in keys}
