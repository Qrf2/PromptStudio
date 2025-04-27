import streamlit as st
import prompt_engine as pe
import models_config as mc
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Streamlit page configuration
st.set_page_config(
    page_title="PromptStudio: Autonomous Prompt Engineering System",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    """Main function to run the PromptStudio Streamlit app."""
    # Custom CSS for Tailwind-like styling
    st.markdown("""
        <style>
        @import url('https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css');
        .main-header { @apply text-4xl font-bold text-gray-800 mb-6; }
        .sub-header { @apply text-2xl font-semibold text-gray-700 mb-4; }
        .card { @apply bg-white p-6 rounded-lg shadow-md mb-4; }
        .button { @apply bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600; }
        .input-box { @apply border border-gray-300 p-2 rounded w-full mb-4; }
        .sidebar-section { @apply mb-6; }
        .result-box { @apply bg-gray-100 p-4 rounded-lg mb-4; }
        </style>
    """, unsafe_allow_html=True)

    # Validate API key
    try:
        api_valid = mc.validate_api_keys()
        if not api_valid:
            st.error("Invalid or missing OpenRouter API key. Please ensure it is set correctly in the `.env` file.")
            st.markdown("1. Verify your API key in `promptstudio/.env`: `OPENROUTER_API_KEY=sk-or-v1-...`")
            st.markdown("2. Get a free key from [OpenRouter](https://openrouter.ai/keys).")
            st.markdown("3. Restart the app after updating the `.env` file.")
            return
    except Exception as e:
        st.error(f"Failed to validate OpenRouter API key: {str(e)}")
        st.markdown("Check your API key and internet connection, then restart the app.")
        logger.error(f"API key validation error: {str(e)}")
        return

    # Sidebar
    with st.sidebar:
        st.markdown('<h2 class="sub-header">PromptStudio Controls</h2>', unsafe_allow_html=True)
        model_choice = st.selectbox(
            "Select OpenRouter Model",
            list(mc.MODEL_CONFIG.keys()),
            help="Choose the model to test prompts."
        )
        creativity_level = st.slider(
            "Creativity Level", 1, 10, 5, help="Higher values produce more novel prompts."
        )
        test_iterations = st.slider(
            "Test Iterations", 1, 3, 1, help="Number of test runs per prompt (limited for free tier)."
        )
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.info("Enter a rough prompt idea, and PromptStudio will generate, test, score, refine, and document multiple versions.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Main content
    st.markdown('<h1 class="main-header">PromptStudio: Autonomous Prompt Engineering System</h1>', unsafe_allow_html=True)
    st.markdown("Input a rough prompt idea, and PromptStudio will generate, test, score, refine, and document professional prompt versions.", unsafe_allow_html=True)

    # Input section
    col1, col2 = st.columns([3, 1])
    with col1:
        rough_prompt = st.text_area(
            "Enter Your Rough Prompt Idea",
            height=100,
            placeholder="e.g., 'Write a blog about AI trends', 'Create a sales email', 'Tell a story about space'",
            help="Input a rough prompt idea to process.",
            key="prompt_input"
        )
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if st.button("Run Studio", key="run_button", help="Generate, test, score, refine, and document prompts"):
            if not rough_prompt:
                st.error("Please enter a rough prompt idea.")
            else:
                with st.spinner("Running PromptStudio..."):
                    try:
                        # Run the full PromptStudio pipeline
                        results = pe.run_studio(rough_prompt, creativity_level, model_choice, test_iterations)
                        logger.info(f"PromptStudio completed: {len(results['prompts'])} prompts processed")

                        # Store results in session state
                        st.session_state['results'] = results
                        st.session_state['rough_prompt'] = rough_prompt

                    except Exception as e:
                        logger.error(f"Error running PromptStudio: {str(e)}")
                        st.error(f"Error running PromptStudio: {str(e)}")

    # Display results
    if 'results' in st.session_state and st.session_state['results']:
        results = st.session_state['results']

        # Generated Prompts
        st.markdown('<h2 class="sub-header">Generated Prompts</h2>', unsafe_allow_html=True)
        for prompt_data in results['prompts']:
            st.markdown(f'<h3>Prompt {prompt_data["id"]} ({prompt_data["style"]})</h3>', unsafe_allow_html=True)
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.write(prompt_data["prompt"])
            st.markdown('</div>', unsafe_allow_html=True)

        # Test Results and Scores
        st.markdown('<h2 class="sub-header">Test Results and Scores</h2>', unsafe_allow_html=True)
        for prompt_data in results['prompts']:
            st.markdown(f'<h3>Prompt {prompt_data["id"]} ({prompt_data["style"]}) - Score: {prompt_data["score"]}/100</h3>', unsafe_allow_html=True)
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.write(f"Test Output:\n{prompt_data['output']}")
            st.markdown('</div>', unsafe_allow_html=True)

        # Refined Prompt
        st.markdown('<h2 class="sub-header">Refined Prompt</h2>', unsafe_allow_html=True)
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.write(results['refined_prompt'])
        st.markdown('</div>', unsafe_allow_html=True)

        # Download Report
        report_text = results['report']
        st.download_button(
            label="Download Report",
            data=report_text,
            file_name=f"promptstudio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            key="download_button"
        )

if __name__ == "__main__":
    main()