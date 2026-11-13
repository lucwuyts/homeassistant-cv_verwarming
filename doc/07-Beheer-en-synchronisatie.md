# Verwarmingspackage beheren

De centrale verwarmingsregeling staat apart in `packages/cv_heating.yaml`. Home Assistant laadt packages via de bestaande instelling `homeassistant: packages: !include_dir_named packages`. De extra macro voor Tado-radiatorkranen staat in `custom_templates/rt_tools.jinja`.

Het package bevat alleen CV-gerelateerde automatiseringen, scripts, templates en gebruikte helpers. De rest van `automations.yaml`, `scripts.yaml`, `mqtt.yaml` en andere Home Assistant-bestanden staat niet in deze repository en wordt niet gekopieerd of overschreven. `configuration.yaml` is al ingesteld om packages te laden en wordt niet aangepast.

## Eenmalige migratie van helpers

De helpers waren eerder via de Home Assistant UI aangemaakt. Hun definities zijn nu declaratief opgenomen in het package. Deze migratie is op 13 november 2026 uitgevoerd: de corresponderende UI-helpers zijn verwijderd, waarna de YAML-definities na een herstart dezelfde entity-id's hebben aangemaakt. Vanaf nu worden helpers en CV-regeling vanuit YAML beheerd.

Voor een nieuwe installatie is lokaal Python met `ruamel.yaml` nodig (`python -m pip install -r requirements.txt`). Het migratiescript is al uitgevoerd op de live configuratie. Ter controle kun je de exacte CV-blokken laten zien die het herkent:

```powershell
python .\scripts\Migrate-CvToPackage.py
```

Het hoort 20 CV-automatiseringen en 8 CV-scripts te tonen. Het stopt zonder bestanden te wijzigen als de live-bestanden daarvan afwijken. Voer daarna uit:

De migratie maakte tijdgestempelde backups van `automations.yaml` en `scripts.yaml` op de HA-share. Alleen de herkende 20 CV-automatiseringen en 8 CV-scripts zijn daaruit verwijderd. `configuration.yaml`, MQTT en alle overige automatiseringen/scripts zijn ongemoeid gebleven. De configuratiecontrole in HA slaagde en HA is herstart.

Tijdens deze migratie zijn de ingestelde nummers na het verwijderen van de UI-helpers niet automatisch met hun oude waarden teruggekomen. Ze zijn daarom eenmalig hersteld uit de lokale migratiebackup. De geverifieerde waarden waren dag 21 °C, nacht 17 °C, Nacht Keuken 17 °C en boost-aanvoer 60 °C. De YAML laat `initial` weg waar mogelijk; bij toekomstige herstarts worden de actuele waarden door Home Assistant hersteld.

Verwijder geen helpers die niet in `packages/cv_heating.yaml` zijn gedefinieerd. De ongebruikte gastenkamer-helper `Gastenkamer Nacht Temp` blijft bijvoorbeeld buiten het package.

