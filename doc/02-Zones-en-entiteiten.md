# Zones en entiteiten

## Hoofd-zones

| Zone | Aan/uit-helper | Externe temperatuursensor | Tado-radiatorkranen |
|---|---|---|---|
| Bureel | `input_boolean.cv_bureel` | `sensor.cv_bureel_temperatuur_stabiel` | RT03 Bureel Deur; RT02 Bureel Venster |
| Living | `input_boolean.cv_living_aan` | `sensor.cv_living_temperatuur_stabiel` | RT01 Living Venster; RT04 Living Doorgang |
| Keuken | `input_boolean.cv_keuken_en_tussen_aan` | `sensor.cv_keuken_temperatuur_stabiel` | RT05 KEUKEN VENSTER; RT08 KEUKEN WC |
| Tussen | deelt `input_boolean.cv_keuken_en_tussen_aan` | deelt `sensor.cv_keuken_temperatuur_stabiel` | RT06 TUSSEN DOORGANG; RT07 TUSSEN WC |

De ketelberekening kent drie deltas: Bureel, Living en Keuken. Tussen heeft geen afzonderlijke delta en volgt Keuken.

De stabiele CV-sensoren volgen de ruwe kamersensoren, maar nemen alleen geldige numerieke waarden over. Bij een korte `unknown` of `unavailable` blijft de vorige geldige temperatuur staan.

## Radiatorkraan-entiteiten

| Naam | Entiteit | Home Assistant-ruimte |
|---|---|---|
| RT01 Living Venster | `climate.smart_radiator_thermostat_x_1` | Living |
| RT02 Bureel Venster | `climate.smart_radiator_thermostat_x_4` | Bureel |
| RT03 Bureel Deur | `climate.smart_radiator_thermostat_x_3` | Bureel |
| RT04 Living Doorgang | `climate.smart_radiator_thermostat_x_2` | Living |
| RT05 KEUKEN VENSTER | `climate.smart_radiator_thermostat_x_5` | Keuken |
| RT06 TUSSEN DOORGANG | `climate.smart_radiator_thermostat_x_6` | Tussen |
| RT07 TUSSEN WC | `climate.smart_radiator_thermostat_x_7` | Tussen |
| RT08 KEUKEN WC | `climate.smart_radiator_thermostat_x_8` | Keuken |

Alle apparaten zijn Tado° Smart Radiator Thermostat X. De macro selecteert op de uiteindelijke zichtbare entiteitsnaam die met `RT` begint. Een kraan hernoemen zonder `RT` of naar een andere ruimte verplaatsen verandert dus welke regeling haar aanstuurt.

## Temperatuurhelpers

| Entiteit | Functie | Configuratiebereik |
|---|---|---:|
| `input_number.temp_wens_dag` | doeltemperatuur voor een ingeschakelde zone | 15–24 °C, stap 0,5 °C |
| `input_number.temp_wens_nacht` | doeltemperatuur voor een uitgeschakelde zone | 14–22 °C, stap 0,5 °C |
| `input_number.cv_laatst_verstuurd_control_setpoint` | laatst naar OTGW geschreven aanvoerwaarde | -1–70 °C, stap 1 °C |
| `input_number.cv_laatst_verstuurde_buitentemperatuur` | laatst naar OTGW geschreven buitentemperatuur | -50–60 °C, stap 0,1 °C |
| `input_number.nacht_keuken` (“Nacht Keuken”) | afzonderlijke nachttemperatuur voor Keuken en Tussen | 14–20 °C, stap 0,5 °C |
| Gastenkamer Nacht Temp (UI-helper; niet opgenomen in het package) | voorziene nachttemperatuur voor de gastenkamer | 6–18 °C, stap 0,5 °C |
| `input_datetime.begin_nacht` | tijdstip waarop alle zones naar nacht gaan | tijdwaarde |

Bij de opname van 13 november 2026: dag 21,0 °C, algemene nacht 17,0 °C, Nacht Keuken 17,0 °C, Gastenkamer Nacht Temp 10,0 °C en begin nacht 22:00.

### Afzonderlijke nachtinstelling voor Keuken

In het instellingenscherm bestaat een aparte waarde **Nacht Keuken**. De oudere scripts `settempkeuken_nacht` en `settemptussen_nacht` zijn bedoeld om deze waarde naar Keuken en Tussen te sturen.

In de huidige Tado-regeling gebruikt `script.cv_boost_zone_parameterized` voor een uitgeschakelde zone nog `input_number.temp_wens_nacht`. De dynamische kraanregeling gebruikt dus de algemene nachttemperatuur. De oudere MQTT-scripts gebruiken wel `input_number.nacht_keuken`. In de interne UI-helperopslag heet de unieke sleutel `nact_keuken`, maar de geregistreerde entity-id is `input_number.nacht_keuken`; die entity-id staat ook als helper in het CV-package.

### Gastenkamer

De UI-helper **Gastenkamer Nacht Temp** hoort bij de gastenkamer en staat niet in het CV-package. In die kamer is nog geen Tado-radiatorkraan aanwezig. De bestaande schakelaar `input_boolean.cv_nic` wordt alleen in nachtlogica uitgezet en maakt geen deel uit van de huidige dynamische Tado- en ketelregeling. De verdere regeling van deze zone kan worden toegevoegd wanneer daar een Tado wordt geplaatst.

## Boosthelpers

| Zone | Boostschakelaar | Vastgelegd eindtijdstip |
|---|---|---|
| Bureel | `input_boolean.cv_boost_bureel` | `input_datetime.cv_boost_einde_bureel` |
| Living | `input_boolean.cv_boost_living` | `input_datetime.cv_boost_einde_living` |
| Keuken | `input_boolean.cv_boost_keuken` | `input_datetime.cv_boost_einde_keuken` |

Het aanwezige `script.cv_boost_zone_slim` zet bij een aanroep een zone en boost aan, legt een eindtijd 60 minuten later vast en controleert maximaal 60 minuten. In de onderzochte configuratie is geen directe automatisering gevonden die dit script aanroept; het kan handmatig of vanuit een dashboard worden gestart.

De normale kraanregeling stelt het setpoint proportioneel hoger in wanneer een ruimte achterloopt. Bij meer dan 2 °C tekort gaat het setpoint naar 30 °C en blijft daar tot het tekort 1,5 °C of kleiner is. Dit is het ingestelde Tado-setpoint; de fysieke klepstand is niet als percentage beschikbaar in de geregistreerde entiteitsattributen. Tijdens boost gaan de kranen van de gebooste zone naar 30 °C. De ketelregelaar gebruikt bij actieve boost `input_number.cv_boost_aanvoer_temp`, zolang `input_boolean.cv_ketelsturing_ha_actief` aan staat.

## Overige helpers

- `input_boolean.cv_nacht_bezig`: markeert het nachtvenster waarin de nalooplogica actief is.
- `input_boolean.automatisch_uit`: dagschakelaar voor het automatisch uitschakelen van de verwarming; uitschakelen voorkomt die automatische uitschakeling. De keuze wordt dagelijks naar de standaardtoestand teruggezet.
- `counter.cv_counter`: oudere/nachtlogica; wordt om 22:00 gereset en gebruikt door enkele oudere automatiseringen.
- `input_boolean.cv_nic`: schakelaar voor de gastenkamer; wordt in de nacht-uitacties meegenomen, maar komt wegens het ontbreken van een Tado nog niet voor in de huidige ketel- of Tado-regeling.
- `input_boolean.cv_constantaan`: bestaat, maar is niet gevonden in de huidige regelketen.
- `switch.verwarming_dummy`: templateschakelaar die Bureel, Living en Keuken + Tussen gezamenlijk aan of uit zet.
- `sensor.gemiddelde_actieve_zones`: gemiddelde temperatuur van de ingeschakelde hoofd-zones; valt terug op Living als geen zone aan staat. Deze sensor stuurt de ketel niet.
- `sensor.cv_debug_status`: toont de maximale delta als diagnosewaarde; stuurt de ketel niet.
