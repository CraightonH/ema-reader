FROM python:3.9.13-slim
ENV USER 'app'
ENV UID '999'
ENV TZ 'America/Denver'
ENV CODEDIR=/ema-reader

WORKDIR ${CODEDIR}

RUN wget -q "https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz" -O /tmp/geckodriver.tgz \
    && tar zxf /tmp/geckodriver.tgz -C /usr/bin/ \
    && rm /tmp/geckodriver.tgz 

RUN apt update && apt install -yq \
    firefox-esr

USER ${USER}

RUN python -m pip install -U \
    pip \
    setuptools

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=${USER} main.py config.py ${CODEDIR}/

CMD python main.py
