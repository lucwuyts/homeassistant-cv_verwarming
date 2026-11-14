# Home Assistant CV Heating

Een Home Assistant-package voor centrale-verwarmingsregeling met thermostatische radiatorkranen en een OpenTherm Gateway. De regeling gebruikt YAML-helpers, automations, scripts en templates. Ze is opgesplitst in een package zodat de CV-configuratie apart kan worden bijgewerkt.

> **Installatiegebonden configuratie:** dit project is oorspronkelijk gemaakt voor één woning. De entity-id's, ruimtes en enkele automations zijn voorbeelden uit die Home Assistant-installatie. Pas ze aan voordat je dit package in een andere installatie laadt. Kopieer nooit de volledige Home Assistant-configuratie uit deze repository over je eigen configuratie.

## Wat doet het?

- Regelt de zones Bureel, Living en Keuken; Tussen deelt de keukeninstelling en -sensor.
- Stuurt Tado-radiatorkranen per Home Assistant-ruimte aan. De macro zoekt climate-entiteiten met een zichtbare naam die met `RT` begint.
- Stuurt het CV-setpoint via de OpenTherm Gateway.
- Beheert de bijbehorende helpers, boost, nachtlogica en diagnostische templates in één package.
- Opent een kraan proportioneel verder naarmate een ruimte achterloopt. Bij een tekort groter dan 2 °C vraagt de kraan 30 °C en houdt die opdracht vast tot het tekort 1,5 °C of kleiner wordt.
- Start de cv-aanvoer bij warmtevraag op 30 °C. Zonder meetbare ruimteverwarming wordt de aanvoer in stappen van 2 °C verhoogd. Bij kleine tekorten geldt een lagere bovengrens.

De precieze regelgrenzen en bediening staan in [`doc/01-Werking.md`](doc/01-Werking.md) en [`doc/06-Boost-en-noodstand.md`](doc/06-Boost-en-noodstand.md).

## Vereisten

- Een werkende Home Assistant-installatie die YAML-configuratie en packages kan laden.
- De OpenTherm Gateway-integratie geconfigureerd in Home Assistant, met de service `opentherm_gw.set_control_setpoint` beschikbaar.
- Ruimtetemperatuursensoren voor Bureel, Living en Keuken.
- Radiatorkranen als `climate`-entiteiten, toegewezen aan de juiste Home Assistant-ruimtes.
- De template-macro in `custom_templates/rt_tools.jinja`.

Home Assistant-documentatie: [configuration packages](https://www.home-assistant.io/docs/configuration/packages/), [custom templates and macros](https://www.home-assistant.io/docs/templating/custom-templates/) en [OpenTherm Gateway-integratie](https://www.home-assistant.io/integrations/opentherm_gw).

## Installatie

1. Maak een backup van je Home Assistant-configuratie.
2. Controleer `configuration.yaml`. Als packages nog niet zijn ingeschakeld, voeg dan onder de bestaande `homeassistant:`-sleutel toe:

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

   Staat er al een `homeassistant:`-sleutel, maak dan geen tweede aan; voeg alleen `packages:` toe onder de bestaande sleutel. Controleer ook of de map `packages` nog niet op een andere manier is ingelezen.

3. Kopieer `packages/cv_heating.yaml` naar `<HA-config>/packages/cv_heating.yaml`.
4. Kopieer `custom_templates/rt_tools.jinja` naar `<HA-config>/custom_templates/rt_tools.jinja`.
5. Pas de entity-id's en ruimtes in het package aan voor jouw installatie; zie [Sensoren en aanpassen](#sensoren-en-aanpassen).
6. Controleer de Home Assistant-configuratie. Herstart Home Assistant om YAML-helpers en het package te laden. Als je later alleen de macro wijzigt, laad dan de custom templates opnieuw via `homeassistant.reload_custom_templates`.
7. Controleer na de herstart of de scripts, automations en entiteiten beschikbaar zijn en bekijk de logboeken op ontbrekende entity-id's.

De configuratie-inhoud van `packages/cv_heating.yaml` staat op hetzelfde YAML-niveau als `input_boolean:`, `automation:` en `script:` in een package. Voeg die sleutels niet nog eens toe aan `configuration.yaml`. Home Assistant combineert het package met de overige configuratie.

## Sensoren en aanpassen

De volgende ruwe sensoren zijn de standaardwaarden uit de oorspronkelijke installatie. Vervang ze door de entity-id's in jouw eigen Home Assistant. Je vindt die onder **Instellingen → Apparaten & diensten → Entiteiten**.

| Ruimte | Standaard ruwe sensor | Stabiele sensor gebruikt door de regeling |
|---|---|---|
| Bureel | `sensor.atc_d897_temperature` | `sensor.cv_bureel_temperatuur_stabiel` |
| Living | `sensor.living_nest_living_temperatuur` | `sensor.cv_living_temperatuur_stabiel` |
| Keuken en Tussen | `sensor.keuken_thermometer_bt_temperature` | `sensor.cv_keuken_temperatuur_stabiel` |

Wijzig de **ruwe sensor** in `packages/cv_heating.yaml`, in de drie trigger-template-sensoren onderaan bij `template:`. Vervang daar de `entity_id` bij `trigger:`. De stabiele sensoren houden de laatste geldige temperatuur vast wanneer een ruwe sensor tijdelijk `unknown` of `unavailable` is.

De ketel- en kraanregeling verwijzen verder naar de stabiele entity-id's in dezelfde package, bijvoorbeeld in `CV Control Setpoint Dynamisch`, `Status CV - Alle ruimtes (script)` en `CV boost zone (parameterized)`. Als je de namen of entity-id's van de stabiele sensoren wijzigt, werk dan ook die verwijzingen bij. Laat ze bij voorkeur ongewijzigd en vervang alleen de drie ruwe sensor-id's.

### Andere installatie-afhankelijke verwijzingen

| Verwijzing | Waar aanpassen of wat doen |
|---|---|
| `weather.wuytskes` | Buitentemperatuurbron voor de OpenTherm Gateway; vervang in de automation `Buiten Temp CV` in `packages/cv_heating.yaml`, of schakel die automation uit. |
| `gateway_id: otgw` | Vervang in de OpenTherm-acties door de gateway-id van jouw integratie. |
| `RT`-kranen en ruimte-indeling | Wijs elke kraan toe aan de juiste HA-ruimte en laat de zichtbare naam met `RT` beginnen. Pas de ruimteargumenten in `Status CV - Alle ruimtes (script)` aan als jouw ruimtebenamingen verschillen. |
| `climate.living_nest_living` | Alleen nodig voor de meegeleverde Nest/Living-koppeling. Vervang de entiteit of schakel die automations uit als je geen overeenkomstige Nest-thermostaat hebt. |
| `binary_sensor.iedereen_afwezig`, `input_boolean.l_m_blijvenaanwezig` | Alleen gebruikt door aanwezigheidslogica. Vervang de entiteiten of schakel de betreffende aanwezigheidsautomations uit. |
| MQTT-topics en -entiteiten | De package bevat oudere MQTT-gerelateerde routines. Controleer ze tegen jouw MQTT-configuratie en schakel ongebruikte routines uit. |
| Tado-debugsensoren | Onderaan het package staan twee optionele templates met vaste Bureel-kraan-entity-id's. Vervang die entity-id's of verwijder alleen die diagnostische templates. |

De helper `input_number.temp_wens_nacht` is de algemene nachttemperatuur. De afzonderlijke helper `input_number.nacht_keuken` wordt door oudere MQTT-scripts gebruikt; de huidige Tado- en ketelregeling gebruikt voor Keuken en Tussen de algemene nachtinstelling.

## Ruimtes voor radiatorkranen

De macro zoekt `climate`-entiteiten binnen een ruimte met `area_entities()` en selecteert entiteiten waarvan de zichtbare naam met `RT` begint. Stel in Home Assistant dus de ruimte-toewijzing en naamgeving van je kranen goed in. Als je andere ruimtebenamingen gebruikt, pas dan de ruimteargumenten aan in de automation `Status CV - Alle ruimtes (script)` en de boostscripts.

De entity-id's van Tado-apparaten hoeven niet in de hoofdregeling te worden opgesomd zolang de ruimte en naam voldoen. De fysieke klepstand wordt in deze installatie niet als percentage-attribuut geregistreerd; `temperature` is het ingestelde kraansetpoint.

## Updates

De bestanden in `packages/` en `custom_templates/` zijn de bronbestanden. Werk in een bestaande installatie alleen deze CV-bestanden bij; kopieer geen `configuration.yaml`, `automations.yaml`, `scripts.yaml`, MQTT-configuratie of andere Home Assistant-bestanden uit een andere installatie.

Het meegeleverde `scripts/Sync-CvPackage.ps1` is bedoeld voor de oorspronkelijke Windows-installatie. De standaard netwerkpaden en documentatielocatie zijn installatiegebonden. Controleer of geef `-HomeAssistantConfig` en `-DocumentationDestination` expliciet op voordat je dat script elders gebruikt. De migratietool `scripts/Migrate-CvToPackage.py` is eveneens bedoeld voor de oorspronkelijke configuratie en is geen algemene installatieprocedure.

Meer details:

- [`doc/02-Zones-en-entiteiten.md`](doc/02-Zones-en-entiteiten.md) — zones, sensoren en helpers.
- [`doc/03-Automatiseringen-en-bediening.md`](doc/03-Automatiseringen-en-bediening.md) — bediening en automatiseringen.
- [`doc/04-Diagnose-en-aandachtspunten.md`](doc/04-Diagnose-en-aandachtspunten.md) — diagnose.
- [`doc/07-Beheer-en-synchronisatie.md`](doc/07-Beheer-en-synchronisatie.md) — beheer van de oorspronkelijke installatie.
