FROM python:3.12-slim-bookworm

RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential

RUN pip install --upgrade pip setuptools
RUN pip install crewai 
RUN pip install 'crewai[tools]' 
RUN pip install 'markdown' 

RUN mkdir -p /app
WORKDIR /app
ADD ./ /app/

CMD python main.py
