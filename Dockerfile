FROM python:3.10
WORKDIR /bot
COPY requirements.txt /bot/
RUN pip install -r requirements.txt
COPY . /bot
EXPOSE 8080
CMD python main.py & python pudding_api.py