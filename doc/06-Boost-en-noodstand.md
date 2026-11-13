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

Zonder boost geldt de normale valve-first regeling: bij een zone-afwijking boven 0,5 °C openen eerst de kranen, daarna start de aanvoer op 30 °C. Alleen als de ruimtetemperatuur vijf minuten lang niet minstens 0,2 °C stijgt, wordt de aanvoer met 2 °C verhoogd tot maximaal 60 °C. Zodra een kamer reageert, blijft de huidige aanvoer staan en start een nieuwe meetperiode. Bij geen vraag wordt de OpenTherm-override vrijgegeven met 0 °C.

De actieve automatisering is `automation.cv_control_setpoint_dynamisch`. Zij schrijft iedere 30 seconden het actuele setpoint naar de OTGW, omdat de OpenTherm Gateway de override kan laten verlopen.

| Situatie | OpenTherm-setpoint vanuit Home Assistant |
|---|---:|
| `cv_ketelsturing_ha_actief` uit | 0 °C (override vrijgeven) |
| Boost actief | `input_number.cv_boost_aanvoer_temp` |
| Geen boost en delta `<= 0,5 °C` | 0 °C (geen warmtevraag) |
| Nieuwe warmtevraag | 30 °C, nadat vragende kranen eerst open zijn gestuurd |
| Geen meetbare kamerrespons na vijf minuten | +2 °C, maximaal 60 °C |
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
