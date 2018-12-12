FROM python:3.7.1

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

COPY start /usr/local/bin/start
RUN chmod u+x /usr/local/bin/start


