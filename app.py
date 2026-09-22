import json
import re
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])


def extract_json(text):
    """Safely extract JSON object from AI response."""

    # Remove markdown code fences
    text = text.strip()
    text = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)

    # Find first { and last }
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return None

    json_text = text[start:end + 1]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return None


def generate_posts(prompt):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": """
You are an expert LinkedIn content writer.

Return ONLY valid JSON.
Do not write anything before or after the JSON.

The JSON must have exactly this structure:

{
  "variations": [
    {
      "title": "🔥 Scroll Stopper",
      "hook": "hook text",
      "post": "complete post"
    },
    {
      "title": "📖 Human Story",
      "hook": "hook text",
      "post": "complete post"
    },
    {
      "title": "💡 Insight & Authority",
      "hook": "hook text",
      "post": "complete post"
    }
  ]
}

IMPORTANT:
- Generate exactly 3 variations.
- Each variation must be genuinely different.
- Do not repeat the same opening.
- Do not use generic openings such as:
  "Today I am excited..."
  "I am thrilled..."
  "I recently..."
- Do not invent achievements, statistics, companies, technologies, or results.
- Keep the writing natural and human.
- The hook must be strong and specific.
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.9,
            max_tokens=3000
        )

        raw = response.choices[0].message.content

        data = extract_json(raw)

        if data is None:
            st.error("AI returned invalid JSON. Please try again.")
            with st.expander("Debug: AI Response"):
                st.code(raw)
            return None

        if "variations" not in data:
            st.error("AI response does not contain variations.")
            with st.expander("Debug: AI Response"):
                st.json(data)
            return None

        if len(data["variations"]) != 3:
            st.error("AI did not return exactly 3 variations.")
            with st.expander("Debug: AI Response"):
                st.json(data)
            return None

        # Validate each variation
        for variation in data["variations"]:
            if not all(
                key in variation
                for key in ["title", "hook", "post"]
            ):
                st.error("One of the generated variations is incomplete.")
                with st.expander("Debug: AI Response"):
                    st.json(data)
                return None

        return data

    except Exception as e:
        st.error(f"Generation error: {str(e)}")
        return None
