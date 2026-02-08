import pytest
from app.services.qa_engine import QAEngine, QAState


def test_qa_state_init():
    state = QAState()
    assert state.current_question_index == 0
    assert len(state.answers) == 0
    assert not state.is_complete


def test_qa_engine_init():
    engine = QAEngine()
    assert len(engine.questions) >= 8


def test_get_first_question():
    engine = QAEngine()
    state = QAState()
    q = engine.get_current_question(state)
    assert q is not None
    assert "text" in q
    assert "key" in q


def test_record_answer():
    engine = QAEngine()
    state = QAState()
    state = engine.record_answer(state, "General audience, business professionals")
    assert len(state.answers) == 1
    assert state.current_question_index == 1


def test_complete_after_all_questions():
    engine = QAEngine()
    state = QAState()
    for i in range(len(engine.questions)):
        state = engine.record_answer(state, f"Answer {i}")
    assert state.is_complete


def test_build_context_from_answers():
    engine = QAEngine()
    state = QAState()
    state = engine.record_answer(state, "Business executives")
    state = engine.record_answer(state, "Persuade to invest")
    context = engine.build_context(state)
    assert "audience" in context
    assert "goal" in context
