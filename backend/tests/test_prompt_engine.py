import pytest
from app.services.prompt_engine import PromptEngine
from app.models.slide import Slide, SlidePlan
from app.models.prompt import VisualDirective


@pytest.fixture
def engine():
    return PromptEngine()


@pytest.fixture
def sample_context():
    return {
        "audience": "Business executives",
        "goal": "Persuade/Convince",
        "tone": "Formal & Professional",
        "slide_count": "10-20",
        "key_message": "AI will transform our industry",
        "visual_style": "Dark & Modern",
        "must_include": "Revenue projections, market analysis",
        "time_limit": "15 minutes",
        "sections": "Introduction, Market Analysis, AI Impact, Projections, Conclusion",
        "data_viz": "A few key charts",
        "speaker_notes": "Yes, detailed notes",
        "call_to_action": "Approve AI investment proposal",
    }


@pytest.fixture
def sample_slides():
    return SlidePlan(
        project_id="test",
        slides=[
            Slide(order=0, title="Introduction", key_points=["Welcome", "Agenda overview"]),
            Slide(order=1, title="Market Analysis", key_points=["Current state", "Trends"]),
            Slide(order=2, title="Conclusion", key_points=["Summary", "Next steps"]),
        ],
        total_slides=3,
    )


def test_build_role_section(engine):
    role = engine._build_role_section()
    assert "presentation" in role.lower() or "designer" in role.lower()


def test_build_context_section(engine, sample_context):
    context = engine._build_context_section(sample_context)
    assert "Business executives" in context
    assert "Persuade" in context


def test_build_slide_plan_section(engine, sample_slides):
    section = engine._build_slide_plan_section(sample_slides)
    assert "Introduction" in section
    assert "Market Analysis" in section


def test_generate_visual_directives(engine):
    directives = engine.generate_visual_directives("Dark & Modern", 3)
    assert len(directives) == 3
    for d in directives:
        assert d.theme_name
        assert len(d.color_palette) > 0


def test_build_full_prompt(engine, sample_context, sample_slides):
    prompt = engine.build_prompt(
        qa_context=sample_context,
        slide_plan=sample_slides,
        resource_summaries=["AI market data summary"],
    )
    assert prompt.raw_text
    assert len(prompt.raw_text) > 100
    assert "Business executives" in prompt.raw_text


def test_build_prompt_with_variants(engine, sample_context, sample_slides):
    prompt = engine.build_prompt(
        qa_context=sample_context,
        slide_plan=sample_slides,
        resource_summaries=["Test summary"],
        variant_count=4,
    )
    assert len(prompt.variants) == 4
    for v in prompt.variants:
        assert v.full_prompt
        assert v.visual_directive.theme_name
