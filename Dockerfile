FROM python:3.11.6-slim-bullseye
WORKDIR /app
COPY ./djangopoc ./

RUN pip install --upgrade pip --no-cache-dir

RUN pip install -r /app/requirements.txt --no-cache-dir

RUN chmod +x /app/server-entrypoint.sh
RUN chmod +x /app/worker-entrypoint.sh


# CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]
# CMD ["gunicorn","djangopoc.wsgi:application","--bind", "0.0.0.0:8000"]
# CMD ["waitress-serve", "--listen", "0.0.0.0:8000", "djangopoc.wsgi:application"]
