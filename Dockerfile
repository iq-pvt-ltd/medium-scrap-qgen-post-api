FROM python:3.8


COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

RUN python -m nltk.downloader stopwords
RUN python -m nltk.downloader popular


COPY . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]