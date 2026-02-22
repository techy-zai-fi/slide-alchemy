import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..models.feedback import Feedback, PreferenceProfile
from ..utils.config import DATA_DIR, PREFERENCES_FILE, PATTERNS_DB


class FeedbackService:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_dir = self.data_dir / "feedbacks"
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.preferences_file = self.data_dir / "preferences.json"
        self.patterns_db = self.data_dir / "patterns.db"
        self._init_patterns_db()

    def _init_patterns_db(self):
        conn = sqlite3.connect(str(self.patterns_db))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS success_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_fragment TEXT NOT NULL,
                rating INTEGER NOT NULL,
                tags TEXT DEFAULT '[]',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def submit_feedback(self, feedback: Feedback) -> None:
        # Save feedback
        feedback_file = self.feedback_dir / f"{feedback.project_id}_v{feedback.variant_number}.json"
        feedback_file.write_text(feedback.model_dump_json(indent=2))

        # Update preference profile
        self._update_preferences(feedback)

    def get_feedbacks(self, project_id: str) -> list[Feedback]:
        feedbacks = []
        for f in self.feedback_dir.glob(f"{project_id}_v*.json"):
            feedbacks.append(Feedback.model_validate_json(f.read_text()))
        return feedbacks

    def get_preference_profile(self) -> PreferenceProfile:
        if self.preferences_file.exists():
            return PreferenceProfile.model_validate_json(self.preferences_file.read_text())
        return PreferenceProfile()

    def _update_preferences(self, feedback: Feedback) -> None:
        profile = self.get_preference_profile()

        # Update tag preferences as style indicators
        for tag in feedback.tags:
            current = profile.preferred_styles.get(tag, 0.5)
            weight = feedback.overall_rating / 5.0
            profile.preferred_styles[tag] = current * 0.7 + weight * 0.3

        profile.total_presentations += 1
        profile.last_updated = datetime.now()

        self.preferences_file.write_text(profile.model_dump_json(indent=2))

    def store_success_pattern(self, prompt_fragment: str, rating: int, tags: list[str]) -> None:
        conn = sqlite3.connect(str(self.patterns_db))
        conn.execute(
            "INSERT INTO success_patterns (prompt_fragment, rating, tags) VALUES (?, ?, ?)",
            (prompt_fragment, rating, json.dumps(tags)),
        )
        conn.commit()
        conn.close()

    def get_top_patterns(self, limit: int = 10) -> list[dict]:
        conn = sqlite3.connect(str(self.patterns_db))
        cursor = conn.execute(
            "SELECT prompt_fragment, rating, tags, created_at FROM success_patterns ORDER BY rating DESC LIMIT ?",
            (limit,),
        )
        patterns = []
        for row in cursor:
            patterns.append({
                "prompt_fragment": row[0],
                "rating": row[1],
                "tags": json.loads(row[2]),
                "created_at": row[3],
            })
        conn.close()
        return patterns
