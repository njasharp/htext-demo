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
def humanize_text(ai_text, selected_prompt, tone_prompt, model_id, temperature):
    prompt = f"{selected_prompt}\n\nTone: {tone_prompt}\n\nText to humanize:\n{ai_text}"
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
selected_model = st.sidebar.selectbox("Select a model", list(SUPPORTED_MODELS.keys()), index=0)
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
    "Approach 1 - Conversational Tone": """To humanize the text, make it more conversational and engaging by:

1. Starting with a friendly greeting or introduction.
2. Using informal language and contractions.
3. Incorporating personal anecdotes or thoughts.
4. Asking open-ended questions to engage the reader.
5. Using emotive language to express feelings.

Text to humanize:""",
    "Approach 2 - Vary Sentence Structure": """To make the text sound more natural and human-like:

1. Vary sentence length and structure.
2. Use contractions.
3. Add filler words or phrases.
4. Incorporate colloquialisms.
5. Include rhetorical questions.
6. Use active voice.

Text to humanize:""",
    # ... (Approaches 3 to 15 are included here) ...
    "Approach 15 - Visual Language": """Enhance imagery by:

1. Using vivid descriptions to engage the senses.
2. Employing symbolism to represent ideas.
3. Creating mental images to help the reader visualize concepts.
4. Using descriptive analogies for complex ideas.
5. Incorporating color and texture descriptions for depth.

Text to humanize:""",
    # New Strategy Added Below
    "Approach 16 - Professional Business Tone": """Adopt a formal and professional tone suitable for business contexts by:

1. Using industry-specific terminology where appropriate.
2. Maintaining a clear and concise writing style.
3. Avoiding slang or overly casual language.
4. Focusing on facts and data to support statements.
5. Employing a confident and authoritative voice.

Text to humanize:""",
}

approach_list = list(prompt_options.keys())
selected_option1 = st.sidebar.selectbox("Choose first approach:", approach_list, key='approach1', index=0)
selected_option2 = st.sidebar.selectbox("Choose second approach:", approach_list, key='approach2', index=1)
selected_prompt1 = prompt_options[selected_option1]
selected_prompt2 = prompt_options[selected_option2]

# Tone options
st.sidebar.header("Select Tone:")
tone_options = {
    "Casual": "Just starting out in before primary school.",
    "Primary school": "Just starting out in primary school, learning the basics.",
    "Secondary school": "Moving up to secondary school, getting into more complex subjects.",
    "Higher education": "Higher education, diving deep into specialized fields.",
    "PhD level": "PhD level, becoming an expert in your chosen area.",
    "Business junior": "Starting your business journey as a junior, learning the ropes.",
    "Business senior": "Senior in the business world, taking on more responsibilities.",
    "Executive": "Executive level, leading and making big decisions."
}
tone_list = list(tone_options.keys())
selected_tone = st.sidebar.selectbox("Choose the tone level:", tone_list, index=3)  # Default to 'Higher education'
tone_prompt = tone_options[selected_tone]

# Humanize text when button is clicked
if st.button("Humanize Text"):
    if ai_text.strip() == "":
        st.warning("Please enter AI-generated text to humanize.")
    else:
        with st.spinner("Humanizing text..."):
            humanized_text1 = humanize_text(ai_text, selected_prompt1, tone_prompt, model_id, temperature)
            humanized_text2 = humanize_text(ai_text, selected_prompt2, tone_prompt, model_id, temperature)
        if humanized_text1 and humanized_text2:
            st.subheader("Humanized Texts:")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"### {selected_option1}")
                st.write(humanized_text1)
                st.code(humanized_text1)
                st.text_area("Export Text", value=humanized_text1, height=400)

            with col2:
                st.markdown(f"### {selected_option2}")
                st.write(humanized_text2)
                st.code(humanized_text2)
                st.text_area("Export Text", value=humanized_text2, height=400)
        else:
            st.error("Failed to humanize the text. Please try again.")

# Footer
st.markdown("<div style='text-align: center; color: grey;'>Powered by Groq</div>", unsafe_allow_html=True)
st.info("built by dw 9-19-24")
