# MediaVault met Home Assistant

Vanaf MediaVault 0.3.236. Home Assistant Core 2026.9 of nieuwer; getest met
2026.9.1. De koppeling werkt lokaal zonder GPT, MQTT, cloudaccount of extra
servercontainer. De serverondersteuning zit standaard in het MediaVault-image;
de Home Assistant-component wordt in Home Assistant geïnstalleerd.

## Installeren via HACS

1. Werk de MediaVault-server en de te bedienen Android-/TV-clients bij.
2. Open HACS → menu → Aangepaste repositories. Voeg
   `https://github.com/ScorpionZK89/MediaVault-Releases` toe als **Integratie**.
3. Download MediaVault en herstart Home Assistant wanneer HACS daarom vraagt.
4. Open MediaVault → Instellingen → Integraties → Home Assistant. Maak een
   sleutel voor het actieve profiel. Vink bediening aan; taakbeheer is optioneel.
5. Open Home Assistant → Instellingen → Apparaten en diensten → Integratie
   toevoegen → MediaVault. Vul het MediaVault-serveradres en de sleutel in.
   Gebruik bijvoorbeeld `http://mediavault.local:3000`, zonder `/api` erachter.
6. Open de MediaVault-app op het gewenste apparaat en selecteer hetzelfde profiel.
   De speler verschijnt automatisch in Home Assistant.

De sleutel wordt in MediaVault slechts één keer getoond en alleen gehasht
opgeslagen. Home Assistant bewaart hem in zijn beveiligingsgevoelige configuratie;
behandel HA-back-ups als vertrouwelijk. Zet sleutels nooit in dashboard-YAML,
automatiseringsnamen, screenshots, Git of URL-queryparameters.

## Zien en bedienen

- Per aangemelde client: beschikbaarheid, titel, poster, speelstatus, positie en
  duur. Ondersteunde acties: starten, pauzeren, hervatten, stoppen en zoeken
  binnen de video. De mediabrowser biedt pagina's met titels en een zoekfunctie.
- Per toegestane bibliotheek: aantal standaardtitels (films en afleveringen;
  alternatieve bestandsversies en extra's tellen niet dubbel mee).
- Bij een beheerdersaccount: CPU en werkgeheugen van MediaVault plus werkprocessen,
  bezetting van het datavolume, actieve streams, transcodes, Direct Play/Stream,
  actieve/wachtende/mislukte taken en beschikbare MediaVault-update.
- Met expliciete beheerrechten: een incrementele scan per bibliotheek en
  `mediavault.task_action` voor pauzeren/hervatten/annuleren van bestaande taken.
  Taak-ID's staan bij de attributen van de sensor Actieve taken; de onderliggende
  taak moet de gevraagde actie daadwerkelijk ondersteunen.

Een standaard Home Assistant-mediakaart werkt met de nieuwe `media_player`-
entiteiten. Gebruik normale `media_player.media_pause`, `media_player.media_play`,
`media_player.media_stop`, `media_player.media_seek` en `media_player.play_media`
acties in automatiseringen. Voor `play_media` is het contenttype `mediavault` en
het content-ID het MediaVault-media-ID, geen bestandsnaam of externe URL.

## Grenzen en rechten

Een koppeling hoort bij één account en één profiel. Andere profielen blijven
afgeschermd; voeg ze desgewenst afzonderlijk toe. Servermetingen en taakbeheer
zijn alleen voor beheerders. De sleutel geeft **geen** gewone beheersessie en
kan geen accounts maken, instellingen wijzigen of persoonlijke media verwijderen.

Een speler moet actief zijn: Web in een zichtbare tab of tijdens playback;
Android/TV in de voorgrond. Na circa 15 seconden zonder heartbeat wordt hij
onbeschikbaar. Deze integratie kan geen gesloten app of uitgeschakelde TV starten.
Offline downloads en een door de app bediende Cast-sessie worden niet als lokaal
bedienbare speler aangeboden. Er worden geen nepknoppen voor volume, aan/uit,
Chromecast of andere niet-ondersteunde functies getoond.

Status ververst ongeveer iedere 5 seconden; serveractiviteit en updatecontrole
iedere minuut. Opdrachten worden niet optimistisch als geslaagd gemeld: de client
moet bevestigen. Er is maximaal één onderhanden opdracht per apparaat. Play/pause/
stop verlopen na 15 seconden; starten/seek na 120 seconden vanwege streamvoorbereiding.
Een verlopen opdracht wordt niet later bij herverbinden alsnog afgeleverd.
De bestaande display-/codec-/kwaliteitskeuze blijft bepalend voor het afspelen.

Browsers kunnen afspelen met geluid zonder eerdere gebruikersinteractie weigeren.
Open en bedien MediaVault dan eerst lokaal; Home Assistant rapporteert een mislukte
opdracht in plaats van te doen alsof de video speelt. Gebruik op internet HTTPS;
voor deze lokale koppeling hoeft geen extra poort publiek te worden geopend.

## Adres wijzigen, sleutel vernieuwen of verwijderen

Gebruik **Opnieuw configureren** op de Home Assistant-integratie voor een nieuw
serveradres of nieuwe sleutel van hetzelfde profiel. Bij sleutelintrekking
vraagt Home Assistant opnieuw om aanmelding. Entiteit-ID's blijven stabiel als
dezelfde serverdatabase, hetzelfde profiel en dezelfde clientidentiteit behouden
blijven. Wissen van appdata of een nieuwe Web-tab kan een nieuw apparaat opleveren.
Onder **Bekende spelers** in MediaVault kun je ongebruikte offline apparaten
vergeten. Verwijder hun eventuele oude entiteiten ook uit Home Assistant.

Verwijder de HA-integratie en trek ook de sleutel in MediaVault in wanneer de
koppeling niet meer nodig is. Een serverherstart maakt bekende spelers tijdelijk
onbeschikbaar; oude opdrachten worden nooit uit opslag opnieuw uitgevoerd.

## Ontwikkeltests

`tests/home_assistant/Dockerfile` bouwt de geïsoleerde, gepinde Linux-testomgeving.
Mount `custom_components` read-only als `/workspace/custom_components` en
`tests/home_assistant` read-only als `/workspace/tests`. De tests gebruiken de
echte HA-configuratieflow, coördinator, platformen en services met testtransport.

`scripts/test-home-assistant-ui.cjs` test echte Web-playback via een tijdelijke
lokale server. `--android` test de echte Android-activiteit/Media3 via een
acceptance-APK op een emulator. De harness maakt uitsluitend synthetische media
onder `media/__codex_test__`, verwijdert haar eigen runtime en ruimt remote
captures in `/data/local/tmp` op. Geheime testreferenties gaan niet naar Git.

De acceptance matrix en het testverslag onderscheiden software-, emulator- en
productiebewijs. Een geslaagde bedieningsproef bewijst geen HDR-, Dolby- of
GPU-ondersteuning.
