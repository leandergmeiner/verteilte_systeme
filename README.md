# Verteilte Systeme Prüfungsaufgabe

## Ausführung mit Docker

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

## Ausführung lokal

Die Datei [main.py](./main.py) dient als Einstiegspunkt für alle Teile des Systems. Voraussetzungen sind eine aktuelle Version
von python und poetry insatlliert zu haben. Die nötigen Dependencies können ganz einfach mit```poetry install``` installiert werden.
Um alles ausführen zu können muss zunächst der **nameserver** gestartet werden, dies muss im poetry environment stattfinden.
Anschließend kann man den dispatcher, worker und den client starten. Folgende Befehler sind notwenig um alle Services
lokal auszuführen (mit der default Portwahl, welche mit angabe des Ports überschrieben werden kann):
~~~shell
poetry run python3 main.py nameserver
~~~
~~~shell
poetry run python3 main.py dispatcher
~~~
Um den Worker zu starten wird die Angabe der Aufgabe, für die der Worker zuständig sein soll, sowie der 
Dispatcher Adresse benötigt. Die unterstützten Aufgaben sind:
* sum (Summiert 2 übergebene Zahlen)
* hash (sha256 hash des übergebenen Strings)
~~~shell
poetry run python3 main.py worker sum localhost:50052
~~~
~~~shell
poetry run python3 main.py dispatcher
~~~
