# Lightweight ARD-Audiothek-Downloader

Es handelt sich um eine kleine selfhosetd Web-App, welche Hörbücher, Podcasts und Filme von der ARD-Audiothek/Mediathek herunterladen kann. 

## Vorraussetzungen / Installation

Installation von Docker:

__Windows:__

1. Download und Installation von [Docker-Desktop](https://docs.docker.com/desktop/setup/install/windows-install/). Danach starten von Docker-Desktop.
2. Anlegen einer neuen Textdatei unter zB. %userprofile%\Music\openAudiothekDownloader
3. Inhalt der [compose.yaml](./compose.yaml) in die Textdatei einfügen, für Windows anpassen und danach in compose.yaml umbenennen.
4. Powershell öffnen: 
```
Tastenbefehl: Win+R
POWERSHELL eingeben
Enter drücken
```
Zu dem Ordner navigieren:
```
cd $env:USERPROFILE\Music\openAudiothekDownloader
```
5. Docker Compose mit der zuvor erstellten compose.yaml ausführen:
```
docker compose up -d --force-recreate
```
6. Im Browser den selbstgehosteten Service aufrufen:
```
http://localhost:5000/
```
7. Zum Beenden des Services:
```
docker compose down
```

__Linux:__
1. Installation von Docker-Compose zB über das Terminal:
```
apt-get install ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" |   tee /etc/apt/sources.list.d/docker.list > /dev/null
   
apt-get update
apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-compose
```
2. compose.yaml in neuem Ordner speichern.
3. Docker Compose mit der zuvor erstellten compose.yaml ausführen:
```
docker compose up -d --force-recreate
```
4. Im Browser den selbstgehosteten Service aufrufen:
```
http://localhost:5000/
```
5. Zum Beenden des Services:
```
docker compose down
```

## Nutzung

![alt text](./images/webfrontend.png)
### Download Show
Link der ersten Folge einfügen.

Die ausgewählte und kommende Folgen werden in das Verzeichnis heruntergeladen, welches in der compose.yml definiert wurde. 

Alternativ Link der Serienübersicht einfügen und herunterladen.
Hierbei werden allerdings häufig nicht alle Folgen erfasst und heruntergeladen.

### Download Episode

Nur die Episode dessen Link eingefügt wurde, wird heruntergeladen.

### Download Movie

Filme oder andere Dateien werden in dem anderen zuvor definierten Verzeichnis heruntergeladen. 
Hierzu wird [yt-dlp](https://github.com/yt-dlp/yt-dlp) verwendet.


## Installation als App (für Fortgeschrittene)
Zur Installation als PWA ist es notwendig, dass die App auf einem Server installiert wird, welcher über HTTPS erreichbar ist.

Die App kann über Chrome als PWA installiert werden, indem die URL aufgerufen wird und über das Chrome-Menü zum Startbildschirm hinzugefügt wird.

Wenn die App erfolgreich installiert wurde, ist es möglich in der Audiothek oder Mediathek eine Episode oder einen Film zu Teilen und dann den OpenAudiothekDownloader auszuwählen. Der Link sollte dann automatisch im Textfeld erscheinen.

