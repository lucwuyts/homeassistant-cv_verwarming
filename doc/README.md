# Documentatie centrale verwarming

Deze repository houdt alleen de centrale verwarmingssturing apart bij in [`../packages/cv_heating.yaml`](../packages/cv_heating.yaml), met de benodigde kraanmacro in [`../custom_templates/rt_tools.jinja`](../custom_templates/rt_tools.jinja). Andere Home Assistant-configuratie, zoals MQTT, staat niet in deze repository en wordt niet door de synchronisatiescripts aangeraakt.

## Documenten

- [01-Werking.md](01-Werking.md) — de regeling van warmtevraag tot ketel, stap voor stap.
- [02-Zones-en-entiteiten.md](02-Zones-en-entiteiten.md) — zones, sensoren, radiatorkranen en helpers.
- [03-Automatiseringen-en-bediening.md](03-Automatiseringen-en-bediening.md) — dashboardknoppen, tijdsturing, afwezigheid, boost, bediening en onderhoudsstand.
- [04-Diagnose-en-aandachtspunten.md](04-Diagnose-en-aandachtspunten.md) — controlepunten, foutzoeken en belangrijke observaties.
- [05-Bronnen.md](05-Bronnen.md) — herkomst van de beschreven logica.
- [06-Boost-en-noodstand.md](06-Boost-en-noodstand.md) — actieve boostwerking en noodschakelaar voor HA-ketelsturing.
- [07-Beheer-en-synchronisatie.md](07-Beheer-en-synchronisatie.md) — configuratie bijwerken, publiceren en omgaan met helpers.

## Samenvatting

De woningregeling gebruikt drie hoofd-zones: **Bureel**, **Living** en **Keuken + Tussen**. Elke zone heeft een aan/uit-helper. Een ingeschakelde zone gebruikt de dagtemperatuur; een uitgeschakelde zone gebruikt de nachttemperatuur. Bij ruimtetekort stelt de regeling de kranen geleidelijk hoger in. De ketel begint op 30 °C en verhoogt de aanvoer alleen zonder meetbare ruimteverwarming; bij kleine temperatuurtekorten geldt een lagere aanvoerlimiet. Hysterese voorkomt schakelen door sensorafronding.

De Tado X-radiatorkranen worden afzonderlijk bijgestuurd. Home Assistant zoekt ze dynamisch per ruimte op aan de hand van een naam die met `RT` begint. De ketel wordt via de OpenTherm Gateway (`otgw`) aangestuurd.

Huidige relevante instellingen bij de opname:

| Instelling | Waarde |
|---|---:|
| Dagtemperatuur | 21,0 °C |
| Nachttemperatuur | 17,0 °C |
| Nacht Keuken | 17,0 °C |
| Gastenkamer Nacht Temp (gastenkamer; nog te herbekijken) | 10,0 °C |
| Begin nacht | 22:00 |

Deze waarden zijn instelbare helpers en kunnen later wijzigen.

In het instellingenscherm staan daarnaast dagschakelaars voor **Automatisch Uit** en **CV: eenmalige ochtendstart**. De eerste bepaalt of de verwarming automatisch mag worden uitgeschakeld; de tweede plant een eenmalige start om 06:00 wanneer de ochtendstart gewenst is.
