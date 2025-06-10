# Verteilte Systeme Prüfungsaufgabe

## Ausführung mit Docker

Das verwendete docker script und die [docker-compose.yaml](docker-compose.yml) wurden nur auf Linux und MacOS erfolgreich getestet,
somit kann keine Windows kompatibilität garantiert werden (da es auf Windows manchmal zu Problemen mit docker networks kommen kann).

Das Repo enthält alle Teile der Prüfungsleistung. Da diese in verteilten Dockerkontainern laufen sollen, kann man nicht
nur ein **Dockerfile** wie gewohnt bauen und ausführen. Die **Dockerfiles** befinden sich im Ordner 
[dockerfiles](./dockerfiles) sie müssen jedoch aus dem Wurzelverzeichnis gebaut werden (da dockers *COPY* Befehl nicht
außerhalb des contexts operieren kann). Um diese zu bauen, sollte das script [docker_test_script.sh](docker_test_script.sh)
verwendet werden.
Anschließend lassen sich die container mit der [docker-compose](docker-compose.yml) mit dem Befehl ```docker compose up```
ausführen. 

Um die container im Hintergrund auszuführen wird ```docker compose up -d``` verwendet und um diese wieder zu beenden
und die Container aufzuräumen: ```docker compose down --remove-orphans```.

## Ausführung lokal
Um die lokale Ausführung zu testen kann einfach das [test Script](test_script.bash) verwendet werden.

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
* hash (md5 hash des übergebenen Strings)
* reverse (Gibt Eingabestring von rechts nach links zurück)
* strlen (Gibt die Längen der Eingabestrings zurück)
* floor (Gibt den Integer Teil einer Dezimalzahl zurück)
* softmax (Wendet die softmax Funktion auf die Eingabezahlen an)
~~~shell
poetry run python3 main.py worker {task} localhost:50052
~~~
Um die Funktionen als client zu testen kann man die folgende Funktion nutzen.
~~~shell
poetry run python main.py exec {task} {args}
~~~
