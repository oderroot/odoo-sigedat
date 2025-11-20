FROM odoo:15.0

USER root

RUN apt-get update && apt-get install -y --no-install-recommends procps
RUN apt-get install libreoffice -y

RUN pip3 install -U debugpy
RUN pip3 install workalendar suds appy

COPY scripts/entry_point.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER odoo 
