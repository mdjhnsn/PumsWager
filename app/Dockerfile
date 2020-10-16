FROM python:3.8.6

LABEL MAINTAINER="Michael Johnson <mdjhnsn@gwu.edu>"

ENV GROUP_ID=1000 \
    USER_ID=1000

RUN addgroup --gid $GROUP_ID www
RUN adduser --uid $USER_ID --ingroup www www --shell /bin/sh

USER www

COPY . /var/www

WORKDIR /var/www

RUN pip install -r requirements.txt
RUN pip install gunicorn

ENV PATH='home/www/.local/bin:$PATH'

EXPOSE 8050

CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:8050", "wsgi" ]