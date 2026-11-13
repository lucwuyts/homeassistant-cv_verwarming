# Documentatie centrale verwarming

Deze map beschrijft hoe de centrale verwarming in Home Assistant is opgebouwd en bestuurd. De analyse is gebaseerd op een **read-only** opname van `\\homeassistant\config` op 12 augustus 2026.

## Documenten

- [01-Werking.md](01-Werking.md) — de regeling van warmtevraag tot ketel, stap voor stap.
- [02-Zones-en-entiteiten.md](02-Zones-en-entiteiten.md) — zones, sensoren, radiatorkranen en helpers.
- [03-Automatiseringen-en-bediening.md](03-Automatiseringen-en-bediening.md) — dashboardknoppen, tijdsturing, afwezigheid, boost, bediening en onderhoudsstand.
- [04-Diagnose-en-aandachtspunten.md](04-Diagnose-en-aandachtspunten.md) — controlepunten, foutzoeken en belangrijke observaties.
- [05-Bronnen.md](05-Bronnen.md) — herkomst van de beschreven logica.
- [06-Boost-en-noodstand.md](06-Boost-en-noodstand.md) — actieve boostwerking en noodschakelaar voor HA-ketelsturing.

## Samenvatting

De woningregeling gebruikt drie hoofd-zones: **Bureel**, **Living** en **Keuken + Tussen**. Elke zone heeft een aan/uit-helper. Een ingeschakelde zone gebruikt de dagtemperatuur; een uitgeschakelde zone gebruikt de nachttemperatuur. De grootste positieve afwijking tussen gewenste en gemeten ruimtetemperatuur bepaalt de gevraagde cv-watertemperatuur.

De Tado X-radiatorkranen worden afzonderlijk bijgestuurd. Home Assistant zoekt ze dynamisch per ruimte op aan de hand van een naam die met `RT` begint. De ketel wordt via de OpenTherm Gateway (`otgw`) aangestuurd.

Huidige relevante instellingen bij de opname:

| Instelling | Waarde |
|---|---:|
| Dagtemperatuur | 21,0 °C |
| Nachttemperatuur | 14,0 °C |
| Nacht Keuken | 14,0 °C |
| Gastenkamer Nacht Temp (gastenkamer; nog te herbekijken) | 10,0 °C |
| Begin nacht | 22:00 |

Deze waarden zijn instelbare helpers en kunnen later wijzigen.

In het instellingenscherm staan daarnaast dagschakelaars voor **Automatisch Uit** en **CV: eenmalige ochtendstart**. De eerste bepaalt of de verwarming automatisch mag worden uitgeschakeld; de tweede plant een eenmalige start om 06:00 wanneer de ochtendstart gewenst is.

> Let op: de map `packages/boiler_controller` bestuurt een afzonderlijke elektrische warmwaterboiler. Die is niet de centrale-verwarmingsketel en valt daarom buiten deze documentatie.
