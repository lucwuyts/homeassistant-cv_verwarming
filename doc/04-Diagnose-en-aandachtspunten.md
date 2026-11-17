# Diagnose en aandachtspunten

## Snel controleren waarom er wel of geen warmte is

Controleer in deze volgorde:

1. **Doelwaarde:** staan `temp_wens_dag`, `temp_wens_nacht` en waar relevant `Nacht Keuken` op de verwachte waarden?
2. **Zonekeuze:** staat de juiste `input_boolean.cv_*` aan? Zo niet, dan geldt de nachttemperatuur.
3. **Kamersensor:** levert de bijbehorende losse temperatuursensor een geldige, realistische waarde?
4. **Delta:** bekijk `sensor.cv_debug_status` en zijn attributen.
5. **Kranen:** staan de RT-klimaatentiteiten in de juiste Home Assistant-ruimte en begint hun zichtbare naam met `RT`?
6. **Kraansetpoint:** vergelijk het berekende debugsetpoint met het setpoint en de `current_temperature` van de kraan.
7. **HA-ketelsturing:** controleer of `input_boolean.cv_ketelsturing_ha_actief` aan staat.
8. **Ketelsetpoint:** controleer het OpenTherm-regelsetpoint en de logboekmelding van `CV Controller`.
9. **OpenTherm:** controleer gateway-beschikbaarheid, ketelvlam, cv-waterdruk, aanvoer-/retourtemperatuur en storingssensoren.
10. **Onderhoudsstand:** controleer of `alle_cv_kranen_open_test` niet per ongeluk aan staat.

## Belangrijke afhankelijkheden

- De ruimtemeting voor Bureel, Living en Keuken is essentieel voor zowel kraan- als ketelsturing.
- Tussen gebruikt de keukensensor; een temperatuurverschil tussen die ruimtes wordt niet afzonderlijk gemeten in de regeling.
- Het weerobject `weather.wuytskes` levert de buitentemperatuur aan OTGW.
- De Tado-selectie hangt af van zowel ruimte-indeling als de prefix `RT`.
- De OpenTherm Gateway moet bereikbaar zijn onder gateway-id `otgw`.

## Fail-safe gedrag en mogelijke verrassingen

### Ongeldige temperatuursensor

De actieve CV-regeling gebruikt stabiele temperatuursensoren:

- `sensor.cv_bureel_temperatuur_stabiel`;
- `sensor.cv_living_temperatuur_stabiel`;
- `sensor.cv_keuken_temperatuur_stabiel`.

Deze sensoren nemen alleen geldige numerieke bronwaarden over. Wanneer de onderliggende kamersensor kort `unknown` of `unavailable` wordt, blijft de vorige geldige waarde staan. Daardoor wordt een tijdelijke sensorstoring niet meer als 0 °C gezien in de ketel- of kraanregeling.

Let op: bij een Home Assistant-herstart kan zo'n stabiele sensor eerst nog `unknown` zijn tot de bron opnieuw een geldige waarde doorgeeft.

### Geen warmtevraag geeft setpoint 0 °C

De actieve ketelregelaar start bij `max_delta > 0,5 °C` en houdt warmtevraag vast tot `max_delta <= 0,3 °C`. Zo voorkomt de hysterese schakelen door afronding rond 0,5 °C. Bij warmtevraag stelt de kraanregeling de kranen proportioneel hoger in. De aanvoer stijgt pas na vijf minuten zonder minstens 0,2 °C kamerrespons en blijft begrensd op basis van de grootte van de warmtevraag.

### Noodstand voor gewone thermostaat

De helper `input_boolean.cv_ketelsturing_ha_actief` dient als noodschakelaar. Wanneer deze uit staat, voert `automation.cv_control_setpoint_dynamisch` setpoint 0 °C naar de OTGW zodra de laatst verstuurde waarde nog niet 0 °C is. Daarmee wordt de OpenTherm-override vrijgegeven, zodat een gewone noodthermostaat de warmtevraag kan overnemen.

Deze softwarestand vervangt geen fysieke test. Controleer apart of de noodthermostaat elektrisch en OpenTherm-technisch echt rechtstreeks of correct via de gateway kan werken.

### Keuken en Tussen zijn gekoppeld

Beide ruimtes delen één aan/uit-helper en één temperatuursensor. De drie betrokken kranen kunnen niet op basis van een afzonderlijke Tussen-temperatuur worden geregeld.

Er bestaat een afzonderlijke instelling **Nacht Keuken**. De actieve Tado-regeling gebruikt momenteel nog de algemene nachttemperatuur; oudere MQTT-scripts gebruiken wel de aparte keukenhelper. De geregistreerde entity-id is `input_number.nacht_keuken`.

### Gastenkamer heeft nog geen Tado

`Gastenkamer Nacht Temp` en `CV Gastenkamer` gaan over de gastenkamer. Omdat daar nog geen Tado aanwezig is, valt deze kamer buiten de huidige dynamische kraanregeling. De UI-helper blijft buiten het package; de schakelaar wordt alleen in de nachtlogica uitgezet.

### Booststatus stuurt kranen en ketel

Tijdens boost zet `script.cv_boost_zone_parameterized` de kranen van de gebooste zone naar 30 °C. De ketelregelaar gebruikt dan `input_number.cv_boost_aanvoer_temp` als OpenTherm-setpoint, behalve wanneer `input_boolean.cv_ketelsturing_ha_actief` uit staat.

### Ieder uur OTGW herstart (los van het CV-package)

De afzonderlijke Home Assistant-automatisering **Herstart OTGW** onderbreekt ieder vol uur de gatewayvoeding 59 seconden. Ze staat in `automations.yaml`, buiten dit CV-package. Tijdens dat venster kunnen OpenTherm-entiteiten tijdelijk niet beschikbaar zijn en kan een regelactie mislukken of pas bij de volgende cyclus effect krijgen.

De CV-regelaar berekent het ketelsetpoint iedere 30 seconden en schrijft wijzigingen op hele graden direct. Een aparte keepalive herhaalt een actief setpoint vanaf 8 °C iedere minuut, maar alleen als de regelaar recent nog hetzelfde setpoint berekende. De buitentemperatuur wordt alleen geschreven bij een verandering van 0,1 °C.

### Ochtendstart is een bewuste dagschakelaar

Om 07:00 wordt standaard alleen de nachtmarkering uitgezet. Voor dagen waarop je de comfortverwarming eerder wilt starten kan **CV: eenmalige ochtendstart** vooraf worden aangezet. Die start Living en Keuken + Tussen om 06:00 en schakelt zichzelf daarna weer uit.

### Afwezigheid wordt niet automatisch hersteld

Bij vijf minuten volledige afwezigheid gaan de drie hoofd-zones uit. In de onderzochte automatiseringen is geen spiegelactie gevonden die ze bij thuiskomst terug aanzet.

## Configuratie-observaties

- De oude MQTT-automatiseringen publiceren dag/nachtwaarden naar `homeassistant/cv/on`, maar stonden uit.
- `cv_counter` en `cv_constantaan` zijn restanten of aanvullende helpers die niet in de actieve kernregeling terugkomen. De gastenkamerschakelaar `cv_nic` wordt alleen in de nachtlogica uitgezet en regelt geen radiator.
- De afzonderlijke helper Nacht Keuken is nog niet in de actieve Tado-regeling verwerkt; de oudere scripts bevatten bovendien een afwijkende spelling van de entity-id.
- De boost-eindtijdhelpers worden geschreven door het boostscript, maar `CV Boost Auto Stop` gebruikt deze tijdstippen niet.
- De onderhoudsactie schakelt `automation.status_cv` uit, maar niet de aparte ketelregelaar.

## Veilig onderhoud

Voor fysiek werk aan radiatoren of ketel is de Home Assistant-teststand geen veiligheidsisolatie. Schakel de installatie volgens de voorschriften van ketel en verwarmingssysteem uit en controleer druk en temperatuur. De softwarestand “alle kranen open” dient alleen om kleppen open te sturen.
