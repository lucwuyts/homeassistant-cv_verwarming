# Boost en noodstand

Deze werking is actief in Home Assistant sinds 23 augustus 2026.

## Helpers

| Helper | Functie | Normale stand |
|---|---|---|
| `input_number.cv_boost_aanvoer_temp` | OpenTherm-aanvoertemperatuur tijdens boost | 65 °C |
| `input_boolean.cv_ketelsturing_ha_actief` | bepaalt of Home Assistant setpoints naar de ketel mag sturen | aan |

`input_boolean.cv_ketelsturing_ha_actief` is de noodschakelaar. Zet deze uit wanneer een gewone noodthermostaat de ketel moet overnemen. Home Assistant blijft dan wel de overige automatiseringen uitvoeren, maar `automation.cv_control_setpoint_dynamisch` stuurt geen nieuw `opentherm_gw.set_control_setpoint` meer naar de OTGW.

## Boostgedrag

| Zone | Boosthelper | Kranen tijdens boost | Ketelsetpoint tijdens boost |
|---|---|---|---:|
| Bureel | `input_boolean.cv_boost_bureel` | Bureel volledig open, setpoint 30 °C | `cv_boost_aanvoer_temp` |
| Living | `input_boolean.cv_boost_living` | Living volledig open, setpoint 30 °C | `cv_boost_aanvoer_temp` |
| Keuken + Tussen | `input_boolean.cv_boost_keuken` | Keuken en Tussen volledig open, setpoint 30 °C | `cv_boost_aanvoer_temp` |

Als geen boost actief is, gebruikt de ketelregelaar opnieuw de normale delta-tabel. Als `cv_ketelsturing_ha_actief` uit staat, heeft boost geen effect op het ketelsetpoint omdat Home Assistant dan niets naar de OTGW schrijft.

## Normale ketelsturing

De actieve automatisering is `automation.cv_control_setpoint_dynamisch`. Zij draait iedere twee minuten.

| Situatie | OpenTherm-setpoint vanuit Home Assistant |
|---|---:|
| `cv_ketelsturing_ha_actief` uit | geen nieuw HA-setpoint |
| Boost actief | `input_number.cv_boost_aanvoer_temp` |
| Geen boost en `max_delta <= 0 °C` | 20 °C |
| Geen boost en `max_delta > 0 en <= 0,5 °C` | 42 °C |
| Geen boost en `max_delta > 0,5 en <= 1 °C` | 48 °C |
| Geen boost en `max_delta > 1 en <= 2 °C` | 55 °C |
| Geen boost en `max_delta > 2 °C` | 60 °C |

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
Write-Data Control setpoint: 65.00
```

De software-noodstand vervangt geen fysieke test. Controleer apart of de noodthermostaat elektrisch en OpenTherm-technisch correct kan overnemen.
