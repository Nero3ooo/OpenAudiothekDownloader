## Lightweight ARD-Audiothek-Downloader

Es handelt sich um ein Python Script, welches Hörbücher und Podcasts von der ARD-Audiothek herunterladen kann. 

### Vorraussetzungen

Python3

Zusätzlich müssen folgende Bibliotheken installiert werden:

Requests:
```
pip install requests
```

bs4:
```
pip install bs4
```

wget:
```
pip install wget
```

### Nutzung

#### Über die erste Folge

Um einen Podcast oder ein Hörbuch herunterzuladen, muss der Link der ersten Folge kopiert und an das Script übergeben werden.
Anschließend werden alle weiteren Episoden heruntergeladen, sofern sie in der Audiothek als nächste Episode verlinkt sind.

Beispiel für [Die Märchen der Brüder Grimm](https://www.ardaudiothek.de/episode/die-maerchen-der-brueder-grimm/das-maerchen-der-brueder-grimm-01-der-raeuberbraeutigam/ard/89322458/)
```
python audioDownloader.py https://www.ardaudiothek.de/episode/die-maerchen-der-brueder-grimm/das-maerchen-der-brueder-grimm-01-der-raeuberbraeutigam/ard/89322458/
```

#### Über die Folgenübersicht

<b>Die Variante funktioniert bisher nicht vollständig!</b>

Es können kleinere Hörbücher oder Podcasts auch über die Folgenübersicht heruntergeladen werden. Es werden allerdings nur die obersten 6 bis 8 Folgen heruntergeladen.

Beispiel für [Die Märchen der Brüder Grimm](https://www.ardaudiothek.de/sendung/die-maerchen-der-brueder-grimm/75559248/)
```
python audioDownloader.py https://www.ardaudiothek.de/sendung/die-maerchen-der-brueder-grimm/75559248/
```

