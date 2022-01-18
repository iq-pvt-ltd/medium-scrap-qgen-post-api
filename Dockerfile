FROM python:3.8

COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# RUN python -m nltk.downloader stopwords
# RUN python -m nltk.downloader popular

COPY . .

RUN useradd -m myuser
USER myuser
COPY ./nltk_data ./home/myuser/nltk_data

EXPOSE 8000

# CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
CMD exec gunicorn --bind :8000 --workers 3 --worker-class uvicorn.workers.UvicornWorker  --threads 8 --timeout 3600 api:app