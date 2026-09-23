import streamlit as st
from groq import Groq
import json
import re
import html


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="LinkAI — LinkedIn Post Generator",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# GROQ CLIENT
# ============================================================

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)

except KeyError:
    st.error(
        "GROQ_API_KEY is missing. "
        "Go to Streamlit Cloud → Manage app → Settings → Secrets "
        "and add your Groq API key."
    )
    st.stop()

except Exception as e:
    st.error(f"Could not initialize Groq: {e}")
    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "generated_post" not in st.session_state:
    st.session_state.generated_post = None

if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""

if "generation_count" not in st.session_state:
    # Bumped every time a new post is generated so the editable
    # text_area below gets a fresh widget key. Without this,
    # Streamlit ignores the `value=` argument on every run after
    # the first (because the widget's key already exists in
    # session_state), so the box silently keeps showing the very
    # first generated post no matter what settings you change.
    st.session_state.generation_count = 0


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background:
            radial-gradient(
                circle at 50% -10%,
                rgba(29, 78, 216, 0.16),
                transparent 35%
            ),
            #07111f;
        color: #f8fafc;
    }

    .main .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ---------- HEADER ---------- */

    .linkai-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }

    .brand {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: #ffffff;
    }

    .brand span {
        color: #38bdf8;
    }

    .online-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 13px;
        border-radius: 999px;
        background: rgba(34, 197, 94, 0.10);
        border: 1px solid rgba(34, 197, 94, 0.25);
        color: #86efac;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .online-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 10px rgba(34, 197, 94, 0.8);
    }

    /* ---------- HERO ---------- */

    .hero {
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 2.5rem;
    }

    .hero h1 {
        font-size: 3.4rem;
        line-height: 1.05;
        letter-spacing: -2px;
        margin-bottom: 0.8rem;
        color: #ffffff;
    }

    .hero h1 span {
        background: linear-gradient(
            90deg,
            #38bdf8,
            #818cf8
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero p {
        color: #94a3b8;
        font-size: 1.05rem;
        max-width: 650px;
        margin: auto;
        line-height: 1.7;
    }

    /* ---------- SETTINGS ---------- */

    div[data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.70);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 16px;
        margin-bottom: 1.5rem;
    }

    /* ---------- INPUTS ---------- */

    .stTextArea textarea,
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] {
        background: #0b1729 !important;
        border: 1px solid #1e293b !important;
        color: #f8fafc !important;
        border-radius: 12px !important;
    }

    textarea {
        line-height: 1.6 !important;
    }

    label {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }

    /* ---------- BUTTON ---------- */

    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(56, 189, 248, 0.25);
        background: linear-gradient(
            135deg,
            #0284c7,
            #4f46e5
        );
        color: white;
        font-weight: 700;
        padding: 0.75rem 1.2rem;
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #38bdf8;
        transform: translateY(-1px);
        box-shadow: 0 8px 25px rgba(14, 165, 233, 0.20);
    }

    /* ---------- POST CARD ---------- */

    .post-card {
        background: rgba(15, 23, 42, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 18px;
        padding: 1.35rem;
        margin-bottom: 1rem;
    }

    .post-card h3 {
        color: #f8fafc;
        margin-bottom: 0.8rem;
    }

    .hook-box {
        background: rgba(56, 189, 248, 0.06);
        border-left: 3px solid #38bdf8;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin-bottom: 1rem;
    }

    .hook-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #38bdf8;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .hook-text {
        color: #e2e8f0;
        font-weight: 600;
        line-height: 1.5;
    }

    .stat-box {
        display: flex;
        gap: 12px;
        margin-top: 0.8rem;
    }

    .stat {
        background: #0b1729;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 6px 10px;
        color: #94a3b8;
        font-size: 0.75rem;
    }

    /* ---------- PREVIEW ---------- */

    .linkedin-preview {
        background: #ffffff;
        color: #172b4d;
        border-radius: 16px;
        padding: 1.3rem;
        margin-top: 1rem;
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.25);
    }

    .linkedin-profile {
        display: flex;
        gap: 10px;
        align-items: center;
        margin-bottom: 1rem;
    }

    .profile-avatar {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: linear-gradient(
            135deg,
            #0f172a,
            #2563eb
        );
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 800;
    }

    .profile-name {
        font-weight: 700;
        color: #172b4d;
    }

    .profile-role {
        font-size: 0.75rem;
        color: #667085;
    }

    .preview-content {
        white-space: pre-wrap;
        line-height: 1.55;
        color: #172b4d;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(148, 163, 184, 0.08);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="linkai-header">'
    '<div class="brand">Link<span>AI</span></div>'
    '<div class="online-status">'
    '<div class="online-dot"></div>'
    'Groq AI Online'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    '<div class="hero">'
    '<h1>Write LinkedIn posts that <span>people actually read.</span></h1>'
    '<p>Turn your ideas, projects, achievements, and experiences '
    'into a natural LinkedIn post with a strong, scroll-stopping '
    'hook — shaped by the tone and style you choose.</p>'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# WRITING SETTINGS
# ============================================================

with st.expander("⚙️ Writing Settings", expanded=True):

    col1, col2, col3 = st.columns(3)

    with col1:

        post_type = st.selectbox(
            "Post Type",
            [
                "Project / Achievement",
                "Personal Experience",
                "Educational / Insight",
                "Career Update",
                "Internship / Work Experience",
                "Announcement",
                "General LinkedIn Post"
            ]
        )

        tone = st.selectbox(
            "Tone",
            [
                "Natural & Human",
                "Professional",
                "Confident",
                "Friendly",
                "Thoughtful",
                "Technical"
            ]
        )

    with col2:

        writing_style = st.selectbox(
            "Writing Style",
            [
                "Natural & Human",
                "Storytelling",
                "Bold & Punchy",
                "Technical & Insightful",
                "Personal & Reflective",
                "Minimal & Clean",
                "Confident & Professional"
            ]
        )

        target_audience = st.selectbox(
            "Target Audience",
            [
                "General LinkedIn Audience",
                "Engineering Students",
                "Engineers",
                "AI / Tech Professionals",
                "Recruiters",
                "Entrepreneurs",
                "Developers",
                "Academic / Research Audience"
            ]
        )

    with col3:

        post_length = st.selectbox(
            "Post Length",
            [
                "Short — 80–120 words",
                "Medium — 150–220 words",
                "Long — 250–350 words"
            ]
        )

        use_emojis = st.checkbox(
            "Use Emojis",
            value=True
        )

        use_hashtags = st.checkbox(
            "Include Hashtags",
            value=True
        )

        use_cta = st.checkbox(
            "Include CTA",
            value=False
        )


# ============================================================
# MAIN COMPOSER
# ============================================================

st.markdown("### ✦ What do you want to post about?")

topic = st.text_area(
    "Topic",
    placeholder=(
        "Example: I built an AI-powered Mechatronics Engineer "
        "Copilot using Python and Groq API..."
    ),
    height=150,
    label_visibility="collapsed"
)


col1, col2 = st.columns(2)

with col1:

    keywords = st.text_input(
        "Keywords",
        placeholder="AI, Python, Mechatronics, Computer Vision..."
    )

with col2:

    important_details = st.text_input(
        "Important Details",
        placeholder="What should definitely be mentioned?"
    )


st.write("")


# ============================================================
# TONE / STYLE GUIDES
# ============================================================
#
# The previous version of this app only handed the model a
# label like "Tone: Confident" or "Writing Style: Storytelling"
# and then told it TONE was "the single most important
# instruction". That caused two problems:
#
#   1. Tone dominated everything, so changing Writing Style
#      alone barely moved the output.
#   2. Several Tone and Writing Style labels overlap in meaning
#      ("Natural & Human" appears in both lists, "Confident"
#      vs. "Confident & Professional"), so the model had no way
#      to tell they were supposed to be two independent axes.
#
# The dictionaries below give the model concrete, mechanical
# instructions (sentence length, pacing, structure) for each
# option instead of a vague label, and the two axes are now
# treated as co-equal and independent: TONE = attitude/voice,
# STYLE = structure/composition.
# ============================================================

TONE_GUIDES = {
    "Natural & Human": (
        "Casual and conversational, like talking to a friend. "
        "Contractions are welcome. No corporate polish."
    ),
    "Professional": (
        "Polished and workplace-appropriate. Composed and "
        "understated rather than flashy."
    ),
    "Confident": (
        "Assertive, declarative sentences. Avoid hedging words "
        "like 'maybe', 'I think', or 'kind of'."
    ),
    "Friendly": (
        "Warm and approachable. Speak directly to the reader "
        "using 'you' where natural."
    ),
    "Thoughtful": (
        "Reflective and measured. Favors nuance over bold "
        "claims; slower, more considered pacing."
    ),
    "Technical": (
        "Precise and matter-of-fact. Leads with a specific "
        "technical observation or detail rather than an emotion."
    ),
}

STYLE_GUIDES = {
    "Natural & Human": (
        "Simple sentence structures and plain vocabulary. Reads "
        "like a real person typed it in one sitting, not a "
        "polished draft."
    ),
    "Storytelling": (
        "Structure the post as a mini narrative: set a moment "
        "in time, build to a turning point or tension, then "
        "resolve it. Use concrete scene details, not abstractions."
    ),
    "Bold & Punchy": (
        "Short, punchy sentences and sentence fragments. Strong "
        "verbs. Minimal connecting words. High-energy pacing — "
        "avoid long, winding sentences."
    ),
    "Technical & Insightful": (
        "Lead with a specific technical detail, number, or "
        "mechanism, then unpack why it matters. Precise, "
        "domain-accurate language."
    ),
    "Personal & Reflective": (
        "First-person introspection. Explore what was learned "
        "or felt. Slower pacing, more internal than external."
    ),
    "Minimal & Clean": (
        "Very short paragraphs (1-2 sentences each) with heavy "
        "whitespace. No filler words. Every line earns its place."
    ),
    "Confident & Professional": (
        "Structured like a well-organized brief: a clear point, "
        "clear supporting evidence, a clear close. Declarative, "
        "no rambling."
    ),
}


# ============================================================
# GENERATION FUNCTIONS
# ============================================================

def extract_json(text):
    """
    Safely extract a JSON object from the model response.
    Handles Markdown code fences and extra text.
    """

    if not text:
        return None

    text = text.strip()

    # Remove Markdown fences
    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*",
        "",
        text
    )

    # Locate JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return None

    json_text = text[start:end + 1]

    try:
        return json.loads(json_text)

    except json.JSONDecodeError:
        # Attempt minor cleanup
        json_text = json_text.replace("\n", "\\n")

        try:
            return json.loads(json_text)
        except Exception:
            return None


def validate_result(data):
    """
    A valid result is a single object with a non-empty
    "hook" and "post" string field.
    """

    if not isinstance(data, dict):
        return False

    required = ["hook", "post"]

    for key in required:

        if key not in data:
            return False

        if not isinstance(data[key], str):
            return False

        if not data[key].strip():
            return False

    return True


def parse_word_range(post_length):
    """
    Extract a (min, max) word count tuple from the
    post_length label, e.g. "Short — 80–120 words" -> (80, 120).
    Falls back to a sane default if parsing fails.
    """

    numbers = re.findall(r"\d+", post_length)

    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])

    return 150, 220


def generate_post(
    user_prompt,
    tone,
    writing_style,
    target_audience,
    post_length,
    use_emojis,
    use_hashtags,
    use_cta
):

    word_min, word_max = parse_word_range(post_length)

    tone_guide = TONE_GUIDES.get(tone, "")
    style_guide = STYLE_GUIDES.get(writing_style, "")

    mandatory_settings = f"""
MANDATORY USER SETTINGS (highest priority — these define how
the post must sound and read):

TONE and WRITING STYLE are two SEPARATE, EQUALLY IMPORTANT axes.
Do not let one override the other, and do not collapse them into
a single generic voice:

- TONE = {tone}
  This controls the ATTITUDE / EMOTIONAL COLORING of the writing.
  Concretely: {tone_guide}

- WRITING STYLE = {writing_style}
  This controls the STRUCTURE / COMPOSITION of the writing —
  sentence length, pacing, paragraph rhythm, how the post is
  built. Concretely: {style_guide}

  If only WRITING STYLE changes between two generations (even
  with the same TONE and same topic), the sentence structure,
  pacing, and paragraph rhythm MUST be clearly different. A
  reader should be able to tell the style apart without being
  told what it is.

- TARGET AUDIENCE: {target_audience}
  Choose vocabulary, examples, and framing that speak directly
  to this audience. A post for "Recruiters" should read
  differently from one for "Developers" even with the same
  underlying facts.

- LENGTH: the "post" field MUST be between {word_min} and
  {word_max} words. Count words before finalizing your answer.

- EMOJIS: {"Use emojis naturally where appropriate." if use_emojis else "Do NOT use any emojis."}

- HASHTAGS: {"Include 3-5 relevant hashtags at the end of the post." if use_hashtags else "Do NOT include hashtags."}

- CTA: {"End the post with a natural, relevant call to action." if use_cta else "Do NOT include a call to action."}
"""

    system_prompt = mandatory_settings + """
You are LinkAI, an expert LinkedIn content writer.

Your job is to transform the user's real information into
ONE high-quality LinkedIn post with a strong, scroll-stopping
hook.

IMPORTANT RULES:

1. Return ONLY valid JSON.
2. Do NOT use Markdown code fences.
3. Do NOT write explanations before or after the JSON.
4. Do not invent achievements, statistics, results, companies,
   technologies, experiences, awards, or facts.
5. Only use information provided by the user.
6. Keep the writing natural and human — never sound like it
   was written by an AI.
7. Avoid excessive corporate buzzwords.
8. Avoid generic AI-generated openings.

NEVER begin with generic phrases such as:

"Today I am excited to..."
"I am thrilled to..."
"I am excited to announce..."
"I recently had the opportunity..."
"I am happy to share..."
"Leveraging the power of..."
"In today's rapidly evolving world..."

HOOK RULES:

The first 1–2 lines are extremely important — they decide
whether someone keeps reading.

The hook must be specific, interesting, and shaped by BOTH the
TONE and WRITING STYLE settings above — tone sets the attitude,
style sets the structure. Depending on those settings, draw on
approaches such as:

- curiosity
- a surprising realization
- a strong, confident statement
- a problem or tension
- a contrast
- a personal realization
- a technical insight
- an unexpected lesson
- a direct question
- a challenge

Pick whichever approach best matches the requested TONE and
WRITING STYLE — do not default to the same hook style every time.

POST STRUCTURE:

Write like a real person, not a press release. Ground the
post in the user's actual information, build naturally from
the hook into the substance, and close with a clear takeaway
(and a CTA only if requested).

LINKEDIN FORMATTING:

Use short paragraphs.

Use whitespace.

Avoid huge blocks of text.

OUTPUT FORMAT:

{
  "hook": "Exact first 1–2 lines of the post",
  "post": "The complete LinkedIn post, including the hook at the start"
}
"""

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            temperature=0.9,

            # Raised from 2500: gpt-oss-120b is a reasoning model,
            # and even with reasoning_format="hidden" its hidden
            # chain-of-thought tokens still count against this
            # budget. A longer/more detailed system prompt (like
            # the tone/style guides above) makes it "think" more,
            # so a low ceiling here can get eaten by hidden
            # reasoning before the actual JSON post is written,
            # producing a "max completion tokens reached before
            # generating a valid document" error.
            max_tokens=4096,

            # Cap reasoning effort so the model doesn't spend an
            # unpredictable (and sometimes large) number of hidden
            # tokens "thinking" about a LinkedIn post — this is a
            # simple generation task, not one that benefits from
            # deep reasoning, and keeping this low leaves more of
            # the token budget for the actual output.
            reasoning_effort="low",

            # Hide the model's internal chain-of-thought so only
            # the final answer comes back in message.content —
            # without this, gpt-oss-120b (a reasoning model) can
            # leak reasoning text or <think> tags into the
            # response, or run out of tokens before finishing.
            reasoning_format="hidden",

            # Force the model to emit exactly this JSON shape
            # (Groq structured outputs, strict mode, supported on
            # gpt-oss-120b). This is far more reliable than
            # hoping the model wraps its answer in clean JSON.
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "linkedin_post",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "hook": {
                                "type": "string",
                                "description": (
                                    "The exact first 1-2 lines "
                                    "of the post."
                                )
                            },
                            "post": {
                                "type": "string",
                                "description": (
                                    "The complete LinkedIn post, "
                                    "including the hook at the "
                                    "start."
                                )
                            }
                        },
                        "required": ["hook", "post"],
                        "additionalProperties": False
                    }
                }
            }
        )

        raw_response = response.choices[0].message.content

        data = extract_json(raw_response)

        if data is None:

            st.error(
                "The AI returned an invalid response. "
                "Please try generating again."
            )

            with st.expander("🔧 Debug: AI Response"):
                st.code(raw_response)

            return None

        if not validate_result(data):

            st.error(
                "The AI response was incomplete. "
                "Please try generating again."
            )

            with st.expander("🔧 Debug: AI Response"):
                st.json(data)

            return None

        return data

    except Exception as e:

        st.error(
            f"Generation failed: {str(e)}"
        )

        return None


# ============================================================
# GENERATE BUTTON
# ============================================================

generate = st.button(
    "✦ Generate LinkedIn Post",
    use_container_width=True
)


if generate:

    if not topic.strip():

        st.warning(
            "Please enter a topic before generating your post."
        )

    else:

        user_prompt = f"""
Create one LinkedIn post using the information below.

TOPIC:
{topic}

KEYWORDS:
{keywords if keywords.strip() else "None provided"}

IMPORTANT DETAILS:
{important_details if important_details.strip() else "None provided"}

POST TYPE:
{post_type}

TONE:
{tone}

WRITING STYLE:
{writing_style}

TARGET AUDIENCE:
{target_audience}

POST LENGTH:
{post_length}

EMOJIS:
{"Use emojis naturally where appropriate." if use_emojis else "Do not use emojis."}

HASHTAGS:
{"Include 3–5 relevant hashtags." if use_hashtags else "Do not include hashtags."}

CTA:
{"End with a natural and relevant CTA." if use_cta else "Do not include a CTA."}

REMEMBER:

TONE and WRITING STYLE are independent settings. The hook and
the overall structure must clearly reflect BOTH the requested
TONE (attitude) and WRITING STYLE (sentence rhythm, pacing,
structure) — rewrite from scratch for this exact combination
rather than reusing a generic opening or structure.

Do not invent information.
"""

        with st.spinner(
            "Writing your LinkedIn post..."
        ):

            result = generate_post(
                user_prompt,
                tone,
                writing_style,
                target_audience,
                post_length,
                use_emojis,
                use_hashtags,
                use_cta
            )

        if result:

            st.session_state.generated_post = result
            st.session_state.last_topic = topic

            # New post → new widget key, so the text_area below
            # is forced to re-initialize with the new value
            # instead of Streamlit reusing the stale old one.
            st.session_state.generation_count += 1

            st.success(
                "✓ Your LinkedIn post is ready!"
            )


# ============================================================
# RESULT
# ============================================================

if st.session_state.generated_post:

    st.markdown("---")

    st.markdown(
        "## Your LinkedIn Post"
    )

    result = st.session_state.generated_post

    hook = result.get("hook", "")
    post = result.get("post", "")

    # ------------------------------------------------
    # HOOK
    # ------------------------------------------------

    safe_hook = html.escape(hook).replace("\n", "<br>")

    st.markdown(
        '<div class="post-card">'
        '<div class="hook-box">'
        '<div class="hook-label">Strong Hook</div>'
        f'<div class="hook-text">{safe_hook}</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------
    # EDITABLE POST
    # ------------------------------------------------

    edited_post = st.text_area(
        "Edit your post",
        value=post,
        height=430,
        key=f"post_editor_{st.session_state.generation_count}",
        label_visibility="visible"
    )

    # ------------------------------------------------
    # STATS
    # ------------------------------------------------

    word_count = len(
        edited_post.split()
    )

    character_count = len(
        edited_post
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Words",
            word_count
        )

    with col2:

        st.metric(
            "Characters",
            character_count
        )

    with col3:

        if character_count <= 3000:
            status = "Good length"
        else:
            status = "Long post"

        st.metric(
            "Status",
            status
        )

    # ------------------------------------------------
    # COPY / DOWNLOAD
    # ------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.code(
            edited_post,
            language=None
        )

    with col2:

        st.download_button(
            label="⬇️ Download Post",
            data=edited_post,
            file_name="linkedin_post.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_post"
        )

    # ------------------------------------------------
    # LINKEDIN PREVIEW
    # ------------------------------------------------

    st.markdown(
        "### LinkedIn Preview"
    )

    safe_post = html.escape(edited_post).replace("\n", "<br>")

    st.markdown(
        '<div class="linkedin-preview">'
        '<div class="linkedin-profile">'
        '<div class="profile-avatar">N</div>'
        '<div>'
        '<div class="profile-name">Noman Iftekhar</div>'
        '<div class="profile-role">Mechatronics Engineering • AI • Computer Vision</div>'
        '</div>'
        '</div>'
        f'<div class="preview-content">{safe_post}</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# EMPTY STATE
# ============================================================

else:

    st.markdown(
        '<div class="post-card" style="text-align:center; padding:3rem;">'
        '<h3>✦ Your post will appear here</h3>'
        '<p style="color:#94a3b8;">'
        'Enter a topic above and generate a LinkedIn post '
        'with a strong hook, shaped by your chosen tone '
        'and style.'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        LinkAI · AI-powered LinkedIn content generation
    </div>
    """,
    unsafe_allow_html=True
)
