# Werking van de centrale verwarming

## 1. Overzicht van de regelketen

De verwarming werkt in vier lagen:

1. De zonehelpers bepalen per hoofd-zone of dag- of nachttemperatuur gewenst is.
2. Losse temperatuursensoren meten de werkelijke kamertemperatuur.
3. Home Assistant stuurt de Tado X-radiatorkranen elke minuut bij.
4. Home Assistant berekent elke twee minuten de benodigde cv-watertemperatuur en stuurt die via de OpenTherm Gateway naar de ketel.

Kort weergegeven:

```text
zone aan/uit + dag/nacht-doel + externe kamertemperatuur
                         |
              +----------+-----------+
              |                      |
       Tado-kraanregeling      grootste warmtevraag
       (iedere minuut)         van alle hoofd-zones
              |                      |
      opening per radiator     OpenTherm-setpoint
                                     |
                                   ketel
```

## 2. Gewenste temperatuur per zone

Voor iedere hoofd-zone wordt een doeltemperatuur gekozen:

- zonehelper **aan** → `input_number.temp_wens_dag`;
- zonehelper **uit** → `input_number.temp_wens_nacht`.

Bij de opname waren deze waarden respectievelijk 21,0 °C en 14,0 °C. “Uit” betekent dus technisch niet noodzakelijk vorstvrij of volledig dicht: de zone wordt naar de nachttemperatuur geregeld.

De temperatuurafwijking of `delta` is:

```text
delta = gewenste ruimtetemperatuur - gemeten ruimtetemperatuur
```

De actieve ketelregelaar neemt de grootste delta van Bureel, Living en Keuken. Daarvoor gebruikt hij stabiele CV-temperatuursensoren die hun vorige waarde vasthouden wanneer de onderliggende kamersensor kort `unknown` of `unavailable` wordt.

De NEST thermostaat staat in de living, en kan met de dial de temperatuur  temp_wens_dag  aanpassen.  Dit gebeurt enkel indien de temperatuur >= 19° is.   Als de ingestelde temperatuur lager dan 19° wordt gezet, wordt de verwarming uitgeschakeld.  (1 minuut wachttijd voor beide acties)

Als de NEST uit wordt gezet, wordt ook de verwarming Living uitgezet (2 minuten wachttijd)

Als de NEST aan wordt gezet, dan wordt de verwarming living aangezet (2 minuten wachttijd)





## 3. Ketelsturing via OpenTherm

De actieve automatisering `automation.cv_control_setpoint_dynamisch` draait iedere twee minuten. Zij gebruikt de grootste zone-delta en kiest het OpenTherm-regelsetpoint. Als `input_boolean.cv_ketelsturing_ha_actief` uit staat, stuurt deze automatisering geen nieuw setpoint naar de OTGW.

| Situatie | OpenTherm-setpoint |
|---|---:|
| `cv_ketelsturing_ha_actief` uit | geen nieuw HA-setpoint |
| Boost actief | `input_number.cv_boost_aanvoer_temp` |
| Geen boost en grootste delta `<= 0 °C` | 20 °C |
| Geen boost en grootste delta `> 0 en <= 0,5 °C` | 42 °C |
| Geen boost en grootste delta `> 0,5 en <= 1 °C` | 48 °C |
| Geen boost en grootste delta `> 1 en <= 2 °C` | 55 °C |
| Geen boost en grootste delta `> 2 °C` | 60 °C |

Dit setpoint wordt verstuurd met `opentherm_gw.set_control_setpoint` naar gateway `otgw`. De automatisering schrijft daarnaast de berekende warmtevraag en CH-status in het logboek.

Bij geen positieve warmtevraag wordt 20 °C verzonden, niet 0 °C. De feitelijke ketelreactie hangt daarnaast af van de OpenTherm-ketel/gateway en zijn eigen beveiligingen.



## 4. Radiatorkranen

`automation.status_cv` loopt elke minuut en roept voor Bureel, Living, Tussen en Keuken het script `script.cv_boost_zone_parameterized` aan. Ook deze kraanregeling gebruikt de stabiele CV-temperatuursensoren.

Het script zoekt per Home Assistant-ruimte alle `climate`-entiteiten waarvan de zichtbare naam met `RT` begint. Daardoor is de ruimtetoewijzing en naamgeving onderdeel van de regeling.

Per kraan berekent het script normaal:

```text
basis = dag- of nachttemperatuur
delta = basis - externe kamertemperatuur
bias  = kraantemperatuur - externe kamertemperatuur, begrensd tussen 0 en 2 °C

als delta <= 0:
    kraansetpoint = basis
anders:
    kraansetpoint = basis + 1,6 × delta + 0,6 × bias
```

Tijdens boost wordt dit overschreven naar 30 °C voor de kranen van de gebooste zone. Tussen volgt daarbij de Keuken-boost.

Een wijziging kleiner dan 0,2 °C wordt niet doorgevoerd; het bestaande setpoint blijft dan staan. Dit vermindert kleine, voortdurende bijstellingen.

De bias compenseert dat een radiatorkraan vlak bij de radiator vaak warmer meet dan de losse kamersensor. Een negatieve bias wordt niet toegepast; een positieve bias is maximaal 2 °C.

Het script heeft een extra parameter gekregen "hoge_prioriteit".   Voor keuken (en tussen) wordt die altijd als True meegegeven.  Dit heeft het effect dat die ruimte even snel opwarmt als met de Boost parameter.



## 5. Buitentemperatuur en gateway

Iedere minuut stuurt `automation.buiten_temp_cv` de temperatuur uit `weather.wuytskes` als buitentemperatuur naar de OpenTherm Gateway. De waarde wordt met `float(0)` omgezet: bij een ontbrekende of ongeldige bron kan daardoor 0 °C worden verzonden.

De OTGW-voeding wordt bovendien ieder uur 59 seconden uit- en daarna weer ingeschakeld door `automation.new_automation` (`Herstart OTGW`).

## 6. Wat bepaalt uiteindelijk of een radiator warmte krijgt?

Een radiator krijgt effectief warmte wanneer beide voorwaarden samenkomen:

- zijn Tado-kraan staat voldoende open door het berekende kraansetpoint;
- de ketel levert warm cv-water doordat minstens één hoofd-zone een positieve warmtevraag heeft.

Keuken en Tussen delen één zonehelper en één externe temperatuursensor. Hun kranen worden wel per Home Assistant-ruimte gevonden, maar voor beide wordt de keukentemperatuur gebruikt.
