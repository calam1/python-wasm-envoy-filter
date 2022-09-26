FROM python:3.9.6-alpine
WORKDIR /project
COPY ./client.py /project
COPY ./requirements.txt /project
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python" ]
CMD [ "client.py" ]
