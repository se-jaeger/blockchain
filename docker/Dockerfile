FROM python:3.7.2-stretch

RUN git clone https://github.com/se-jaeger/blockchain.git

WORKDIR blockchain

RUN pip install -r requirements.txt
RUN pip install -e .

ENTRYPOINT ["blockchain"]