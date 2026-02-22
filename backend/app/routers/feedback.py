from fastapi import APIRouter
from ..models.feedback import Feedback, PreferenceProfile
from ..services.feedback_service import FeedbackService

router = APIRouter(prefix="/api/feedback", tags=["feedback"])
service = FeedbackService()


@router.post("/submit")
async def submit_feedback(feedback: Feedback):
    service.submit_feedback(feedback)

    # Store success patterns for high-rated variants
    if feedback.overall_rating >= 4:
        service.store_success_pattern(
            prompt_fragment=f"Tags: {', '.join(feedback.tags)}",
            rating=feedback.overall_rating,
            tags=feedback.tags,
        )

    return {"status": "saved"}


@router.get("/preferences", response_model=PreferenceProfile)
async def get_preferences():
    return service.get_preference_profile()


@router.get("/patterns")
async def get_patterns(limit: int = 10):
    return service.get_top_patterns(limit)


@router.get("/{project_id}")
async def get_project_feedback(project_id: str):
    return service.get_feedbacks(project_id)
