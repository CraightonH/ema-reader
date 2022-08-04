FROM python:3.9.13-slim
ENV USER 'app'
ENV UID '999'
ENV TZ 'America/Denver'
ENV CODEDIR=/ema-reader

WORKDIR ${CODEDIR}

ADD "https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz" /tmp/geckodriver.tgz

RUN tar zxf /tmp/geckodriver.tgz -C /usr/bin/ \
    && rm /tmp/geckodriver.tgz \
    && useradd -m -r ${USER} \
    && chown ${USER}:${USER} ${CODEDIR} \
    && echo ${TZ} > /etc/timezone \
    && ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime

RUN apt update && apt install -yq \
    firefox-esr

USER ${USER}

RUN python -m pip install -U \
    pip \
    setuptools

COPY --chown=${USER} requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=${USER} main.py config.py ${CODEDIR}/

CMD python main.py
