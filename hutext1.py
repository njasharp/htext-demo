import streamlit as st
import os
import time
from groq import Groq

# Initialize Groq client with API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ_API_KEY not found in environment variables. Please set it and restart the app.")
    st.stop()

client = Groq(api_key=groq_api_key)

# Supported models
SUPPORTED_MODELS = {
    "Llama 3 8B": "llama3-8b-8192",
    "Llama 3.1 70B": "llama-3.1-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "Mixtral 8x7B": "mixtral-8x7b-32768",
    "Gemma 2 9B": "gemma2-9b-it",
    "LLaVA 1.5 7B": "llava-v1.5-7b-4096-preview"  # New model added
}

# Initialize temperature in session state
if "temperature" not in st.session_state:
    st.session_state["temperature"] = 0.7

# Function to query Groq with retry and temperature
def query_groq_with_retry(messages, model, temperature=None, retries=3):
    for attempt in range(retries):
        try:
            kwargs = {"messages": messages, "model": model}
            if temperature is not None:
                kwargs["temperature"] = temperature
            chat_completion = client.chat.completions.create(**kwargs)
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            if attempt < retries - 1:
                continue  # Retry if possible
            else:
                st.error(f"An error occurred after {retries} attempts: {e}")
                return ""

# Function to humanize AI-generated text using Groq API
def humanize_text(ai_text, selected_prompt, model_id, temperature):
    prompt = f"{selected_prompt}\n\nText to humanize:\n{ai_text}"
    messages = [{"role": "user", "content": prompt}]
    humanized_text = query_groq_with_retry(messages, model=model_id, temperature=temperature)
    return humanized_text

# Streamlit app
st.set_page_config(layout="wide", page_title="AI Text Humanizer")
st.image("p1.png")
st.sidebar.image("p2.png", width=200)
st.title("Humanizer")
st.write("Convert AI-generated text into human-like text using advanced humanization strategies.")

# Text input
ai_text = st.text_area("Enter AI-generated text here:", height=200)

# Model selection
st.sidebar.header("Model Selection")
selected_model = st.sidebar.selectbox("Select a model", list(SUPPORTED_MODELS.keys()))
model_id = SUPPORTED_MODELS[selected_model]

# Add temperature slider
st.sidebar.header("Model Settings")
st.session_state["temperature"] = st.sidebar.slider(
    "Set Model Temperature",
    min_value=0.0,
    max_value=1.0,
    value=st.session_state["temperature"],
    step=0.1,
    key="temperature_slider"
)
temperature = st.session_state["temperature"]

# Select two humanization approaches
st.sidebar.header("Select Two Humanization Strategies:")
prompt_options = {
    "Approach 1 - Conversational Tone": """To humanize the prompt for a text-generative AI, you can make it more conversational and engaging. Here's how:

1. Start with a friendly greeting or introduction.
2. Use informal language and contractions.
3. Incorporate personal anecdotes or thoughts.
4. Ask open-ended questions to engage the reader.
5. Use emotive language to express feelings.

Text to humanize:""",
    "Approach 2 - Vary Sentence Structure": """To make the following text sound more natural and human-like:

1. Vary sentence length and structure.
2. Use contractions.
3. Add filler words or phrases.
4. Incorporate colloquialisms.
5. Include rhetorical questions.
6. Use active voice.

Text to humanize:""",
    "Approach 3 - Sensory Language": """Humanize the text by:

1. Using vivid sensory details.
2. Incorporating metaphors or similes.
3. Sharing personal experiences.
4. Expressing emotions openly.
5. Engaging the reader's imagination.

Text to humanize:""",
    "Approach 4 - Storytelling": """Transform the text by:

1. Framing it as a story.
2. Introducing characters or personas.
3. Building a narrative arc.
4. Including dialogue where appropriate.
5. Concluding with a personal reflection.

Text to humanize:""",
    "Approach 5 - Humor and Wit": """Make the text more human by:

1. Adding humorous observations.
2. Using witty remarks.
3. Incorporating light-hearted sarcasm.
4. Including relatable anecdotes.
5. Keeping the tone casual and fun.

Text to humanize:""",
}

approach_list = list(prompt_options.keys())
selected_option1 = st.sidebar.selectbox("Choose first approach:", approach_list, key='approach1')
selected_option2 = st.sidebar.selectbox("Choose second approach:", approach_list, key='approach2')
selected_prompt1 = prompt_options[selected_option1]
selected_prompt2 = prompt_options[selected_option2]

# Humanize text when button is clicked
if st.button("Humanize Text"):
    if ai_text.strip() == "":
        st.warning("Please enter AI-generated text to humanize.")
    else:
        with st.spinner("Humanizing text..."):
            humanized_text1 = humanize_text(ai_text, selected_prompt1, model_id, temperature)
            humanized_text2 = humanize_text(ai_text, selected_prompt2, model_id, temperature)
        if humanized_text1 and humanized_text2:
            st.subheader("Humanized Texts:")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"### {selected_option1}")
                st.write(humanized_text1)
                st.code(humanized_text1)
                st.text_area("Export Text", value=humanized_text1, height=200)

            with col2:
                st.markdown(f"### {selected_option2}")
                st.write(humanized_text2)
                st.code(humanized_text2)
                st.text_area("Export Text", value=humanized_text2, height=200)
        else:
            st.error("Failed to humanize the text. Please try again.")

# Footer
st.markdown("<div style='text-align: center; color: grey;'>Powered by Groq</div>", unsafe_allow_html=True)
st.info("built by dw 9-19-24")
