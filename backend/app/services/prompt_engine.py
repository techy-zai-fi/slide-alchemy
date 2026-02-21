from ..models.prompt import Prompt, PromptVariant, VisualDirective
from ..models.slide import SlidePlan
from ..models.feedback import PreferenceProfile
from typing import Optional


THEME_PRESETS = {
    "corporate-blue": VisualDirective(
        theme_name="Corporate Blue",
        color_palette=["#1a365d", "#2b6cb0", "#4299e1", "#e2e8f0", "#ffffff"],
        typography="Inter for headings, Source Sans Pro for body",
        layout_style="grid with ample whitespace",
        data_viz_style="clean bar and line charts with blue gradient",
        image_guidance="professional stock photography, abstract geometric patterns",
    ),
    "dark-modern": VisualDirective(
        theme_name="Dark & Modern",
        color_palette=["#0f172a", "#1e293b", "#6366f1", "#a5b4fc", "#f8fafc"],
        typography="Outfit for headings, DM Sans for body",
        layout_style="asymmetric with bold hero elements",
        data_viz_style="neon-accent charts on dark backgrounds",
        image_guidance="high contrast imagery, gradient overlays, minimal icons",
    ),
    "minimal-clean": VisualDirective(
        theme_name="Minimal & Clean",
        color_palette=["#ffffff", "#f9fafb", "#111827", "#6b7280", "#3b82f6"],
        typography="Poppins for headings, Open Sans for body",
        layout_style="centered with generous margins",
        data_viz_style="thin line charts, donut charts, subtle colors",
        image_guidance="minimal illustrations, lots of whitespace, icon-driven",
    ),
    "vibrant-creative": VisualDirective(
        theme_name="Vibrant & Creative",
        color_palette=["#7c3aed", "#ec4899", "#f59e0b", "#10b981", "#1e1b4b"],
        typography="Space Grotesk for headings, Nunito for body",
        layout_style="dynamic layouts with overlapping elements",
        data_viz_style="colorful infographic-style charts, icon arrays",
        image_guidance="vibrant photography, gradient backgrounds, playful shapes",
    ),
}


class PromptEngine:
    def build_prompt(
        self,
        qa_context: dict,
        slide_plan: SlidePlan,
        resource_summaries: list[str],
        variant_count: int = 1,
        preferences: Optional[PreferenceProfile] = None,
    ) -> Prompt:
        role = self._build_role_section()
        context = self._build_context_section(qa_context)
        resources = self._build_resources_section(resource_summaries)
        slides = self._build_slide_plan_section(slide_plan)
        quality = self._build_quality_rules(qa_context)
        prefs = self._build_preferences_section(preferences) if preferences else ""

        visual_style = qa_context.get("visual_style", "Minimal & Clean")
        directives = self.generate_visual_directives(visual_style, variant_count)

        variants = []
        for i, directive in enumerate(directives):
            variant_instruction = self._build_variant_instruction(i + 1, variant_count, directive)
            full_prompt = self._assemble_prompt(role, context, resources, slides, directive, quality, prefs, variant_instruction)
            variants.append(PromptVariant(
                variant_number=i + 1,
                variant_description=directive.theme_name,
                visual_directive=directive,
                full_prompt=full_prompt,
            ))

        prompt = Prompt(
            project_id=slide_plan.project_id,
            role_section=role,
            context_section=context,
            resources_summary=resources,
            slide_plan_section=slides,
            quality_rules=quality,
            user_preferences_section=prefs,
            variants=variants,
            raw_text=variants[0].full_prompt if variants else "",
        )
        return prompt

    def _build_role_section(self) -> str:
        return """You are a world-class presentation designer and visual storyteller with 20 years of experience creating keynote presentations for Fortune 500 companies, TED speakers, and top-tier consulting firms. You combine the narrative clarity of McKinsey, the visual impact of Apple keynotes, and the data storytelling of Hans Rosling. Every slide you create is purposeful, visually striking, and drives the audience toward a clear takeaway."""

    def _build_context_section(self, qa_context: dict) -> str:
        return f"""[PRESENTATION CONTEXT]
- Target Audience: {qa_context.get('audience', 'General audience')}
- Primary Goal: {qa_context.get('goal', 'Inform')}
- Tone & Voice: {qa_context.get('tone', 'Professional')}
- Duration: {qa_context.get('time_limit', 'No limit')}
- Slide Count Target: {qa_context.get('slide_count', '10-20')}
- Core Message: {qa_context.get('key_message', 'To be determined')}
- Call to Action: {qa_context.get('call_to_action', 'None specified')}
- Data Visualization Need: {qa_context.get('data_viz', 'Moderate')}
- Speaker Notes: {qa_context.get('speaker_notes', 'Brief bullet points')}"""

    def _build_resources_section(self, summaries: list[str]) -> str:
        if not summaries:
            return "[RESOURCES]\nNo external resources provided. Use your knowledge to create compelling content."

        sections = ["[RESOURCES SUMMARY]"]
        for i, summary in enumerate(summaries):
            sections.append(f"\nSource {i + 1}:\n{summary[:1000]}")
        return "\n".join(sections)

    def _build_slide_plan_section(self, plan: SlidePlan) -> str:
        lines = ["[SLIDE-BY-SLIDE PLAN]"]
        for slide in sorted(plan.slides, key=lambda s: s.order):
            lines.append(f"\n--- Slide {slide.order + 1}: {slide.title} ---")
            if slide.key_points:
                lines.append("Key Points:")
                for point in slide.key_points:
                    lines.append(f"  - {point}")
            if slide.supporting_data:
                lines.append("Supporting Data:")
                for data in slide.supporting_data:
                    lines.append(f"  - {data}")
            if slide.source_refs:
                lines.append(f"Sources: {', '.join(slide.source_refs)}")
            if slide.visual_direction:
                lines.append(f"Visual Direction: {slide.visual_direction}")
            if slide.speaker_notes:
                lines.append(f"Speaker Notes: {slide.speaker_notes}")
        return "\n".join(lines)

    def _build_quality_rules(self, qa_context: dict) -> str:
        return f"""[QUALITY RULES]
1. Maximum 4 bullet points per slide — if you need more, split into multiple slides
2. Every data claim must be backed by a source reference
3. {"Include detailed speaker notes for each slide" if "detailed" in qa_context.get("speaker_notes", "").lower() else "Include brief speaker notes"}
4. Each slide must have a clear single takeaway
5. Use transition phrases between slides to maintain narrative flow
6. Opening slide must hook the audience within 5 seconds
7. Closing slide must reinforce the call to action: {qa_context.get('call_to_action', 'N/A')}
8. Maintain consistent visual language throughout
9. Data visualizations must be self-explanatory without additional text
10. Must-include content: {qa_context.get('must_include', 'None specified')}"""

    def _build_preferences_section(self, preferences: PreferenceProfile) -> str:
        if not preferences or preferences.total_presentations == 0:
            return ""

        lines = ["[USER PREFERENCES — learned from past presentations]"]
        if preferences.preferred_styles:
            top_styles = sorted(preferences.preferred_styles.items(), key=lambda x: x[1], reverse=True)[:3]
            lines.append(f"Preferred styles: {', '.join(f'{s} ({w:.0%})' for s, w in top_styles)}")
        if preferences.preferred_tones:
            top_tones = sorted(preferences.preferred_tones.items(), key=lambda x: x[1], reverse=True)[:2]
            lines.append(f"Preferred tones: {', '.join(f'{t} ({w:.0%})' for t, w in top_tones)}")
        if preferences.favorite_palettes:
            lines.append(f"Favorite color palette: {', '.join(preferences.favorite_palettes[0])}")
        lines.append(f"Preferred bullet density: {preferences.bullet_density}")
        return "\n".join(lines)

    def _build_variant_instruction(self, variant_num: int, total: int, directive: VisualDirective) -> str:
        return f"""[VARIANT {variant_num} of {total}: {directive.theme_name}]
Apply this specific visual treatment to all slides in this variant."""

    def _assemble_prompt(self, role: str, context: str, resources: str, slides: str,
                          directive: VisualDirective, quality: str, preferences: str, variant: str) -> str:
        visual = f"""[VISUAL DIRECTIVE]
- Theme: {directive.theme_name}
- Color Palette: {', '.join(directive.color_palette)}
- Typography: {directive.typography}
- Layout: {directive.layout_style}
- Data Visualization Style: {directive.data_viz_style}
- Image & Graphic Guidance: {directive.image_guidance}"""

        sections = [
            f"[ROLE]\n{role}",
            context,
            resources,
            slides,
            visual,
            quality,
        ]
        if preferences:
            sections.append(preferences)
        sections.append(variant)

        return "\n\n".join(sections)

    def generate_visual_directives(self, style_hint: str, count: int) -> list[VisualDirective]:
        all_presets = list(THEME_PRESETS.values())
        style_lower = style_hint.lower()

        # Find the best match for the user's style preference
        priority = []
        for key, preset in THEME_PRESETS.items():
            if any(word in style_lower for word in key.split("-")):
                priority.insert(0, preset)
            else:
                priority.append(preset)

        return priority[:count]
