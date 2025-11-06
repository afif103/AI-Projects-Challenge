"""
Cloud-only Groq via LangChain
"""
import base64
import io
import json
import os
from typing import Dict, List, Optional
from PIL import Image
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from dotenv import load_dotenv
from .prompts import CLASSIFIER_PROMPT, DEFAULT_LABELS

load_dotenv()

class ImageClassifier:
    def __init__(self, mode: str = "groq", labels: Optional[List[str]] = None):
        self.mode = mode.lower()
        self.labels = labels or DEFAULT_LABELS
        self.label_str = ", ".join(self.labels)

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY missing in secrets")

        self.llm = ChatGroq(
            model="llama-3.2-11b-vision-preview",
            api_key=api_key,
            temperature=0.1,
            max_tokens=100
        )

    def _preprocess_image(self, image_bytes: bytes) -> Image.Image:
        if len(image_bytes) > 5 * 1024 * 1024:
            raise ValueError("Image > 5MB")
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img.thumbnail((1024, 1024))
        return img

    def classify(self, image_bytes: bytes) -> Dict:
        img = self._preprocess_image(image_bytes)
        
        # Encode image for LangChain
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()

        prompt = CLASSIFIER_PROMPT.format(labels=self.label_str)

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                }
            ]
        )

        try:
            response = self.llm.invoke([message])
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"label": "unknown", "confidence": 0.0, "reason": "Parse failed"}
        except Exception as e:
            return {"label": "error", "confidence": 0.0, "reason": f"LangChain Groq: {e}"}
