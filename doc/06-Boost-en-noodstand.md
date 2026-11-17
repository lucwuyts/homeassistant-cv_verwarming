# Boost en noodstand

Deze werking is actief in Home Assistant sinds 23 augustus 2026.

## Helpers

| Helper | Functie | Normale stand |
|---|---|---|
| `input_number.cv_boost_aanvoer_temp` | OpenTherm-aanvoertemperatuur tijdens boost | 60 °C bij de opname van 13 november 2026 |
| `input_boolean.cv_ketelsturing_ha_actief` | bepaalt of Home Assistant setpoints naar de ketel mag sturen | aan |

`input_boolean.cv_ketelsturing_ha_actief` is de noodschakelaar. Zet deze uit wanneer een gewone noodthermostaat de ketel moet overnemen. Home Assistant blijft dan wel de overige automatiseringen uitvoeren, maar stuurt setpoint 0 °C om de OpenTherm-override vrij te geven.

## Boostgedrag

| Zone | Boosthelper | Kranen tijdens boost | Ketelsetpoint tijdens boost |
|---|---|---|---:|
| Bureel | `input_boolean.cv_boost_bureel` | Bureel volledig open, setpoint 30 °C | `cv_boost_aanvoer_temp` |
| Living | `input_boolean.cv_boost_living` | Living volledig open, setpoint 30 °C | `cv_boost_aanvoer_temp` |
| Keuken + Tussen | `input_boolean.cv_boost_keuken` | Keuken en Tussen volledig open, setpoint 30 °C | `cv_boost_aanvoer_temp` |

Zonder boost geldt de normale proportionele regeling: bij een zone-afwijking boven 0,5 °C wordt de kraan hoger ingesteld op basis van de grootte van het tekort. Bij 0,5 °C tekort is dat 1,5 °C boven de normale dag- of nachtbasis. Bij meer dan 2 °C tekort gaat de kraan naar 30 °C en blijft daar tot het tekort 1,5 °C of kleiner is; bij boost gaat de kraan meteen naar 30 °C. De aanvoer start op 30 °C. Alleen als de ruimtetemperatuur vijf minuten lang niet minstens 0,2 °C stijgt, wordt de aanvoer met 2 °C verhoogd. De limiet is 36 °C bij maximaal 0,75 °C warmtevraag, 42 °C tot 1,25 °C, 50 °C tot 2 °C en anders 60 °C. Warmtevraag start boven 0,5 °C en blijft actief tot de afwijking 0,3 °C of kleiner is, zodat afronding van de sensor niet voor schakelen zorgt. Bij geen vraag wordt de OpenTherm-override vrijgegeven met 0 °C.

De actieve automatisering is `automation.cv_control_setpoint_dynamisch`. Ze berekent iedere 30 seconden het actuele setpoint en schrijft wijzigingen meteen. `CV Control Setpoint Keepalive` herhaalt een actief setpoint vanaf 8 °C iedere minuut zolang de setpointregelaar recent nog actief is; zo blijft de OTGW-override geldig zonder die wijzigingsactie iedere 30 seconden te herhalen.

| Situatie | OpenTherm-setpoint vanuit Home Assistant |
|---|---:|
| `cv_ketelsturing_ha_actief` uit | 0 °C (override vrijgeven) |
| Boost actief | `input_number.cv_boost_aanvoer_temp` |
| Geen lopende vraag en delta `<= 0,5 °C` | 0 °C (nog geen warmtevraag) |
| Lopende vraag en delta `<= 0,3 °C` | 0 °C (vraag beëindigd) |
| Nieuwe warmtevraag | 30 °C, nadat vragende kranen proportioneel hoger zijn ingesteld |
| Geen meetbare kamerrespons na vijf minuten | +2 °C, begrensd op de limiet voor de huidige warmtevraag |
| Kamer reageert minstens 0,2 °C | huidig setpoint vasthouden |

## Controle

Gebruik deze controles na een wijziging of bij twijfel:

1. zet `input_boolean.cv_ketelsturing_ha_actief` uit;
2. controleer in OTGW logging dat Home Assistant geen nieuwe `Control setpoint` writes doet;
3. test dat de gewone noodthermostaat warmtevraag kan maken zonder door Home Assistant te worden teruggezet;
4. zet `input_boolean.cv_ketelsturing_ha_actief` weer aan;
5. start boost op één zone;
6. controleer dat alleen de kranen van die zone naar 30 °C gaan;
7. controleer dat OTGW tijdens boost ongeveer dit toont:

```text
   Write-Data Control setpoint: 60.00
```

De software-noodstand vervangt geen fysieke test. Controleer apart of de noodthermostaat elektrisch en OpenTherm-technisch correct kan overnemen.
