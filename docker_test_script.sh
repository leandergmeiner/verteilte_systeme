#!/bin/bash

docker network create verteilte-systeme

docker build -t nameserver --file ./dockerfiles/nameserver.Dockerfile .

docker build -t dispatcher --file ./dockerfiles/dispatcher.Dockerfile .

docker build -t worker --file ./dockerfiles/worker.Dockerfile .

docker build -t client --file ./dockerfiles/client.Dockerfile .