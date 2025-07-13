@echo off
echo 🚀 Starting Chat with Image App...
echo.

cd /d "c:\Users\Admin\Documents\AI-Python\GenAI\ChatWithImage"

echo � Checking dependencies...
"C:/Program Files/Python312/python.exe" -m pip install -r requirements.txt --quiet

echo �📡 Opening browser at http://localhost:8501
echo ⏹️  Press Ctrl+C to stop the app
echo.

"C:/Program Files/Python312/python.exe" -m streamlit run main.py
