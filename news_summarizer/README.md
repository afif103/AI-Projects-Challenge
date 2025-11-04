# 📰 News Summarizer – Daily AI News Digest

**Summarize any news article in 3–5 neutral sentences. Paste text or URL. Export PDF report.**



---

## 🚀 Live Demo
[Streamlit Cloud (CPU Fallback Mode)](https://ai-projects-challenge-ainewssummarizercrjyyn2hzpdc.streamlit.app/) 

---

## 🛠 Run Locally (Recommended – Full GPU + Ollama) 

### Prerequisites
- Python 3.10+
- NVIDIA GPU + CUDA 11.8+
- Ollama installed: `curl -fsSL https://ollama.com/install.sh | sh`
- Run: `ollama pull llama3.2`

### Steps
```bash
git clone https://github.com/ramiafif/news-summarizer.git
cd news-summarizer
pip install -r requirements.txt
streamlit run app.py

```
🔒 Privacy & Safety

100% local processing (with Ollama + FAISS)
No data sent to third parties
Input sanitized: URLs, emails, profanity removed
Max 5000 chars per article
Output capped at 300 chars


📊 Features

Paste article or enter URL (auto-scrape)
3–5 sentence factual summary
Key bullet points
Download PDF report (Helvetica, clean layout)
Dark mode toggle
GPU-accelerated embeddings (all-mpnet-base-v2)


🧠 Tech Stack


LayerTechLLMOllama(llama3.2) localEmbeddingsall-mpnet-base-v2 (HuggingFace)Vector DBFAISS (local)UIStreamlitPDFfpdfScraperrequests + BeautifulSoup

📄 Sample Output

Summary: Meta released Llama 3.2 with vision and 3B/11B variants. The model supports multimodal input and runs efficiently on edge devices. It is open-source under a commercial-friendly license.

Key Points:

Vision + text support
Optimized for mobile
MIT-like license


💡 Use Cases

Daily AI news digest
Research paper summaries
Corporate news monitoring
Personal knowledge base




Zero token cost. Fully offline-capable. Built for scale and privacy.
