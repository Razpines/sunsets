@echo off
REM Install dependencies, compile scripts, and launch the Streamlit app
python -m pip install -r requirements.txt
python -m py_compile sunset_prediction.py streamlit_app.py
streamlit run streamlit_app.py
