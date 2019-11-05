FROM python:3.6

EXPOSE 80

WORKDIR /gos

COPY requirements.txt /gos
RUN pip install -r requirements.txt

COPY gos.py /gos
CMD python gos.py
