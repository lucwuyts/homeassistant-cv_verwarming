# Verwarmingspackage beheren

De centrale verwarmingsregeling staat apart in `packages/cv_heating.yaml`. Home Assistant laadt packages via de bestaande instelling `homeassistant: packages: !include_dir_named packages`. De extra macro voor Tado-radiatorkranen staat in `custom_templates/rt_tools.jinja`.

Het package bevat alleen CV-gerelateerde automatiseringen, scripts, templates en gebruikte helpers. De rest van `automations.yaml`, `scripts.yaml`, `mqtt.yaml` en andere Home Assistant-bestanden staat niet in deze repository en wordt niet gekopieerd of overschreven. `configuration.yaml` is al ingesteld om packages te laden en wordt niet aangepast.

## Eenmalige migratie van helpers

De helpers zijn tot nu toe via de Home Assistant UI aangemaakt. Hun definities zijn nu declaratief opgenomen in het package. Voordat het package voor het eerst wordt geactiveerd, moeten de corresponderende UI-helpers worden verwijderd om dubbele definities te voorkomen. Dit is een eenmalige migratie; daarna worden de helpers samen met de CV-regeling vanuit YAML beheerd.

Voer de migratie in een onderhoudsvenster uit. Hiervoor is lokaal Python met `ruamel.yaml` nodig (`python -m pip install -r requirements.txt`). Eerst laat je het migratiescript de exacte CV-blokken zien die het herkent:

```powershell
python .\scripts\Migrate-CvToPackage.py
```

Het hoort 20 CV-automatiseringen en 8 CV-scripts te tonen. Het stopt zonder bestanden te wijzigen als de live-bestanden daarvan afwijken. Voer daarna uit:

1. Maak eerst een volledige Home Assistant-back-up.
2. Noteer de huidige waarden van de CV-helpers. De YAML-definities laten `initial` weg waar mogelijk, zodat Home Assistant de laatst herstelde waarde blijft gebruiken.
3. Publiceer alleen het package en de kraanmacro met de stappen hieronder. Herstart HA nog niet.
4. Verwijder via **Instellingen → Apparaten & diensten → Helpers** de UI-definities die ook in het package staan: CV-zone-, boost-, nacht- en onderhoudsschakelaars, dag/nachttemperatuur, Nacht Keuken, boost-aanvoertemperatuur, begin-nacht, boost-eindtijden en `CV Counter`.
5. Voer `python .\scripts\Migrate-CvToPackage.py --apply` uit. Het maakt tijdgestempelde backups van `automations.yaml` en `scripts.yaml` en verwijdert uitsluitend de herkende CV-automatiseringen en de twee CV-scripts. `configuration.yaml`, MQTT en de overige automatiseringen/scripts blijven ongemoeid.
6. Controleer de YAML-configuratie en herstart Home Assistant. Controleer daarna of de entity-id's gelijk zijn gebleven en of de ingestelde temperaturen en zone-statussen hersteld zijn.

Verwijder geen helpers die niet in `packages/cv_heating.yaml` zijn gedefinieerd. De ongebruikte gastenkamer-helper `Gastenkamer Nacht Temp` blijft bijvoorbeeld buiten het package.

