FROM 3.12-alpine

RUN pip install crewai 
RUN pip install 'crewai[tools]' 

RUN mkdir -p /app
WORKDIR /app
ADD ./main.py /app/main.py