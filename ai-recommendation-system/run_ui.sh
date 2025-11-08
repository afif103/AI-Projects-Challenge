#!/bin/bash
echo "Starting AI Recommendation System..."

# Ingest data if not done
python -c "from backend.db.ingest import ingest_sample_data; ingest_sample_data()" 2>/dev/null || echo "Data already ingested."

# Launch Streamlit
streamlit run ui/app.py --server.port=8501 --server.headless=true