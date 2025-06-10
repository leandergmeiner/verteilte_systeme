FROM alpine:3.22

RUN mkdir /nameserver

# Copy all files in verteilte_systeme to the container
COPY . /nameserver

WORKDIR /nameserver

RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    py3-virtualenv \
    bash \
    netcat-openbsd

# Create python venv (to use pip without Errors)
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN pip3 install --no-cache-dir poetry

RUN poetry install

ENTRYPOINT ["poetry", "run", "python3", "main.py", "nameserver"]