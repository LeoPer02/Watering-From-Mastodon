# start by pulling the python image
FROM python:latest

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

ENV SECRET_KEY="this is where you should place your secret key"
ENV MQTT_BROKER="localhost"

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt
RUN pip install python-dotenv

# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["main.py" ]