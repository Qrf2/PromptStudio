PromptStudio: Autonomous Prompt Engineering System
PromptStudio is a professional prompt engineering system that takes a rough prompt idea and autonomously generates, tests, scores, refines, and documents multiple prompt versions. Built with a sleek Streamlit UI, it uses OpenRouter's free-tier model (LLaMA 3.1 8B Instruct) to deliver a full feedback loop, making it 10X smarter than simple prompt generators.
Features

Prompt Generation: Creates 4 prompt versions with dynamic styles (Concise, Detailed, Structured, Creative).
Testing: Tests each prompt with OpenRouter, producing real outputs.
Scoring: Evaluates outputs based on clarity, relevance, and length (0–100 scale).
Refinement: Improves the best prompt using test feedback.
Documentation: Generates a detailed TXT report with all steps.
Modern UI: Streamlit-based interface with Tailwind CSS.

Installation

Clone the repository:
git clone https://github.com/yourusername/promptstudio.git
cd promptstudio


Install dependencies:
pip install streamlit requests python-dotenv


Set up your OpenRouter API key in a .env file in the project root:
OPENROUTER_API_KEY=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


Run the app:
streamlit run app.py



Usage

Open the app in your browser (default: http://localhost:8501).
In the sidebar, select the OpenRouter model, creativity level, and test iterations.
Enter a rough prompt idea (e.g., 'Write a blog about AI trends').
Click "Run Studio" to generate, test, score, and refine prompts.
View generated prompts, test outputs, scores, and the refined prompt.
Download the report as a TXT file.

Troubleshooting

401 Unauthorized Error:
Ensure the .env file is in the promptstudio/ directory and contains the correct API key.
Verify your API key at OpenRouter's dashboard.
Run pip install python-dotenv to load the .env file.
Restart the app after updating the .env file.


Rate Limits:
The free tier has strict rate limits. Wait a few minutes if you hit limits.
Check OpenRouter's status page for issues.


API Key Validation:
The app tests the API key on startup. Check terminal logs for errors if it fails.



File Structure

app.py: Main Streamlit application with the UI and core logic.
prompt_engine.py: Prompt generation, testing, scoring, refining, and reporting logic.
models_config.py: OpenRouter model configurations and client initialization.
README.md: Project documentation.

Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub. Ensure your code follows PEP 8 and includes tests where applicable.
License
MIT License. See LICENSE for details.
