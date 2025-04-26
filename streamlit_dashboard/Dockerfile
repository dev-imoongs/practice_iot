FROM python:3.10-slim

WORKDIR /streamlit_dashboard

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit_dashboard.py ./

CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]