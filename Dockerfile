
FROM python:3.7.2-stretch

COPY . /blockchain

WORKDIR blockchain

RUN pip install -r requirements.txt
RUN pip install -e .

ENTRYPOINT ["blockchain"]