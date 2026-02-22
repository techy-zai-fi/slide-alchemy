import pytest
import json
from pathlib import Path
from app.services.feedback_service import FeedbackService
from app.models.feedback import Feedback, SlideRating, PreferenceProfile


@pytest.fixture
def service(tmp_path):
    return FeedbackService(data_dir=tmp_path)


@pytest.fixture
def sample_feedback():
    return Feedback(
        project_id="test-1",
        variant_number=1,
        overall_rating=5,
        tags=["colors", "layout", "flow"],
        slide_ratings=[
            SlideRating(slide_id="s1", thumbs_up=True, comment="Great chart"),
            SlideRating(slide_id="s2", thumbs_up=False, comment="Too wordy"),
        ],
    )


def test_submit_feedback(service, sample_feedback):
    service.submit_feedback(sample_feedback)
    feedbacks = service.get_feedbacks("test-1")
    assert len(feedbacks) == 1
    assert feedbacks[0].overall_rating == 5


def test_preference_profile_updates(service, sample_feedback):
    service.submit_feedback(sample_feedback)
    profile = service.get_preference_profile()
    assert profile.total_presentations == 1


def test_multiple_feedbacks_build_profile(service):
    for i in range(3):
        fb = Feedback(
            project_id=f"proj-{i}",
            variant_number=1,
            overall_rating=4 + (i % 2),
            tags=["colors", "layout"],
        )
        service.submit_feedback(fb)

    profile = service.get_preference_profile()
    assert profile.total_presentations == 3


def test_success_patterns_stored(service, sample_feedback):
    service.store_success_pattern(
        prompt_fragment="[VISUAL DIRECTIVE]\n- Theme: Dark & Modern",
        rating=5,
        tags=["colors", "layout"],
    )
    patterns = service.get_top_patterns(limit=5)
    assert len(patterns) >= 1
    assert patterns[0]["rating"] == 5
