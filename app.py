import streamlit as st
from groq import Groq
import json
import re


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
    font-size: 40px;
    font-weight: 800;
    letter-spacing: -1.5px;
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
   CARDS
   ========================================================= */

.card {
    background: rgba(12, 25, 39, 0.82);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.25);
}


/* =========================================================
   COMPOSER
   ========================================================= */

.composer {
    background: rgba(10, 24, 38, 0.90);
    border: 1px solid rgba(76,201,240,0.18);
    border-radius: 20px;
    padding: 25px;
    margin-top: 15px;
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
   TEXT AREAS
   ========================================================= */

textarea {
    background-color: #091522 !important;
    color: white !important;
    border-radius: 12px !important;
}


/* =========================================================
   INPUTS
   ========================================================= */

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
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #4cc9f0;
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
        "Add it in Streamlit Cloud → Settings → Secrets."
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

with st.expander("⚙️ Writing Settings"):

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


    col1, col2, col3 = st.columns(3)

    with col1:

        length = st.selectbox(
            "Post Length",
            [
                "Short",
                "Medium",
                "Long"
            ]
        )

    with col2:

        hashtags = st.toggle(
            "Include Hashtags",
            value=True
        )

    with col3:

        emojis = st.toggle(
            "Include Emojis",
            value=True
        )

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
        "Example: I recently completed an AI Resume "
        "Analyzer using Python, Streamlit and NLP..."
    ),
    height=150,
    label_visibility="collapsed"
)


col1, col2 = st.columns(2)

with col1:

    keywords = st.text_input(
        "Keywords",
        placeholder=(
            "AI, Python, Streamlit, Computer Vision"
        )
    )


with col2:

    details = st.text_input(
        "Important Details",
        placeholder=(
            "What did you learn? What was the result?"
        )
    )


generate = st.button(
    "✦ Generate 3 Variations",
    type="primary",
    use_container_width=True
)


st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# GENERATE POSTS
# =========================================================

if generate:

    if not topic.strip():

        st.warning(
            "Please enter a topic first."
        )

        st.stop()


    # Length instructions

    length_instruction = {

        "Short":
            "around 80-120 words",

        "Medium":
            "around 150-220 words",

        "Long":
            "around 250-350 words"

    }[length]


    # Emoji instructions

    if emojis:

        emoji_instruction = (
            "Use a few relevant emojis naturally."
        )

    else:

        emoji_instruction = (
            "Do not use emojis."
        )


    # Hashtag instructions

    if hashtags:

        hashtag_instruction = (
            "Include 3-6 relevant LinkedIn hashtags "
            "at the end."
        )

    else:

        hashtag_instruction = (
            "Do not include hashtags."
        )


    # CTA instructions

    if cta:

        cta_instruction = (
            "End with a natural call-to-action "
            "or question."
        )

    else:

        cta_instruction = (
            "Do not add a call-to-action."
        )


    # =====================================================
    # AI PROMPT
    # =====================================================

    prompt = f"""
You are an expert LinkedIn content writer.

Create THREE different LinkedIn post variations.

USER INFORMATION

Topic:
{topic}

Post Type:
{post_type}

Tone:
{tone}

Target Audience:
{audience}

Keywords:
{keywords}

Important Details:
{details}

Length:
{length_instruction}

INSTRUCTIONS

1. Make the posts natural and human.
2. Avoid generic AI-sounding phrases.
3. Do not start every variation the same way.
4. Make each variation substantially different.
5. {emoji_instruction}
6. {hashtag_instruction}
7. {cta_instruction}
8. Do not invent achievements, numbers, organizations,
   technologies, or results that the user did not provide.
9. Keep the content suitable for LinkedIn.
10. Return ONLY valid JSON.

JSON FORMAT:

{{
    "variations": [
        {{
            "title": "Professional",
            "post": "..."
        }},
        {{
            "title": "Storytelling",
            "post": "..."
        }},
        {{
            "title": "Engaging",
            "post": "..."
        }}
    ]
}}
"""


    # =====================================================
    # GROQ REQUEST
    # =====================================================

    with st.spinner(
        "Creating your LinkedIn posts..."
    ):

        try:

            response = client.chat.completions.create(

                model="openai/gpt-oss-120b",

                messages=[

                    {
                        "role": "system",
                        "content":
                            "You are a professional LinkedIn "
                            "content writer. Return valid JSON only."
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }

                ],

                temperature=0.8,

                max_tokens=2500
            )


            raw = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )


            # Remove Markdown JSON fences

            raw = re.sub(
                r"```json\s*|\s*```",
                "",
                raw,
                flags=re.IGNORECASE
            ).strip()


            # Parse JSON

            data = json.loads(raw)


            variations = data.get(
                "variations",
                []
            )


            if not variations:

                st.error(
                    "The AI did not return any posts. "
                    "Please try again."
                )

                st.stop()


            st.session_state.generated_variations = variations

            st.session_state.last_topic = topic


        except json.JSONDecodeError:

            st.error(
                "The AI response was not valid JSON. "
                "Please click Generate again."
            )

            st.stop()


        except Exception as e:

            st.error(
                f"Generation error: {str(e)}"
            )

            st.stop()


# =========================================================
# DISPLAY RESULTS
# =========================================================

if st.session_state.generated_variations:

    st.markdown(
        "## ✦ Generated Posts"
    )


    variations = (
        st.session_state.generated_variations
    )


    # Create tabs

    tabs = st.tabs(
        [
            f"Variation {i + 1}"
            for i in range(len(variations))
        ]
    )


    for i, (tab, variation) in enumerate(
        zip(tabs, variations)
    ):

        with tab:

            title = variation.get(
                "title",
                f"Variation {i + 1}"
            )

            post = variation.get(
                "post",
                ""
            )


            st.markdown(
                f"### {title}"
            )


            edited_post = st.text_area(
                "Edit your post",
                value=post,
                height=360,
                key=f"post_{i}"
            )


            # Statistics

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


            # =================================================
            # LINKEDIN PREVIEW
            # =================================================

            st.markdown(
                "### LinkedIn Preview"
            )


            # Basic HTML escaping

            preview = (
                edited_post
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
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
                        {preview}
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
        <div class="card"
             style="text-align:center;
                    padding:60px 20px;">

            <div style="font-size:45px;">
                ✦
            </div>

            <h2>
                Your LinkedIn post will appear here
            </h2>

            <p style="color:#8d9bab;">
                Enter your topic above and generate
                three AI-powered LinkedIn variations.
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
        LinkAI • Powered by Groq AI
    </div>
    """,
    unsafe_allow_html=True
)
