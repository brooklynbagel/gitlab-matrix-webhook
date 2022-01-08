FROM python:3.9

RUN useradd --create-home webhook

USER webhook

WORKDIR /webhook

COPY --chown=webhook:webhook ./requirements.txt /webhook/requirements.txt

RUN pip install --user --no-cache-dir -r /webhook/requirements.txt

COPY --chown=webhook:webhook ./webhook /webhook/webhook

CMD [ "/home/webhook/.local/bin/uvicorn", "webhook.main:app", "--host", "0.0.0.0", "--port", "8000" ]