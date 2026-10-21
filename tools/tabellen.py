"""Erzeugt je Flotte eine README.md mit einer Tabelle: Kennzeichen x Optionen.

Aufruf aus dem Repo-Wurzelordner: python tools/tabellen.py
"""

import re
from pathlib import Path

FLOTTEN = {
    "VL319": "Lufthansa City Airlines A319",
    "LH319": "Lufthansa A319",
    "LH320": "Lufthansa A320",
    "4Y320": "Discover Airlines A320",
    "LH321": "Lufthansa A321",
}

AN, AUS = "✓", "–"

_alt = {"0": "+1000", "1": "+1500", "2": "+800"}

# Klartext je Wert, laut https://support.fenixsim.com/hc/en-us/articles/12466593239567
WERTE = {
    "acp_type": {"0": "klassisch", "1": "modern"},
    "adirs_type": {"0": "GNADIRS", "1": "ADIRS"},
    "baro_unit": {"0": "hPa", "1": "inHg"},
    "cabin_ready_fwc_type": {"0": "keine", "1": "Checklist", "2": "Memo"},
    "cdls_keypad_beep_enabled": {"0": AUS, "1": "beep", "2": "beep beep"},
    "channel_spacing_type": {"0": "25 kHz", "1": "8.33 kHz"},
    "default_acceleration_altitude_ft": {"0": "+1000", "1": "+1500", "2": "+3000"},
    "default_thrust_reduction_altitude_ft": _alt,
    "default_acceleration_altitude_engine_out_ft": _alt,
    "direct_to_default_abeam_enabled": {"0": "DCT", "1": "ABEAM PTS"},
    "efb_mount_type": {"0": "Fenster", "1": "Rahmen"},
    "electric_hydraulic_pump_type": {"0": "Vickers", "1": "Parker"},
    "emergency_exits_type": {"0": "einfach", "1": "doppelt"},
    "fap_slide_disarmed_message": {"0": "SLIDE DISARMED", "1": "SLIDE IN PARK"},
    "front_window_type": {"0": "Fenster", "1": "Plug", "2": "Plug randlos"},
    "go_around_nav_enabled": {"0": "GA TRK", "1": "NAV"},
    "iae_crank_type": {"0": "30 s", "1": "50 s"},
    "isis_type": {"0": "alt", "1": "neu"},
    "standby_type": {"0": "ISIS", "1": "analog"},
    "start_pack_inhibit_type": {"0": "legacy", "1": "vor SB", "2": "mit SB"},
    "takeoff_performance_packs_on_enabled": {"0": "Packs aus", "1": "Packs an"},
    "takeoff_shift_unit": {"0": "m", "1": "ft"},
    "weight_unit": {"0": "kg", "1": "lbs"},
    "wifi_antenna_type": {"0": AUS, "1": "EU", "2": "US"},
    "window_plug_type": {"0": "Fenster", "1": "Plug", "2": "Plug randlos"},
    "wingbox_type": {"0": "alt", "1": "modern"},
    "yellow_hydraulic_steering": {"0": "grün", "1": "gelb"},
    "virtual_purser_cruise_cabin_lights_brightness_in_dark": {"0": "Off", "1": "DIM 2", "2": "DIM 1", "3": "BRT"},
    "virtual_purser_keep_emer_exits_armed_for_turnaround": {"0": "alle entwaffnen", "1": "nur 1 + 4"},
}

# Ohne Klartext: 0/1 als Haken anzeigen, sonst den Rohwert
ROH = {"act_count", "msn", "selcal_code", "airline_pack_custom_tags", "window_plug_list",
       "cabin_ready_type", "light_type"}


def lesen(pfad):
    tags, optionen = "", {}
    for zeile in pfad.read_text(encoding="utf-8-sig").splitlines():
        m = re.match(r"\s*([A-Za-z0-9_]+)\s*=\s*(.*?)\s*$", zeile)
        if not m:
            continue
        name, wert = m.group(1), m.group(2).strip('"')
        if name == "required_tags":
            tags = wert
        elif name.startswith("fnx_"):
            optionen[name[4:]] = wert
    return tags, optionen


def zelle(name, wert):
    if wert is None:
        return ""
    if name in WERTE:
        return WERTE[name].get(wert, f"`{wert}`")
    if name not in ROH and wert in ("0", "1"):
        return AN if wert == "1" else AUS
    return f"`{wert}`" if wert else ""


def tabelle(ordner, titel):
    daten = {d.name: lesen(d / "livery.cfg") for d in sorted(ordner.iterdir()) if (d / "livery.cfg").is_file()}
    if not daten:
        return None
    spalten = []
    for _, opt in daten.values():
        spalten += [n for n in opt if n not in spalten]

    kopf = ["Kennzeichen", "Tags"] + spalten
    out = [
        f"# {ordner.name} – {titel}",
        "",
        "<!-- Automatisch erzeugt von tools/tabellen.py, nicht von Hand bearbeiten. -->",
        "",
        f"{len(daten)} Lackierungen. {AN} = an, {AUS} = aus, leer = nicht gesetzt (Fenix-Standard). "
        "Spaltennamen ohne `fnx_`-Präfix. Bedeutung der Optionen: "
        "[Fenix Livery Configuration Options](https://support.fenixsim.com/hc/en-us/articles/12466593239567-Livery-Configuration-Options)",
        "",
        "| " + " | ".join(kopf) + " |",
        "|" + "|".join([":--"] * 2 + [":-:"] * len(spalten)) + "|",
    ]
    for reg, (tags, opt) in daten.items():
        werte = [zelle(n, opt.get(n)) for n in spalten]
        out.append("| " + " | ".join([f"[{reg}]({reg}/livery.cfg)", tags] + werte) + " |")
    return "\n".join(out) + "\n"


def main():
    wurzel = Path(__file__).resolve().parent.parent
    for flotte, titel in FLOTTEN.items():
        ordner = wurzel / flotte
        md = tabelle(ordner, titel)
        ziel = ordner / "README.md"
        if md:
            ziel.write_text(md, encoding="utf-8", newline="\n")
            print(f"{flotte}: README.md geschrieben")
        elif ziel.exists():
            ziel.unlink()


if __name__ == "__main__":
    main()
