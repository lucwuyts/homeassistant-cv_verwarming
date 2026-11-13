# Bronnen en afbakening

## Onderzochte configuratie

De documentatie is samengesteld uit de volgende bronnen op `\\homeassistant\config`. De actuele CV-configuratie is geïsoleerd in `packages/cv_heating.yaml`; alleen de benodigde macro staat aanvullend in `custom_templates/rt_tools.jinja`.

| Bron | Relevante inhoud |
|---|---|
| `configuration.yaml` | includes van automations, scripts, templates en packages |
| `automations.yaml` | zone-, tijd-, afwezigheids-, OpenTherm-, boost- en onderhoudsautomatiseringen |
| `scripts.yaml` | dynamische Tado-kraanregeling en boostscript |
| `custom_templates/rt_tools.jinja` | dynamische selectie van RT-klimaatentiteiten per ruimte |
| `templates/cv.yaml` | gezamenlijke verwarmingsschakelaar en gemiddelde actieve zones |
| `templates/debug.yaml` | CV-deltadiagnose |
| `templates/tado.yaml` | twee Tado-setpointsensoren |
| `.storage/*` (read-only onderzocht) | Lovelace-dashboard, UI-helperdefinities, registries en herstelde waarden; niet opgenomen in Git |

## Afbakening

- De CV-inventarisatie van 13 november 2026 las uit `\\homeassistant\config`. Er is niets naar HA gepubliceerd.
- Geheimen en persoonsgegevens uit de configuratie zijn niet in deze documentatie opgenomen.
- De grote historie-database is niet nodig geweest voor het beschrijven van de statische werking.
- `packages/boiler_controller` gaat over een elektrische warmwaterboiler en is bewust niet als centrale verwarming beschreven.
- Status- en instelwaarden in deze documenten zijn momentopnamen; de CV-logica staat in het package. Niet-CV-configuratie is niet in deze repository opgenomen.

## Betrouwbaarheidsnotitie

De documenten beschrijven wat uit de Home Assistant-configuratie en de laatst herstelde staten kan worden afgeleid. Ketelinterne instellingen, hydraulische opbouw, bedrading en bedieningen buiten Home Assistant zijn niet rechtstreeks zichtbaar en kunnen het werkelijke gedrag verder beïnvloeden.
