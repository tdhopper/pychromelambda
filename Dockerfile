FROM lambci/lambda:build-python3.6
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY bin/chromedriver /opt/chromedriver
COPY bin/headless-chromium /opt/headless-chromium
CMD bash
