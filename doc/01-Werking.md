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

De actieve automatisering `automation.cv_control_setpoint_dynamisch` controleert iedere 30 seconden en na een Home Assistant-start de warmtevraag. Warmtevraag start bij meer dan 0,5 °C afwijking en blijft actief tot de afwijking 0,3 °C of kleiner wordt. Deze hysterese voorkomt aan/uit-klapperen door sensorafronding op 0,1 °C.

| Situatie | Actie |
|---|---|
| `cv_ketelsturing_ha_actief` uit | OpenTherm-setpoint 0 °C; rampstatus wordt gewist |
| Boost actief | `input_number.cv_boost_aanvoer_temp`; boost opent de gekozen kranen |
| Geen lopende vraag en grootste delta `<= 0,5 °C` | Geen nieuwe warmtevraag |
| Lopende vraag en grootste delta `<= 0,3 °C` | OpenTherm-setpoint 0 °C en rampstatus wissen |
| Nieuwe warmtevraag boven 0,5 °C | Kranen eerst proportioneel hoger instellen; daarna start de aanvoer op 30 °C |
| Na vijf minuten geen kamerrespons van minstens 0,2 °C | Aanvoer met 2 °C verhogen, tot de limiet die past bij de warmtevraag |
| Kamerrespons van minstens 0,2 °C | Aanvoer vasthouden en een nieuwe meetperiode starten |

De maximale aanvoer is 36 °C bij een delta tot en met 0,75 °C, 42 °C tot en met 1,25 °C, 50 °C tot en met 2 °C en 60 °C bij grotere warmtevraag. Als de vraag afneemt, verlaagt de regelaar de limiet direct. De kamerrespons wordt alleen gemeten voor zones die nog warmtevraag hebben. Een actief OpenTherm-setpoint wordt periodiek vernieuwd om te voorkomen dat de OTGW-override verloopt. Bij einde warmtevraag wordt de override met setpoint 0 °C vrijgegeven.

## 4. Radiatorkranen

`automation.status_cv` loopt elke minuut en roept voor Bureel, Living, Tussen en Keuken het script `script.cv_boost_zone_parameterized` aan. Ook deze kraanregeling gebruikt de stabiele CV-temperatuursensoren.

Het script zoekt per Home Assistant-ruimte alle `climate`-entiteiten waarvan de zichtbare naam met `RT` begint. Daardoor is de ruimtetoewijzing en naamgeving onderdeel van de regeling.

Bij normale warmtevraag stelt het script de kraan geleidelijk hoger in: `basis + 3 × delta`, met een maximum van 30 °C. Bij een tekort groter dan 2 °C gaat de kraan volledig open naar 30 °C. Dat commando blijft staan tot het tekort 1,5 °C of kleiner is; daarna verlaagt de instelling maximaal 0,5 °C per minuut. Stijgingen worden meteen toegepast. Zo loopt de kraan niet abrupt terug wanneer de warmtevraag afneemt. Zonder warmtevraag keert de instelling geleidelijk terug naar de basis. Tijdens boost gaan de kranen van de gebooste zone eveneens volledig naar 30 °C; Tussen volgt de Keuken-boost.

Een kraansetpoint-wijziging kleiner dan 0,2 °C wordt niet verstuurd. Bij een ongewijzigd setpoint wordt de climate-service overgeslagen.

## 5. Buitentemperatuur en gateway

`automation.buiten_temp_cv` stuurt de temperatuur uit `weather.wuytskes` naar de OpenTherm Gateway wanneer de waarde op 0,1 °C is veranderd. De laatst verstuurde waarde wordt bewaard in `input_number.cv_laatst_verstuurde_buitentemperatuur`; een ontbrekende of ongeldige bron wordt niet verzonden.

De dynamische ketelregelaar blijft iedere 30 seconden de warmtevraag berekenen en rondt het `set_control_setpoint` af op hele graden. Een gewijzigd setpoint wordt direct verstuurd. Een aparte keepalive-automatisering herhaalt een actief setpoint vanaf 8 °C iedere minuut, zolang de regelaar in de afgelopen minuut nog actief was en dezelfde waarde berekend heeft. Setpoint 0 wordt alleen bij een wijziging verstuurd. De actuele en laatst verstuurde waarden staan in `input_number.cv_berekend_control_setpoint` en `input_number.cv_laatst_verstuurd_control_setpoint`.

De OTGW-voeding wordt bovendien ieder uur 59 seconden uit- en daarna weer ingeschakeld door de afzonderlijke Home Assistant-automatisering **Herstart OTGW**. Deze automatisering staat bewust buiten het verwarmingspackage, omdat ze losstaat van de CV-regeling.

## 6. Wat bepaalt uiteindelijk of een radiator warmte krijgt?

Een radiator krijgt effectief warmte wanneer beide voorwaarden samenkomen:

- zijn Tado-kraan staat voldoende open door het berekende kraansetpoint;
- de ketel levert warm cv-water doordat minstens één hoofd-zone een positieve warmtevraag heeft.

Keuken en Tussen delen één zonehelper en één externe temperatuursensor. Hun kranen worden wel per Home Assistant-ruimte gevonden, maar voor beide wordt de keukentemperatuur gebruikt.
