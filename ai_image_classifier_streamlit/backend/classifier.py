"""
Cloud-only: Groq mode
"""
import base64
import io
import json
import os
from typing import Dict
from PIL import Image
from groq import Groq
from dotenv import load_dotenv
from .prompts import CLASSIFIER_PROMPT, DEFAULT_LABELS

load_dotenv()

class ImageClassifier:
    def __init__(self, mode: str = "groq", labels=None):
        self.mode = mode.lower()
        self.labels = labels or DEFAULT_LABELS
        self.label_str = ", ".join(self.labels)

        if self.mode != "groq":
            self.mode = "groq"  # Force Groq in cloud

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY missing in secrets")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.2-11b-vision-preview"

    def _preprocess(self, image_bytes: bytes) -> Image.Image:
        if len(image_bytes) > 5 * 1024 * 1024:
            raise ValueError("Image > 5MB")
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img.thumbnail((1024, 1024))
        return img

    def _encode(self, img: Image.Image) -> str:
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode()

    def classify(self, image_bytes: bytes) -> Dict:
        img = self._preprocess(image_bytes)
        img_b64 = self._encode(img)
        prompt = CLASSIFIER_PROMPT.format(labels=self.label_str)

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }],
                temperature=0.1,
                max_tokens=100
            )
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            return {"label": "error", "confidence": 0.0, "reason": f"Groq: {e}"}
