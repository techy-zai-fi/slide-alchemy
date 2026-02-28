# Prompt Engine Deep Dive

The prompt engine is the core of SlideAlchemy's intelligence. It takes your Q&A answers, resource content, slide plan, and feedback history, and assembles them into a detailed mega-prompt that instructs NotebookLM exactly how to create your presentation.

Source: `backend/app/services/prompt_engine.py`

## How the Prompt Engine Works

The engine follows a strict pipeline:

1. Receive inputs: Q&A context dict, slide plan, resource summaries, variant count, optional preference profile
2. Build each of the 7 prompt sections independently
3. Select visual directives based on the user's style preference and requested variant count
4. For each variant, assemble all sections + that variant's visual directive into a complete prompt
5. Return a `Prompt` object containing all variants

```
Inputs                         Prompt Engine                    Output
+---------+                    +-----------+                    +--------+
|QA Context|--+                |           |                    |Prompt  |
+---------+  |                 | Section   |                    |        |
|Slide Plan|--+-- build() -->  | Builders  |-- assemble() -->  |Variant1|
+---------+  |                 | + Theme   |                    |Variant2|
|Resources |--+                | Selection |                    |...     |
+---------+  |                 |           |                    +--------+
|Preferences|-+                +-----------+
+---------+
```

## The 7 Sections of the Mega-Prompt

Each section is built by a dedicated method and serves a specific purpose. They are assembled in order with double-newline separators.

### Section 1: Role Definition

**Builder:** `_build_role_section()`

Sets the AI's persona for the task. This is a fixed prompt that establishes expertise and quality expectations:

```
[ROLE]
You are a world-class presentation designer and visual storyteller with 20 years
of experience creating keynote presentations for Fortune 500 companies, TED speakers,
and top-tier consulting firms. You combine the narrative clarity of McKinsey, the
visual impact of Apple keynotes, and the data storytelling of Hans Rosling. Every
slide you create is purposeful, visually striking, and drives the audience toward
a clear takeaway.
```

**Why it matters:** The role section anchors the AI's behavior. By establishing a specific expertise level and referencing real-world quality benchmarks (McKinsey, Apple, Hans Rosling), the output quality is significantly higher than a generic "create a presentation" prompt.

### Section 2: Presentation Context

**Builder:** `_build_context_section(qa_context)`

Injects the user's answers from the Q&A interview into a structured context block:

```
[PRESENTATION CONTEXT]
- Target Audience: Business executives
- Primary Goal: Inform/Educate
- Tone & Voice: Formal & Professional
- Duration: 15 minutes
- Slide Count Target: 10-20 (Standard)
- Core Message: Q4 results exceeded all targets
- Call to Action: Approve Q1 budget
- Data Visualization Need: Yes, lots of data viz
- Speaker Notes: Yes, detailed notes
```

**Fields populated from Q&A:** audience, goal, tone, time_limit, slide_count, key_message, call_to_action, data_viz, speaker_notes.

### Section 3: Resources Summary

**Builder:** `_build_resources_section(resource_summaries)`

Provides the AI with summaries of the user's source materials, numbered for reference:

```
[RESOURCES SUMMARY]

Source 1:
This PDF contains quarterly financial data showing revenue of $4.2M...

Source 2:
YouTube transcript discussing market trends in the SaaS industry...
```

Each summary is truncated to 1,000 characters to keep the prompt within token limits while preserving the most important information. If no resources are provided, the section instructs the AI to use its own knowledge.

### Section 4: Slide-by-Slide Plan

**Builder:** `_build_slide_plan_section(slide_plan)`

Provides the detailed blueprint for every slide:

```
[SLIDE-BY-SLIDE PLAN]

--- Slide 1: Q4 Results: Exceeding Expectations ---
Key Points:
  - Revenue up 23% YoY
  - Customer base grew 15%
Supporting Data:
  - $4.2M revenue
  - 1,200 new customers
Sources: Source 1
Visual Direction: Hero number with trend line chart
Speaker Notes: Open with the headline number to grab attention...

--- Slide 2: Revenue Deep Dive ---
...
```

Slides are sorted by their `order` field. Each slide includes all available fields: title, key points, supporting data, source references, visual direction, and speaker notes.

### Section 5: Visual Directive

**Builder:** Assembled in `_assemble_prompt()` from the `VisualDirective` object

Provides specific visual design instructions for this variant:

```
[VISUAL DIRECTIVE]
- Theme: Corporate Blue
- Color Palette: #1a365d, #2b6cb0, #4299e1, #e2e8f0, #ffffff
- Typography: Inter for headings, Source Sans Pro for body
- Layout: grid with ample whitespace
- Data Visualization Style: clean bar and line charts with blue gradient
- Image & Graphic Guidance: professional stock photography, abstract geometric patterns
```

Each variant gets a different visual directive, so variant 1 might use "Corporate Blue" while variant 2 uses "Dark & Modern."

### Section 6: Quality Rules

**Builder:** `_build_quality_rules(qa_context)`

A set of 10 hard rules that constrain the output quality:

```
[QUALITY RULES]
1. Maximum 4 bullet points per slide -- if you need more, split into multiple slides
2. Every data claim must be backed by a source reference
3. Include detailed speaker notes for each slide
4. Each slide must have a clear single takeaway
5. Use transition phrases between slides to maintain narrative flow
6. Opening slide must hook the audience within 5 seconds
7. Closing slide must reinforce the call to action: Approve Q1 budget
8. Maintain consistent visual language throughout
9. Data visualizations must be self-explanatory without additional text
10. Must-include content: Revenue chart, customer growth data
```

Rules 3, 7, and 10 are dynamic -- they adapt based on the Q&A answers:
- Rule 3 changes based on whether the user selected "detailed" speaker notes
- Rule 7 injects the user's specific call to action
- Rule 10 injects the "must include" content from the Q&A

### Section 7: User Preferences (Optional)

**Builder:** `_build_preferences_section(preferences)`

Only included if the user has a preference profile from past feedback:

```
[USER PREFERENCES -- learned from past presentations]
Preferred styles: clean design (82%), minimal (71%), professional (68%)
Preferred tones: formal (90%), authoritative (75%)
Favorite color palette: #1a365d, #2b6cb0, #4299e1, #e2e8f0, #ffffff
Preferred bullet density: medium
```

This section is built from the `PreferenceProfile` model which is updated after every feedback submission. Styles and tones are sorted by weight (descending) and the top 3 / top 2 are included respectively.

## The 4 Theme Presets

Each theme preset is a `VisualDirective` object with 6 design properties. The prompt engine uses these to generate visual directives for each variant.

### Corporate Blue

| Property | Value |
|----------|-------|
| Color Palette | `#1a365d` `#2b6cb0` `#4299e1` `#e2e8f0` `#ffffff` |
| Typography | Inter for headings, Source Sans Pro for body |
| Layout Style | Grid with ample whitespace |
| Data Viz Style | Clean bar and line charts with blue gradient |
| Image Guidance | Professional stock photography, abstract geometric patterns |

**Best for:** Board meetings, investor updates, corporate communications, formal reports.

### Dark & Modern

| Property | Value |
|----------|-------|
| Color Palette | `#0f172a` `#1e293b` `#6366f1` `#a5b4fc` `#f8fafc` |
| Typography | Outfit for headings, DM Sans for body |
| Layout Style | Asymmetric with bold hero elements |
| Data Viz Style | Neon-accent charts on dark backgrounds |
| Image Guidance | High contrast imagery, gradient overlays, minimal icons |

**Best for:** Tech product launches, startup pitches, developer conferences, modern brand presentations.

### Minimal & Clean

| Property | Value |
|----------|-------|
| Color Palette | `#ffffff` `#f9fafb` `#111827` `#6b7280` `#3b82f6` |
| Typography | Poppins for headings, Open Sans for body |
| Layout Style | Centered with generous margins |
| Data Viz Style | Thin line charts, donut charts, subtle colors |
| Image Guidance | Minimal illustrations, lots of whitespace, icon-driven |

**Best for:** Design reviews, product walkthroughs, educational content, documentation-style presentations.

### Vibrant & Creative

| Property | Value |
|----------|-------|
| Color Palette | `#7c3aed` `#ec4899` `#f59e0b` `#10b981` `#1e1b4b` |
| Typography | Space Grotesk for headings, Nunito for body |
| Layout Style | Dynamic layouts with overlapping elements |
| Data Viz Style | Colorful infographic-style charts, icon arrays |
| Image Guidance | Vibrant photography, gradient backgrounds, playful shapes |

**Best for:** Marketing campaigns, brand storytelling, creative pitches, workshop presentations.

## How Variants Work

When you request N variants (1-4), the engine selects N theme presets and generates a separate complete prompt for each:

1. **Style matching:** The engine takes the user's `visual_style` answer from the Q&A (e.g., "Dark & Modern") and matches it against theme preset keys by checking for keyword overlap
2. **Priority ordering:** The best-matching preset is placed first in the priority list; remaining presets follow in their default order
3. **Selection:** The first N presets from the priority list become the N variants
4. **Assembly:** Each variant gets its own `PromptVariant` object containing:
   - Variant number (1-based)
   - Theme name (e.g., "Corporate Blue")
   - The full `VisualDirective` object
   - The complete assembled prompt text (all 7 sections with this variant's visual directive)

**Example with 2 variants and style "dark":**

| Variant | Theme Selected | Reason |
|---------|---------------|--------|
| 1 | Dark & Modern | "dark" matches "dark-modern" |
| 2 | Corporate Blue | Next in default order |

The variant instruction at the end of each prompt tells the AI which variant it is building:

```
[VARIANT 1 of 2: Dark & Modern]
Apply this specific visual treatment to all slides in this variant.
```

## How User Preferences Are Injected

The preference profile evolves over time through the feedback loop:

1. **Initial state:** No preferences (section is omitted from the prompt)
2. **After first feedback:** Tags from the feedback become style indicators with initial weights
3. **Exponential moving average:** Each subsequent feedback updates weights: `new = current * 0.7 + (rating/5.0) * 0.3`
4. **High-confidence suggestions:** When a style weight exceeds 0.8, the QA engine can suggest it as a default answer

The preferences section is only included when `total_presentations > 0`. It provides soft guidance -- the AI should consider these preferences but the explicit Q&A answers and quality rules take precedence.

## Tips for Writing Good Presentation Prompts

While SlideAlchemy builds prompts automatically, understanding what makes a good prompt helps you get better results through the Q&A:

### Be Specific in the Q&A

- **Key message:** "Q4 revenue grew 23% to $4.2M driven by enterprise expansion" is far better than "Q4 was good"
- **Call to action:** "Approve $2M Q1 marketing budget" is better than "Get buy-in"
- **Must-include:** List specific data points, quotes, or topics rather than vague categories

### Optimize Your Sections

When listing sections in the Q&A, use descriptive names that guide the AI:

**Weak:** "Intro, Middle, End"

**Strong:** "Hook with key stat, Market landscape and opportunity size, Our solution and differentiators, Traction and growth metrics, Revenue model and unit economics, Team and advisors, The ask and use of funds"

### Choose the Right Visual Style

Match the style to your audience:

- Executives and board members respond best to **Corporate Blue** or **Minimal & Clean**
- Technical audiences appreciate **Dark & Modern** with data-heavy slides
- Creative and marketing audiences engage more with **Vibrant & Creative**

### Provide Rich Resources

The more and better your resources, the more grounded the presentation will be:

- Upload the actual data/report rather than summarizing it yourself
- Include competitor information as supplementary resources
- Add relevant YouTube videos for the AI to reference real-world context
- Use the research feature to fill gaps before generating

### Iterate with Feedback

The feedback loop is the most powerful feature for long-term quality:

- Always rate your presentations, even quick ones
- Use descriptive tags ("too text-heavy", "perfect data viz", "great narrative flow")
- Rate individual slides so the system learns which slide types work for you
- After 3-5 presentations, the preference profile significantly improves output quality
