FROM rust:1.67

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y python3.10 && \
    apt-get install -y python3-pip

RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc

RUN pip install --upgrade pip==23.0
RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=30100
ENV APP_MODULE=main:app

EXPOSE $PORT

CMD uvicorn --host=0.0.0.0 --port $PORT $APP_MODULE
