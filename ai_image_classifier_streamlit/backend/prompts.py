"""
Prompt template for zero-shot image classification.
Ensures model outputs structured JSON with label, confidence, and reason.
"""

# Default labels for classification (customize in UI)
DEFAULT_LABELS = [
    "cat", "dog", "car", "tree", "person", "food", "house", "airplane"
]

# Strict prompt to enforce JSON output and prevent hallucination
CLASSIFIER_PROMPT = """
You are an expert image classifier. Analyze the image and select exactly ONE label from the list below.
Do not invent new labels. If uncertain, choose the closest match.

Available labels: {labels}

Respond ONLY in this exact JSON format (no extra text, no markdown):
{{"label": "chosen_label", "confidence": 0.95, "reason": "Brief explanation based on visual features."}}

Image analysis begins now.
"""