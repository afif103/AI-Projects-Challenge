from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage
import json
import base64
import io
from PIL import Image
from dotenv import load_dotenv
import os
from .prompts import CLASSIFIER_PROMPT, DEFAULT_LABELS

load_dotenv()

class ImageClassifier:
    def __init__(self, mode="groq", labels=None):
        self.mode = "groq"  # Force cloud mode
        self.labels = labels or DEFAULT_LABELS
        self.label_str = ", ".join(self.labels)

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY missing")
        
        self.llm = ChatGroq(
            model="llama-3.2-11b-vision-preview",
            api_key=api_key,
            temperature=0.1,
            max_tokens=100
        )

    def _preprocess(self, image_bytes: bytes) -> Image.Image:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img.thumbnail((1024, 1024))
        return img

    def classify(self, image_bytes: bytes) -> dict:
        img = self._preprocess(image_bytes)
        img_b64 = base64.b64encode(io.BytesIO().getvalue())  # Dummy, not used

        message = HumanMessage(
            content=[
                {"type": "text", "text": CLASSIFIER_PROMPT.format(labels=self.label_str)},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}"
                    }
                }
            ]
        )

        try:
            response = self.llm.invoke([message])
            return json.loads(response.content)
        except Exception as e:
            return {"label": "error", "confidence": 0.0, "reason": f"LangChain: {e}"}
