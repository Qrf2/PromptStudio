import logging
from typing import List, Dict
import models_config as mc
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define dynamic prompt styles
PROMPT_STYLES = ["Concise", "Detailed", "Structured", "Creative"]

def generate_prompts(rough_prompt: str, creativity_level: int) -> List[Dict]:
    """
    Generates multiple prompt versions from a rough prompt idea.
    
    Args:
        rough_prompt: The rough prompt idea.
        creativity_level: Creativity level (1-10) to adjust novelty.
    
    Returns:
        A list of dictionaries with prompt IDs, styles, and texts.
    """
    logger.info(f"Generating prompts for: {rough_prompt}, creativity: {creativity_level}")
    
    creativity_modifier = "highly creative and innovative" if creativity_level > 7 else "moderately creative" if creativity_level > 4 else "clear and straightforward"
    meta_prompt = f"""
You are an expert prompt engineering team tasked with creating 4 professional prompt versions for the rough prompt idea '{rough_prompt}'. Each prompt must have a distinct style: Concise, Detailed, Structured, and Creative. Ensure the prompts are {creativity_modifier}, relevant to the topic, and optimized for clarity and effectiveness. Return the prompts in the following format, with each prompt labeled:

1. **Concise**: A short, direct prompt (50-100 words).
2. **Detailed**: A comprehensive prompt (150-200 words) with specific instructions.
3. **Structured**: A prompt (100-150 words) using bullet points or numbered steps.
4. **Creative**: A novel, engaging prompt (100-150 words) with a unique angle.

Example for rough prompt 'Write a blog about AI trends':
1. **Concise**: Write a 500-word blog on key AI trends in 2025, focusing on industry impacts.
2. **Detailed**: Write a 1000-word blog exploring AI trends in 2025, including case studies, data, and predictions, in a professional tone for tech executives.
3. **Structured**: Write a 750-word blog on AI trends, covering:
   - Current advancements
   - Industry applications
   - Future outlook
4. **Creative**: Craft a 600-word blog as a futuristic AI narrating 2025 trends, blending humor and insight.

Generate the 4 prompts for '{rough_prompt}'.
"""
    
    try:
        client = mc.get_model_client(list(mc.MODEL_CONFIG.keys())[0])
        response = client.complete(meta_prompt)
        logger.info(f"Received raw response: {response[:100]}...")

        # Parse response into structured prompts
        prompts = []
        for idx, style in enumerate(PROMPT_STYLES, 1):
            start_marker = f"**{style}**:"
            end_marker = f"**{PROMPT_STYLES[(idx % len(PROMPT_STYLES))]}**:" if idx < len(PROMPT_STYLES) else None
            start_idx = response.find(start_marker) + len(start_marker)
            end_idx = response.find(end_marker) if end_marker else len(response)
            prompt_text = response[start_idx:end_idx].strip()
            
            if prompt_text:
                prompts.append({"id": idx, "style": style, "prompt": prompt_text})
            else:
                logger.warning(f"Failed to parse prompt for {style}")
                prompts.append({"id": idx, "style": style, "prompt": f"Error: Could not generate {style} prompt."})

        return prompts

    except Exception as e:
        logger.error(f"Error generating prompts: {str(e)}")
        raise

def test_prompt(prompt: str, model: str, iterations: int) -> str:
    """
    Tests a prompt by sending it to the specified model.
    
    Args:
        prompt: The prompt to test.
        model: The OpenRouter model.
        iterations: Number of test runs.
    
    Returns:
        Aggregated test output.
    """
    logger.info(f"Testing prompt: {prompt[:50]}..., iterations: {iterations}")
    try:
        client = mc.get_model_client(model)
        outputs = []
        for i in range(iterations):
            output = client.complete(prompt)
            outputs.append(f"Iteration {i+1}: {output}")
        return "\n".join(outputs)
    except Exception as e:
        logger.error(f"Error testing prompt: {str(e)}")
        raise

def score_output(output: str, prompt: str) -> int:
    """
    Scores the output based on clarity, relevance, and length.
    
    Args:
        output: The model output.
        prompt: The original prompt.
    
    Returns:
        A score from 0 to 100.
    """
    score = 0
    
    # Clarity (0-40): Check for coherence and readability
    if len(output.split()) > 10 and len(re.findall(r'[.!?]', output)) > 1:
        score += 30
    if not re.search(r'\b(lorem|ipsum|error)\b', output.lower()):
        score += 10

    # Relevance (0-40): Check if output aligns with prompt keywords
    prompt_keywords = set(re.findall(r'\w+', prompt.lower()))
    output_keywords = set(re.findall(r'\w+', output.lower()))
    common_keywords = len(prompt_keywords.intersection(output_keywords))
    if common_keywords / max(len(prompt_keywords), 1) > 0.5:
        score += 30
    elif common_keywords > 0:
        score += 20

    # Length (0-20): Penalize overly short or long outputs
    word_count = len(output.split())
    if 50 <= word_count <= 500:
        score += 20
    elif 20 <= word_count < 50 or 500 < word_count <= 1000:
        score += 10

    logger.info(f"Scored output: {score}/100")
    return min(score, 100)

def refine_prompt(prompt: str, output: str, score: int) -> str:
    """
    Refines the highest-scoring prompt based on test output and score.
    
    Args:
        prompt: The original prompt.
        output: The test output.
        score: The prompt's score.
    
    Returns:
        The refined prompt.
    """
    logger.info(f"Refining prompt: {prompt[:50]}..., score: {score}")
    
    refinements = []
    if score < 80:
        refinements.append("Add more specific instructions for clarity.")
    if len(output.split()) < 50:
        refinements.append("Increase the expected output length.")
    if not re.search(r'\b(tone|style|audience)\b', prompt.lower()):
        refinements.append("Specify tone and target audience.")

    meta_prompt = f"""
You are an expert prompt engineer tasked with refining the following prompt to improve its clarity, specificity, and effectiveness. Original prompt: '{prompt}'. Test output: '{output[:200]}...'. Score: {score}/100. Suggested refinements: {', '.join(refinements) or 'None'}. Return the refined prompt.
"""
    
    try:
        client = mc.get_model_client(list(mc.MODEL_CONFIG.keys())[0])
        refined_prompt = client.complete(meta_prompt)
        logger.info(f"Refined prompt: {refined_prompt[:50]}...")
        return refined_prompt.strip()
    except Exception as e:
        logger.error(f"Error refining prompt: {str(e)}")
        return prompt  # Fallback to original prompt

def generate_report(rough_prompt: str, prompts: List[Dict], refined_prompt: str) -> str:
    """
    Generates a detailed report of the PromptStudio process.
    
    Args:
        rough_prompt: The original rough prompt.
        prompts: List of generated prompts with test outputs and scores.
        refined_prompt: The refined prompt.
    
    Returns:
        The report text.
    """
    logger.info("Generating report...")
    
    report = f"""
PromptStudio Report
==================
Generated: {datetime.now().isoformat()}
Original Rough Prompt: {rough_prompt}

1. Generated Prompts
-------------------
"""
    for prompt_data in prompts:
        report += f"""
Prompt {prompt_data['id']} ({prompt_data['style']}):
{prompt_data['prompt']}

Test Output:
{prompt_data['output'][:500]}...

Score: {prompt_data['score']}/100
"""

    report += f"""
2. Refined Prompt
----------------
{refined_prompt}

3. Summary
----------
Processed {len(prompts)} prompts with styles: {', '.join(p['style'] for p in prompts)}.
Highest score: {max(p['score'] for p in prompts)}/100.
Refinement improved the best prompt based on test feedback.
==================
"""
    
    return report

def run_studio(rough_prompt: str, creativity_level: int, model: str, iterations: int) -> Dict:
    """
    Runs the full PromptStudio pipeline: generate, test, score, refine, document.
    
    Args:
        rough_prompt: The rough prompt idea.
        creativity_level: Creativity level (1-10).
        model: The OpenRouter model.
        iterations: Number of test iterations.
    
    Returns:
        A dictionary with prompts, refined prompt, and report.
    """
    logger.info(f"Running PromptStudio for: {rough_prompt}")
    
    # Generate prompts
    prompts = generate_prompts(rough_prompt, creativity_level)
    
    # Test and score prompts
    for prompt_data in prompts:
        try:
            output = test_prompt(prompt_data['prompt'], model, iterations)
            prompt_data['output'] = output
            prompt_data['score'] = score_output(output, prompt_data['prompt'])
        except Exception as e:
            prompt_data['output'] = f"Error: {str(e)}"
            prompt_data['score'] = 0
            logger.error(f"Error testing prompt {prompt_data['id']}: {str(e)}")

    # Refine the best prompt
    best_prompt = max(prompts, key=lambda p: p['score'], default=prompts[0])
    refined_prompt = refine_prompt(best_prompt['prompt'], best_prompt['output'], best_prompt['score'])

    # Generate report
    report = generate_report(rough_prompt, prompts, refined_prompt)

    return {
        "prompts": prompts,
        "refined_prompt": refined_prompt,
        "report": report
    }