import streamlit as st
from groq import Groq
import json
import re
import html


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="LinkAI — LinkedIn Post Generator",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at top left,
            #13283d 0%,
            #07111d 35%,
            #050b12 100%
        );
    color: #f5f7fa;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* =========================================================
   HEADER
   ========================================================= */

.brand {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -1.8px;
}

.brand span {
    color: #4cc9f0;
}

.subtitle {
    color: #9aa8b8;
    margin-top: -8px;
    margin-bottom: 25px;
}


/* =========================================================
   STATUS
   ========================================================= */

.status {
    display: inline-block;
    background: rgba(46, 204, 113, 0.12);
    border: 1px solid rgba(46, 204, 113, 0.30);
    color: #5be38b;
    padding: 7px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
}


/* =========================================================
   COMPOSER
   ========================================================= */

.composer {
    background: rgba(10, 24, 38, 0.90);
    border: 1px solid rgba(76, 201, 240, 0.18);
    border-radius: 20px;
    padding: 25px;
    margin-top: 15px;
    box-shadow: 0 15px 45px rgba(0, 0, 0, 0.20);
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button {
    border-radius: 12px;
    border: none;
    font-weight: 700;
    min-height: 45px;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(
        90deg,
        #168aad,
        #4cc9f0
    );
    color: white;
}


/* =========================================================
   INPUTS
   ========================================================= */

textarea {
    background-color: #091522 !important;
    color: white !important;
    border-radius: 12px !important;
}

input {
    background-color: #091522 !important;
    color: white !important;
}


/* =========================================================
   EXPANDER
   ========================================================= */

.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
}


/* =========================================================
   TABS
   ========================================================= */

button[data-baseweb="tab"] {
    color: #aebdca;
    font-weight: 600;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #4cc9f0;
}


/* =========================================================
   RESULT CARD
   ========================================================= */

.result-label {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    background: rgba(76, 201, 240, 0.10);
    border: 1px solid rgba(76, 201, 240, 0.20);
    color: #4cc9f0;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 8px;
}

.hook-card {
    background: rgba(76, 201, 240, 0.06);
    border-left: 3px solid #4cc9f0;
    padding: 14px 17px;
    border-radius: 10px;
    margin: 12px 0 18px 0;
}

.hook-title {
    color: #8ea2b5;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 5px;
}

.hook-text {
    color: #f2f7fa;
    font-size: 15px;
    line-height: 1.5;
}


/* =========================================================
   LINKEDIN PREVIEW
   ========================================================= */

.linkedin-preview {
    background: #ffffff;
    color: #222222;
    border-radius: 14px;
    padding: 22px;
    line-height: 1.6;
    margin-top: 10px;
}

.profile {
    font-weight: 700;
    margin-bottom: 3px;
}

.profile-sub {
    color: #666666;
    font-size: 13px;
    margin-bottom: 15px;
}

.preview-text {
    white-space: pre-wrap;
}


/* =========================================================
   EMPTY STATE
   ========================================================= */

.empty-state {
    background: rgba(12, 25, 39, 0.82);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    text-align: center;
    padding: 60px 20px;
    margin-top: 25px;
}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    text-align: center;
    color: #637386;
    margin-top: 45px;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# GROQ API
# =========================================================

try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error(
        "GROQ_API_KEY is not configured. "
        "Go to Streamlit Cloud → Settings → Secrets "
        "and add your Groq API key."
    )
    st.stop()

client = Groq(api_key=api_key)


# =========================================================
# SESSION STATE
# =========================================================

if "generated_variations" not in st.session_state:
    st.session_state.generated_variations = []

if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""


# =========================================================
# HEADER
# =========================================================

col1, col2 = st.columns([3, 1])

with col1:

    st.markdown(
        '<div class="brand">Link<span>AI</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'AI-powered LinkedIn Post Generator'
        '</div>',
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        '<div style="text-align:right; margin-top:10px;">'
        '<span class="status">● Groq AI Online</span>'
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# WRITING SETTINGS
# =========================================================

with st.expander("⚙️ Writing Settings", expanded=True):

    col1, col2, col3 = st.columns(3)

    with col1:

        post_type = st.selectbox(
            "Post Type",
            [
                "Project",
                "Internship",
                "Achievement",
                "Learning",
                "Career Update",
                "Technical",
                "Hackathon",
                "Certification",
                "Networking",
                "General"
            ]
        )

    with col2:

        tone = st.selectbox(
            "Tone",
            [
                "Professional",
                "Casual",
                "Storytelling",
                "Technical",
                "Inspirational",
                "Confident"
            ]
        )

    with col3:

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

    col1, col2, col3 = st.columns(3)

    with col1:

        audience = st.selectbox(
            "Target Audience",
            [
                "Recruiters",
                "Engineers",
                "Students",
                "Tech Professionals",
                "Entrepreneurs",
                "General LinkedIn Audience"
            ]
        )

    with col2:

        length = st.selectbox(
            "Post Length",
            [
                "Short",
                "Medium",
                "Long"
            ],
            index=1
        )

    with col3:

        emojis = st.toggle(
            "Include Emojis",
            value=True
        )

    col1, col2 = st.columns(2)

    with col1:

        hashtags = st.toggle(
            "Include Hashtags",
            value=True
        )

    with col2:

        cta = st.toggle(
            "Include Call-to-Action",
            value=True
        )


# =========================================================
# POST COMPOSER
# =========================================================

st.markdown(
    '<div class="composer">',
    unsafe_allow_html=True
)

st.markdown(
    "### ✦ What do you want to post about?"
)

topic = st.text_area(
    "Topic",
    placeholder=(
        "Example: I recently built an AI-powered "
        "Industrial Safety Monitoring system using "
        "YOLOv8 and OpenCV..."
    ),
    height=160,
    label_visibility="collapsed"
)


col1, col2 = st.columns(2)

with col1:

    keywords = st.text_input(
        "Keywords",
        placeholder=(
            "AI, YOLOv8, Computer Vision, OpenCV"
        )
    )

with col2:

    details = st.text_input(
        "Important Details",
        placeholder=(
            "What did you learn? What was difficult? "
            "What was the result?"
        )
    )


generate = st.button(
    "✦ Generate 3 Unique Variations",
    type="primary",
    use_container_width=True
)

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# GENERATION
# =========================================================

if generate:

    if not topic.strip():

        st.warning(
            "Please enter a topic first."
        )

        st.stop()


    # -----------------------------------------------------
    # LENGTH
    # -----------------------------------------------------

    length_instruction = {

        "Short":
            "around 80-120 words",

        "Medium":
            "around 150-220 words",

        "Long":
            "around 250-350 words"

    }[length]


    # -----------------------------------------------------
    # EMOJIS
    # -----------------------------------------------------

    if emojis:

        emoji_instruction = (
            "Use a maximum of 2-4 relevant emojis. "
            "Never put emojis in every paragraph."
        )

    else:

        emoji_instruction = (
            "Do not use emojis."
        )


    # -----------------------------------------------------
    # HASHTAGS
    # -----------------------------------------------------

    if hashtags:

        hashtag_instruction = (
            "Add 3-5 highly relevant hashtags at the end. "
            "Avoid generic hashtag spam."
        )

    else:

        hashtag_instruction = (
            "Do not include hashtags."
        )


    # -----------------------------------------------------
    # CTA
    # -----------------------------------------------------

    if cta:

        cta_instruction = (
            "End with a natural and relevant CTA. "
            "Do not automatically use 'What do you think?'"
        )

    else:

        cta_instruction = (
            "Do not include a call-to-action."
        )


    # =====================================================
    # MASTER PROMPT
    # =====================================================

    prompt = f"""
You are an elite LinkedIn content strategist,
copywriter, and personal-brand writer.

Your job is to transform the user's information into
THREE genuinely different LinkedIn posts.

IMPORTANT:

These must NOT be three paraphrases.

Each variation must have a completely different:

- Hook
- Opening
- Writing rhythm
- Structure
- Emotional angle
- Sentence patterns
- Reader benefit
- Ending

The posts should feel as if three different expert
LinkedIn writers created them.

=========================================================
USER INFORMATION
=========================================================

Topic:
{topic}

Post Type:
{post_type}

Tone:
{tone}

Selected Writing Style:
{writing_style}

Target Audience:
{audience}

Length:
{length_instruction}

Keywords:
{keywords}

Important Details:
{details}

=========================================================
CORE WRITING RULES
=========================================================

1. WRITE LIKE A REAL HUMAN.

The post should sound natural, specific and authentic.

Avoid robotic AI language.

Avoid excessive corporate language.

Avoid phrases such as:

"leveraging cutting-edge technology"
"revolutionizing the industry"
"game-changing solution"
"unlocking new possibilities"
"seamless integration"
"transformative journey"
"excited to announce"
"thrilled to share"
"happy to announce"

unless the user's information genuinely requires them.

=========================================================
2. HOOKS ARE THE HIGHEST PRIORITY
=========================================================

The first 1-2 lines must make the reader want to
continue reading.

Create three completely different hooks.

Possible hook approaches:

- Curiosity
- Contrarian idea
- Problem
- Surprising observation
- Specific challenge
- Personal realization
- Technical insight
- Strong statement
- Before/after contrast
- Unexpected lesson

Do NOT make generic announcement hooks.

NEVER start all three posts with:

"I recently..."
"I am excited..."
"I am thrilled..."
"Today..."
"I built..."
"I learned..."

Avoid starting every post with "I".

Each hook must work independently as a LinkedIn preview.

=========================================================
3. NO INVENTED INFORMATION
=========================================================

Only use information provided by the user.

Do NOT invent:

- achievements
- statistics
- numbers
- companies
- awards
- results
- users
- performance improvements
- technologies
- experiences

If a result was not provided, do not manufacture one.

=========================================================
VARIATION 1 — SCROLL STOPPER
=========================================================

Title:
Scroll Stopper

Purpose:

Make people stop scrolling.

Structure:

HOOK
↓
Interesting context/problem
↓
What happened / what was built
↓
Key insight
↓
Strong final line

Style:

- Bold
- Punchy
- Fast-paced
- Short paragraphs
- Strong contrast
- High curiosity

The opening should be the strongest part.

The post should feel modern and highly readable.

=========================================================
VARIATION 2 — HUMAN STORY
=========================================================

Title:
Human Story

Purpose:

Make the reader feel connected to the person behind
the project or experience.

Structure:

HOOK
↓
Situation / starting point
↓
Challenge
↓
Action
↓
Learning
↓
Reflection
↓
Natural ending

Style:

- Personal
- Conversational
- Authentic
- Warm
- Story-driven

Use "I" naturally but do not overuse it.

This should feel like someone telling a genuine story,
not writing a corporate announcement.

=========================================================
VARIATION 3 — INSIGHT & AUTHORITY
=========================================================

Title:
Insight & Authority

Purpose:

Give the reader a useful technical or professional
insight while naturally demonstrating the author's
knowledge.

Structure:

HOOK
↓
Interesting insight
↓
Technical/professional context
↓
What the author discovered
↓
Why it matters
↓
Practical takeaway
↓
Professional ending

Style:

- Intelligent
- Clear
- Technical where appropriate
- Insightful
- Value-driven

Do not simply describe the project.

Explain why the experience or lesson matters.

=========================================================
WRITING STYLE
=========================================================

The selected writing style is:

{writing_style}

Apply this style across all three variations,
but keep the three structural approaches different.

=========================================================
TARGET AUDIENCE
=========================================================

The target audience is:

{audience}

Write so this specific audience has a reason to care.

For example:

Recruiters:
Highlight skills, initiative, problem-solving and learning.

Engineers:
Highlight technical thinking, implementation and lessons.

Students:
Make the experience relatable and educational.

Tech Professionals:
Focus on useful technical insights and practical value.

Entrepreneurs:
Focus on problem-solving, value and real-world application.

General LinkedIn Audience:
Prioritize clarity, story and relatable lessons.

=========================================================
TONE
=========================================================

Use this tone:

{tone}

Do not let the tone make the three posts identical.

=========================================================
EMOJIS
=========================================================

{emoji_instruction}

=========================================================
HASHTAGS
=========================================================

{hashtag_instruction}

=========================================================
CALL TO ACTION
=========================================================

{cta_instruction}

=========================================================
FINAL QUALITY CHECK
=========================================================

Before returning the answer, internally check:

- Are the three hooks completely different?
- Are the three openings different?
- Are the three structures different?
- Are the three posts genuinely different?
- Does each post sound human?
- Is the first line interesting?
- Did I avoid generic AI language?
- Did I avoid invented information?
- Did I avoid repeating the same phrases?
- Does the selected audience have a reason to care?
- Does each ending feel natural?

If two posts feel too similar, rewrite one.

Do NOT output your analysis.

=========================================================
OUTPUT FORMAT
=========================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "variations": [
        {{
            "title": "🔥 Scroll Stopper",
            "hook": "Exact first 1-2 lines",
            "post": "Complete LinkedIn post"
        }},
        {{
            "title": "📖 Human Story",
            "hook": "Exact first 1-2 lines",
            "post": "Complete LinkedIn post"
        }},
        {{
            "title": "💡 Insight & Authority",
            "hook": "Exact first 1-2 lines",
            "post": "Complete LinkedIn post"
        }}
    ]
}}
"""


    # =====================================================
    # CALL GROQ
    # =====================================================

    with st.spinner(
        "Crafting three different LinkedIn voices..."
    ):

        try:

            response = client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                messages=[

                    {
                        "role": "system",
                        "content": (
                            "You are an elite LinkedIn copywriter. "
                            "Create highly differentiated posts. "
                            "Return valid JSON only."
                        )
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }

                ],

                temperature=0.95,

                max_tokens=3500
            )


            raw = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )


            # -------------------------------------------------
            # Clean markdown JSON fences
            # -------------------------------------------------

            raw = re.sub(
                r"```json\s*|\s*```",
                "",
                raw,
                flags=re.IGNORECASE
            ).strip()


            # -------------------------------------------------
            # Extract JSON if model adds extra text
            # -------------------------------------------------

            start = raw.find("{")
            end = raw.rfind("}")

            if start != -1 and end != -1:

                raw = raw[start:end + 1]


            # -------------------------------------------------
            # Parse
            # -------------------------------------------------

            data = json.loads(raw)


            variations = data.get(
                "variations",
                []
            )


            if len(variations) < 3:

                st.error(
                    "The AI returned fewer than three "
                    "variations. Please generate again."
                )

                st.stop()


            st.session_state.generated_variations = (
                variations[:3]
            )

            st.session_state.last_topic = topic


        except json.JSONDecodeError:

            st.error(
                "The AI returned an invalid response. "
                "Please click Generate again."
            )

            st.stop()


        except Exception as e:

            st.error(
                f"Generation error: {str(e)}"
            )

            st.stop()


# =========================================================
# RESULTS
# =========================================================

if st.session_state.generated_variations:

    st.markdown(
        "## ✦ Your LinkedIn Posts"
    )

    st.caption(
        "Three different approaches — not three simple rewrites."
    )


    variations = (
        st.session_state.generated_variations
    )


    # =====================================================
    # TABS
    # =====================================================

    tabs = st.tabs(
        [
            "🔥 Scroll Stopper",
            "📖 Human Story",
            "💡 Insight & Authority"
        ]
    )


    for i, tab in enumerate(tabs):

        if i >= len(variations):
            continue

        with tab:

            variation = variations[i]

            post = variation.get(
                "post",
                ""
            )

            hook = variation.get(
                "hook",
                ""
            )


            # ------------------------------------------------
            # Label
            # ------------------------------------------------

            titles = [
                "SCROLL STOPPER",
                "HUMAN STORY",
                "INSIGHT & AUTHORITY"
            ]

            st.markdown(
                f"""
                <div class="result-label">
                    {titles[i]}
                </div>
                """,
                unsafe_allow_html=True
            )


            # ------------------------------------------------
            # Hook
            # ------------------------------------------------

            safe_hook = html.escape(hook)

            st.markdown(
                f"""
                <div class="hook-card">

                    <div class="hook-title">
                        ⚡ Hook
                    </div>

                    <div class="hook-text">
                        {safe_hook}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


            # ------------------------------------------------
            # Editable Post
            # ------------------------------------------------

            edited_post = st.text_area(
                "Edit your post",
                value=post,
                height=390,
                key=f"post_editor_{i}"
            )


            # ------------------------------------------------
            # Statistics
            # ------------------------------------------------

            words = len(
                edited_post.split()
            )

            characters = len(
                edited_post
            )


            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Words",
                    words
                )


            with col2:

                st.metric(
                    "Characters",
                    characters
                )


            with col3:

                st.download_button(
                    "⬇ Download",
                    data=edited_post,
                    file_name=(
                        f"linkedin_post_{i + 1}.txt"
                    ),
                    mime="text/plain",
                    key=f"download_{i}"
                )


            # ------------------------------------------------
            # LinkedIn Preview
            # ------------------------------------------------

            st.markdown(
                "### LinkedIn Preview"
            )


            safe_preview = (
                html.escape(edited_post)
                .replace("\n", "<br>")
            )


            st.markdown(
                f"""
                <div class="linkedin-preview">

                    <div class="profile">
                        Noman Iftekhar
                    </div>

                    <div class="profile-sub">
                        Mechatronics Engineering •
                        AI • Computer Vision
                    </div>

                    <div class="preview-text">
                        {safe_preview}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# EMPTY STATE
# =========================================================

else:

    st.markdown(
        """
        <div class="empty-state">

            <div style="font-size:48px;">
                ✦
            </div>

            <h2>
                Create better LinkedIn posts
            </h2>

            <p style="color:#8d9bab;">
                Enter your idea and LinkAI will create
                three genuinely different versions:
                a scroll stopper, a human story,
                and an insight-driven post.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        LinkAI • AI-powered LinkedIn Content Creation
    </div>
    """,
    unsafe_allow_html=True
)
