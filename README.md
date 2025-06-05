# Verteilte Systeme Prüfungsaufgabe

## Verwendung

Das Repo enthält alle Teile der Prüfungsleistung. Da diese in verteilten Dockerkontainern laufen sollen, kann man nicht
nur ein **Dockerfile** wie gewohnt bauen und ausführen. Die **Dockerfiles** befinden sich im Ordner 
[dockerfiles](./dockerfiles) sie müssen jedoch aus dem Wurzelverzeichnis gebaut werden (da dockers *COPY* Befehl nicht
außerhalb des contexts operieren kann). Die Befehle für die Erstellung der jeweiligen Docker Images:
~~~shell
docker build -t nameserver --file ./dockerfiles/nameserver.Dockerfile .
~~~
~~~shell
docker build -t client --file ./dockerfiles/client.Dockerfile .
~~~
~~~shell
docker build -t dispatcher --file ./dockerfiles/dispatcher.Dockerfile .
~~~
~~~shell
docker build -t worker --file ./dockerfiles/worker.Dockerfile .
~~~