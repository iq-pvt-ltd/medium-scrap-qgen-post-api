FROM python:3.8


COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5000"]