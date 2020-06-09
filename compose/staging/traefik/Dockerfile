FROM traefik:latest

RUN mkdir -p /etc/traefik/acme
RUN touch /etc/traefik/acme/acme.json
RUN chmod 600 /etc/traefik/acme/acme.json
COPY ./compose/staging/traefik/traefik.yml /etc/traefik
