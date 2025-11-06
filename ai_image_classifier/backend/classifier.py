"""
Core classification logic.
Supports:
  - Ollama (local, private): Uses LLaVA model
  - Groq (cloud, fast): Uses Llama 3.2 11B Vision

Features:
  - Image validation (size, format)
  - Auto-resize for efficiency
  - Base64 encoding for API
  - JSON response parsing with fallback
"""

import base64
import io
import json
import os
from typing import Dict, List, Optional
from PIL import Image
import ollama
from groq import Groq
from dotenv import load_dotenv
from .prompts import CLASSIFIER_PROMPT, DEFAULT_LABELS

# Load environment variables (for Groq API key)
load_dotenv()

class ImageClassifier:
    def __init__(self, mode: str = "ollama", labels: Optional[List[str]] = None):
        """
        Initialize classifier with mode and custom labels.
        
        Args:
            mode (str): "ollama" for local, "groq" for cloud
            labels (List[str], optional): Custom classification labels
        """
        self.mode = mode.lower()
        self.labels = labels or DEFAULT_LABELS
        self.label_str = ", ".join(self.labels)

        # Setup Groq client if in cloud mode
        if self.mode == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in .env file")
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.2-11b-vision-preview"  # Fast vision model

    def _preprocess_image(self, image_bytes: bytes) -> Image.Image:
        """
        Validate and preprocess image.
        - Rejects files > 5MB
        - Converts to RGB
        - Resizes to max 1024px per side
        """
        if len(image_bytes) > 5 * 1024 * 1024:
            raise ValueError("Image exceeds 5MB limit")
        
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.thumbnail((1024, 1024))  # Reduce compute & memory
            return img
        except Exception as e:
            raise ValueError(f"Invalid or corrupted image: {e}")

    def _encode_image(self, img: Image.Image) -> str:
        """
        Convert PIL image to base64 string (used by both backends).
        """
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode()

    def _classify_ollama(self, img: Image.Image) -> Dict:
        """
        Run inference using local Ollama + LLaVA.
        Requires: `ollama serve` and `ollama pull llava`
        """
        img_b64 = self._encode_image(img)
        prompt = CLASSIFIER_PROMPT.format(labels=self.label_str)

        try:
            response = ollama.chat(
                model="llava",  # ← Use vision model
                messages=[{"role": "user", "content": prompt, "images": [img_b64]}]
                )
            raw_text = response["message"]["content"]
            return json.loads(raw_text)
        except json.JSONDecodeError:
            return {"label": "unknown", "confidence": 0.0, "reason": "Failed to parse model output"}
        except Exception as e:
            return {"label": "error", "confidence": 0.0, "reason": f"Ollama error: {e}"}

    def _classify_groq(self, img: Image.Image) -> Dict:
        """
        Run inference using Groq cloud API.
        Fast, rate-limited (free tier: ~30 req/min).
        """
        img_b64 = self._encode_image(img)
        prompt = CLASSIFIER_PROMPT.format(labels=self.label_str)

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                        }
                    ]
                }],
                temperature=0.1,   # Low for consistency
                max_tokens=100     # Short JSON response
            )
            raw_text = completion.choices[0].message.content
            return json.loads(raw_text)
        except json.JSONDecodeError:
            return {"label": "unknown", "confidence": 0.0, "reason": "Failed to parse model output"}
        except Exception as e:
            return {"label": "error", "confidence": 0.0, "reason": f"Groq API error: {e}"}

    def classify(self, image_bytes: bytes) -> Dict:
        """
        Public method: Preprocess → classify → return JSON result.
        """
        img = self._preprocess_image(image_bytes)
        if self.mode == "ollama":
            return self._classify_ollama(img)
        else:
            return self._classify_groq(img)