# Camera Image Classifier (Streamlit)

Zero-shot classification using **Ollama (local)** or **Groq (cloud)**.

## Features
- Local = 100% private
- Cloud = fast inference
- Safe: 5MB limit, resize, validation
- Custom labels
- VS Code + Conda ready

## Conda Setup (VS Code)

1. **Open folder in VS Code**
2. **Open Terminal** (`Ctrl + `` `)
3. **Create Conda env**:
   ```bash
   conda create -n img-class python=3.12 -y

   conda activate img-class
   
   pip install -r requirements.txt     
   ollama pull llava  
   ollama serve
   streamlit run frontend/app.py            
