# Bronnen en afbakening

## Onderzochte configuratie

De documentatie is samengesteld uit de volgende read-only bronnen op `\\homeassistant\config`:

| Bron | Relevante inhoud |
|---|---|
| `configuration.yaml` | includes van automations, scripts, templates en packages |
| `automations.yaml` | zone-, tijd-, afwezigheids-, OpenTherm-, boost- en onderhoudsautomatiseringen |
| `scripts.yaml` | dynamische Tado-kraanregeling en boostscript |
| `custom_templates/rt_tools.jinja` | dynamische selectie van RT-klimaatentiteiten per ruimte |
| `templates/cv.yaml` | gezamenlijke verwarmingsschakelaar en gemiddelde actieve zones |
| `templates/debug.yaml` | CV-deltadiagnose |
| `templates/tado.yaml` | twee Tado-setpointsensoren |
| `.storage/lovelace.lovelace` | dashboardknoppen, kleuren, enkele-tikactie en dubbele-tikactie voor boost |
| `.storage/input_number` | grenzen en namen van temperatuurhelpers |
| `.storage/input_boolean` | zone-, boost- en onderhoudshelpers |
| `.storage/input_datetime` | begin nacht en boost-eindtijden |
| `.storage/counter` | CV Counter-definitie |
| `.storage/core.entity_registry` | entiteitsnamen en apparaatkoppelingen |
| `.storage/core.device_registry` | Tado-apparaatnamen en ruimtes |
| `.storage/core.area_registry` | Home Assistant-ruimtes |
| `.storage/core.restore_state` | laatst herstelde waarden en automatiseringsstatus bij de opname |

## Afbakening

- Er is niets gewijzigd in `\\homeassistant\config`.
- Geheimen en persoonsgegevens uit de configuratie zijn niet in deze documentatie opgenomen.
- De grote historie-database is niet nodig geweest voor het beschrijven van de statische werking.
- `packages/boiler_controller` gaat over een elektrische warmwaterboiler en is bewust niet als centrale verwarming beschreven.
- Status- en instelwaarden zijn een momentopname van 12 augustus 2026; de logica is gebaseerd op de configuratie zoals die toen aanwezig was.

## Betrouwbaarheidsnotitie

De documenten beschrijven wat uit de Home Assistant-configuratie en de laatst herstelde staten kan worden afgeleid. Ketelinterne instellingen, hydraulische opbouw, bedrading en bedieningen buiten Home Assistant zijn niet rechtstreeks zichtbaar en kunnen het werkelijke gedrag verder beïnvloeden.
