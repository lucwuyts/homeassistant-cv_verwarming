# Werking van de centrale verwarming

## 1. Overzicht van de regelketen

De verwarming werkt in vier lagen:

1. De zonehelpers bepalen per hoofd-zone of dag- of nachttemperatuur gewenst is.
2. Losse temperatuursensoren meten de werkelijke kamertemperatuur.
3. Home Assistant stuurt de Tado X-radiatorkranen elke minuut bij.
4. Home Assistant stuurt bij warmtevraag eerst de kranen open en houdt daarna de cv-aanvoer via OpenTherm laag; alleen zonder ruimteverwarming wordt die langzaam verhoogd.

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

Bij de opname van 13 november 2026 waren deze waarden respectievelijk 21,0 °C en 17,0 °C. “Uit” betekent dus technisch niet noodzakelijk vorstvrij of volledig dicht: de zone wordt naar de nachttemperatuur geregeld.

De temperatuurafwijking of `delta` is:

```text
delta = gewenste ruimtetemperatuur - gemeten ruimtetemperatuur
```

De actieve ketelregelaar neemt de grootste delta van Bureel, Living en Keuken. Daarvoor gebruikt hij stabiele CV-temperatuursensoren die hun vorige waarde vasthouden wanneer de onderliggende kamersensor kort `unknown` of `unavailable` wordt.

De NEST thermostaat staat in de living, en kan met de dial de temperatuur  temp_wens_dag  aanpassen.  Dit gebeurt enkel indien de temperatuur >= 19° is.   Als de ingestelde temperatuur lager dan 19° wordt gezet, wordt de verwarming uitgeschakeld.  (1 minuut wachttijd voor beide acties)

Als de NEST uit wordt gezet, wordt ook de verwarming Living uitgezet (2 minuten wachttijd)

Als de NEST aan wordt gezet, dan wordt de verwarming living aangezet (2 minuten wachttijd)





## 3. Ketelsturing via OpenTherm

De actieve automatisering `automation.cv_control_setpoint_dynamisch` controleert iedere 30 seconden en na een Home Assistant-start de warmtevraag. Een zone telt mee bij een afwijking groter dan 0,5 °C. Die kleine dode band voorkomt dat sensorruis de ketel laat aanslaan.

| Situatie | Actie |
|---|---|
| `cv_ketelsturing_ha_actief` uit | OpenTherm-setpoint 0 °C; rampstatus wordt gewist |
| Boost actief | `input_number.cv_boost_aanvoer_temp`; boost opent de gekozen kranen |
| Geen boost en grootste delta `<= 0,5 °C` | OpenTherm-setpoint 0 °C en rampstatus wissen |
| Nieuwe warmtevraag boven 0,5 °C | Eerst kranen van vragende zones naar 30 °C, daarna OpenTherm-setpoint 30 °C |
| Na vijf minuten geen kamerrespons van minstens 0,2 °C | Aanvoer met 2 °C verhogen, tot maximaal 60 °C |
| Kamerrespons van minstens 0,2 °C | Aanvoer vasthouden en een nieuwe meetperiode starten |

De kamerrespons wordt alleen gemeten voor zones die nog warmtevraag hebben. Elke 30 seconden wordt het huidige OpenTherm-setpoint opnieuw geschreven; dit voorkomt dat de OTGW-aanvraag verloopt. Bij einde warmtevraag wordt de override met setpoint 0 °C vrijgegeven.

## 4. Radiatorkranen

`automation.status_cv` loopt elke minuut en roept voor Bureel, Living, Tussen en Keuken het script `script.cv_boost_zone_parameterized` aan. Ook deze kraanregeling gebruikt de stabiele CV-temperatuursensoren.

Het script zoekt per Home Assistant-ruimte alle `climate`-entiteiten waarvan de zichtbare naam met `RT` begint. Daardoor is de ruimtetoewijzing en naamgeving onderdeel van de regeling.

Bij warmtevraag groter dan 0,5 °C zet het script de kranen van die zone op 30 °C zodat ze eerst voldoende openen. Zonder warmtevraag keren ze terug naar de basis dag- of nachttemperatuur. Tijdens boost gaan de kranen van de gebooste zone eveneens naar 30 °C; Tussen volgt de Keuken-boost.

De normale kraanregeling en de ketelregeling hebben dezelfde dode band van 0,5 °C. Een kraansetpoint-wijziging kleiner dan 0,2 °C wordt niet verstuurd.

## 5. Buitentemperatuur en gateway

Iedere minuut stuurt `automation.buiten_temp_cv` de temperatuur uit `weather.wuytskes` als buitentemperatuur naar de OpenTherm Gateway. De waarde wordt met `float(0)` omgezet: bij een ontbrekende of ongeldige bron kan daardoor 0 °C worden verzonden.

De OTGW-voeding wordt bovendien ieder uur 59 seconden uit- en daarna weer ingeschakeld door `automation.new_automation` (`Herstart OTGW`).

## 6. Wat bepaalt uiteindelijk of een radiator warmte krijgt?

Een radiator krijgt effectief warmte wanneer beide voorwaarden samenkomen:

- zijn Tado-kraan staat voldoende open door het berekende kraansetpoint;
- de ketel levert warm cv-water doordat minstens één hoofd-zone een positieve warmtevraag heeft.

Keuken en Tussen delen één zonehelper en één externe temperatuursensor. Hun kranen worden wel per Home Assistant-ruimte gevonden, maar voor beide wordt de keukentemperatuur gebruikt.
