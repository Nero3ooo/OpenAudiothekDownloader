FROM python:3.14-rc

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN apt-get update && apt-get install -y ffmpeg

COPY ./app /code/app

CMD ["python", "./app/app.py"]