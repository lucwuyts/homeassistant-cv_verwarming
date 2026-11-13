#!/usr/bin/env python3
"""Move only the CV automation/script entries into packages/cv_heating.yaml."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

from ruamel.yaml import YAML


AUTOMATION_ALIASES = {
    "CV Uit op tijdstip",
    "Buiten Temp -> CV",
    "Verstuur wijziging Dag Temp naar CV",
    "Verstuur wijziging Nacht Temp naar CV",
    "CV: zones uitschakelen bij afwezigheid",
    "CV  NachtBezig helper uitzetten op tijdstip ochtend",
    "CV sNachts uit na 1H",
    "CV: eenmalige ochtendstart",
    "Herstart  OTGW ",
    "Status CV - Alle ruimtes (script)",
    "Stop boost bureel bij uitschakelen",
    "Stop boost living bij uitschakelen",
    "Stop boost keuken bij uitschakelen",
    "CV Boost Auto Stop",
    "CV Control Setpoint Dynamisch",
    "(TEST) Alle CV kranen open",
    "Nest-Off",
    "Nest-On",
    " Nest wens temperatuur overnemen voor CV",
    "CV Living koppelen aan Nest Thermostaat met Helper",
}
SCRIPT_KEYS = {
    "settempbureel_dag",
    "settempbureel_nacht",
    "settempkeuken_dag",
    "settempkeuken_nacht",
    "settemptussen_dag",
    "settemptussen_nacht",
    "cv_boost_zone_parameterized",
    "cv_boost_zone_slim",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(r"\\homeassistant\config"),
        help="Home Assistant config map (default: \\\\homeassistant\\config)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Back up and remove the CV entries from automations.yaml and scripts.yaml.",
    )
    args = parser.parse_args()
    config = args.config.resolve()
    automation_path = config / "automations.yaml"
    scripts_path = config / "scripts.yaml"

    if not automation_path.is_file() or not scripts_path.is_file():
        parser.error(f"Expected automations.yaml and scripts.yaml in {config}")

    yaml = YAML()
    yaml.preserve_quotes = True
    with automation_path.open(encoding="utf-8") as stream:
        automations = yaml.load(stream)
    with scripts_path.open(encoding="utf-8") as stream:
        scripts = yaml.load(stream)

    if not isinstance(automations, list) or not isinstance(scripts, dict):
        parser.error("Unexpected YAML structure; no files were changed.")

    actual_aliases = [entry.get("alias") for entry in automations if isinstance(entry, dict)]
    counts = {alias: actual_aliases.count(alias) for alias in AUTOMATION_ALIASES}
    missing = sorted(alias for alias, count in counts.items() if count == 0)
    duplicated = sorted(alias for alias, count in counts.items() if count > 1)
    missing_scripts = sorted(SCRIPT_KEYS - scripts.keys())
    if missing or duplicated or missing_scripts:
        print("Geen bestanden gewijzigd; de bron wijkt af van de verwachte CV-configuratie.", file=sys.stderr)
        if missing:
            print(f"Ontbrekende CV-automatiseringen: {missing}", file=sys.stderr)
        if duplicated:
            print(f"Dubbele CV-aliases: {duplicated}", file=sys.stderr)
        if missing_scripts:
            print(f"Ontbrekende CV-scripts: {missing_scripts}", file=sys.stderr)
        return 2

    remaining_automations = [
        entry
        for entry in automations
        if not (isinstance(entry, dict) and entry.get("alias") in AUTOMATION_ALIASES)
    ]
    remaining_scripts = {key: value for key, value in scripts.items() if key not in SCRIPT_KEYS}

    print(f"CV-automatiseringen die worden verplaatst: {len(AUTOMATION_ALIASES)}")
    for alias in sorted(AUTOMATION_ALIASES):
        print(f"  - {alias}")
    print(f"CV-scripts die worden verplaatst: {len(SCRIPT_KEYS)}")
    for key in sorted(SCRIPT_KEYS):
        print(f"  - {key}")
    print("Wordt niet aangepast: configuration.yaml, mqtt.yaml en alle andere automations/scripts.")

    if not args.apply:
        print("Alleen controle. Voeg --apply toe om met backups te migreren.")
        return 0

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    for path in (automation_path, scripts_path):
        backup = path.with_name(f"{path.name}.pre-cv-package-{stamp}.bak")
        shutil.copy2(path, backup)
        print(f"Backup: {backup}")

    with automation_path.open("w", encoding="utf-8", newline="") as stream:
        yaml.dump(remaining_automations, stream)
    with scripts_path.open("w", encoding="utf-8", newline="") as stream:
        yaml.dump(remaining_scripts, stream)
    print("Migratie klaar. Publiceer nu het package en herstart HA na controle van de YAML.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
