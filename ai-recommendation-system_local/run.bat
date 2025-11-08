@echo off
cd /d "C:\Users\Rami\anaconda_projects\ai-recommendation-system"
set PYTHONPATH=%CD%
echo.
echo ================================
echo   AI RECOMMENDATION SYSTEM
echo ================================
echo.
streamlit run ui/app.py --server.port=8501
pause