"""
build_map_db.py — Construit la base de données locale des maps Dofus
====================================================================
Format DDC v0.11.29 :
  map-coordinates.json : [{position: {x,y}, map-ids: [id1,id2,...]}, ...]
  sub-areas.json       : [{id, name-id, area-id, ...}, ...]
  fr.i18n.json         : {entries: [{id, value}, ...], language-code: "fr"}
  areas.json           : [{id, name-id, super-area-id, ...}, ...]
"""

import json, os, zipfile

KEYWORDS_MUSIC = [
    # ── Combats spécifiques en PREMIER ───────────────────────────────
    ("cartes de combat frigost",   "frigost_combat"),
    ("carte de combat frigost",    "frigost_combat"),
    ("cartes de combat sufokia",   "sufokia_combat"),
    ("carte de combat sufokia",    "sufokia_combat"),
    ("cartes de combat xelorium",  "xelorium_combat"),
    ("carte de combat xelorium",   "xelorium_combat"),
    ("cartes de combat cimetiere", "cimetieres_combat"),
    ("carte de combat cimetiere",  "cimetieres_combat"),
    ("cartes de combat dimension", "dimensions_combat"),
    ("carte de combat dimension",  "dimensions_combat"),
    ("cartes de combat saharach",  "saharach_combat1"),
    ("carte de combat saharach",   "saharach_combat1"),
    ("cartes de combat crocuzco",  "crocuzco_combat"),
    ("carte de combat crocuzco",   "crocuzco_combat"),
    ("cartes de combat martegel",  "martegel_combat"),
    ("carte de combat martegel",   "martegel_combat"),
    ("cartes de combat astrub",    "astrub_combat"),
    ("carte de combat astrub",     "astrub_combat"),
    # Combat générique
    ("cartes de combat", "combat_general"), ("carte de combat", "combat_general"),
    ("mode tactique",    "combat_general"), ("combat",          "combat_general"),

    # ── Frigost (spécifiques avant générique) ────────────────────────
    ("la bourgade",      "frigost_village"), ("bourgade",       "frigost_village"),
    ("port de givre",    "frigost_port"),
    ("village enseveli", "frigost_village"),
    ("remparts a vent",  "frigost_village"), ("rempart",        "frigost_village"),
    ("foret des pins",   "frigost_foret"),   ("pins perdus",    "frigost_foret"),
    ("lac gele",         "frigost_foret"),
    ("jardins d hiver",  "frigost_jardins"), ("jardin",         "frigost_jardins"),
    ("peninsule",        "frigost_peninsule"),
    ("clepsydre",        "donjon_clepsydre"),
    ("frigost",          "frigost"),

    # ── Sufokia (spécifiques avant générique) ────────────────────────
    ("abysses",          "sufokia_abysses"), ("trithon",        "sufokia_abysses"),
    ("ville submergee",  "sufokia_ville"),   ("koutoulou",      "sufokia_fosse"),
    ("sufokia",          "sufokia"),         ("sufok",          "sufokia"),

    # ── Otomaï ───────────────────────────────────────────────────────
    ("tourbiere",        "otomai_tourbieres"),
    ("canopee",          "otomai_village"),
    ("otomai",           "otomai"),          ("otomaj",         "otomai"),

    # ── Saharach ─────────────────────────────────────────────────────
    ("cite oubliee",     "saharach2"),       ("pyramide maudite","saharach2"),
    ("tal kasha",        "saharach2"),
    ("saharach",         "saharach"),

    # ── Xélorium ─────────────────────────────────────────────────────
    ("xelorium",         "xelorium"),

    # ── Crocuzco / Archipel des Ecailles ─────────────────────────────
    ("crocuzco",         "crocuzco"),        ("crocuzko",       "crocuzco"),
    ("tikoltenak",       "crocuzco"),        ("tork",           "crocuzco"),
    ("kaziman",          "crocuzco"),        ("crocatan",       "crocuzco"),

    # ── Martegel ─────────────────────────────────────────────────────
    ("martegel",         "martegel"),

    # ── Vulkania ─────────────────────────────────────────────────────
    ("vulkania",         "foret_sombre"),    ("kohrog",         "foret_sombre"),
    ("lantamau",         "foret_sombre"),    ("espartiate",     "foret_sombre"),

    # ── Forêt des Abraknydes / Forêt Sombre ──────────────────────────
    ("abrakny",          "foret_sombre"),    ("foret sombre",   "foret_sombre"),
    ("foret maledique",  "foret_sombre"),    ("maledique",      "foret_sombre"),
    ("dark vlad",        "foret_sombre"),    ("halouine",       "foret_sombre"),

    # ── Dimensions divines ───────────────────────────────────────────
    ("ecaflipus",        "dimensions_ecaflipus"),
    ("dimension obscure","dimensions_obscure"),
    ("xelorium",         "xelorium"),
    ("enutrosor",        "donjon_generique"),
    ("dimension",        "dimensions_divines"), ("eliotrope",   "dimensions_divines"),
    ("imaginarium",      "dimensions_divines"),
    ("onirique",         "dimensions_divines"), ("plan astral", "dimensions_divines"),
    ("monde des esprits","dimensions_divines"),

    # ── Songes ───────────────────────────────────────────────────────
    ("songe",            "songe"),              ("puits des songes","songe"),
    ("contrees oniriques","songe"),

    # ── Eliocalypse ──────────────────────────────────────────────────
    ("eliocalypse",      "eliocalypse"),        ("tempete de l eliocalypse","eliocalypse"),
    ("sanctuaire du dernier espoir","eliocalypse"),
    ("futur imprevu",    "eliocalypse"),

    # ── Kolizéum ─────────────────────────────────────────────────────
    ("kolizeum",         "kolizeum"),           ("arenes de goultard","kolizeum"),
    ("amphitheatre",     "kolizeum"),

    # ── Nimotopia ────────────────────────────────────────────────────
    ("nimotopia",        "nonowel"),

    # ── Île de Grobe / Mer d'Asse ────────────────────────────────────
    ("grobe",            "ile_moon"),
    ("kartonpath",       "kartonpath"),      ("ilot estitch",   "kartonpath"),
    ("ile mysterieuse",  "kartonpath"),      ("dramak",         "kartonpath"),
    ("tunnel de karton", "kartonpath"),

    # ── Éther / Centre du monde ──────────────────────────────────────
    ("ether",            "dimensions_divines"), ("pyramide ocre", "dimensions_divines"),
    ("croisee des mondes","dimensions_divines"),

    # ── Wukin et Wukang ──────────────────────────────────────────────
    ("wukin",            "pandala"),         ("wukang",         "pandala"),
    ("orukam",           "pandala"),         ("imagiro",        "pandala"),
    ("royaume d encre",  "pandala"),         ("royaume de papier","pandala"),

    # ── Montagne des Koalaks ─────────────────────────────────────────
    ("koalak",           "amakna"),          ("kaliptus",       "amakna"),
    ("koulosse",         "amakna"),          ("skeunk",         "amakna"),
    ("morh kitu",        "amakna"),          ("lacs enchantes", "amakna"),
    ("marecages nausea", "amakna"),          ("marecages sans fond", "amakna"),
    ("village des eleveurs", "havre_monde"),

    # ── Îles ─────────────────────────────────────────────────────────
    ("incarnam",         "incarnam"),
    ("ile des wabbits",  "ile_wabbits"),     ("wabbit",         "ile_wabbits"),
    ("cawotte",          "ile_wabbits"),
    ("ile de moon",      "ile_moon"),        ("moon",           "ile_moon"),
    ("ile de nowel",     "nowel"),           ("nowel",          "nowel"),
    ("ile de pwak",      "ile_pwak"),        ("pwak",           "ile_pwak"),
    ("ile de rok",       "ile_moon"),

    # ── Donjons nommés ───────────────────────────────────────────────
    ("ilyzaelle",        "donjon_ilyzaelle"),
    ("sakai",            "donjon_sakai"),
    ("qu'tan",           "donjon_qutan"),    ("qutan",          "donjon_qutan"),
    ("minotoror",        "donjon_minotoror"),
    ("perge",            "donjon_perge"),
    ("dragon cochon",    "donjon_generique"),
    ("sphincter",        "donjon_generique"),
    ("kharnozor",        "donjon_generique"),
    ("korriandre",       "donjon_generique"),
    ("obsidiantre",      "donjon_generique"),
    ("nileza",           "donjon_generique"),
    ("dazak",            "donjon_generique"),
    ("kolosso",          "donjon_generique"),
    ("bethel",           "donjon_generique"),
    ("harebourg",        "donjon_clepsydre"),
    ("gloursons",        "gloursons"),
    ("missiz frizz",     "donjon_generique"),
    ("mansot",           "donjon_generique"),
    ("royalmouth",       "donjon_generique"),
    ("klime",            "donjon_generique"),
    ("sylargh",          "donjon_generique"),
    ("labyrinthe",       "donjon_generique"),

    # ── Pandala ──────────────────────────────────────────────────────
    ("pandala",          "pandala"),
    ("atoll des possedes","pandala"),        ("pandamonium",    "pandala"),

    # ── Srambad ──────────────────────────────────────────────────────
    ("srambad",          "srambad"),

    # ── Havre-monde ──────────────────────────────────────────────────
    ("havre-monde",      "havre_monde"),     ("havre",          "havre_monde"),

    # ── Foire du Trool ───────────────────────────────────────────────
    ("trool",            "foire_trool"),

    # ── Cimetières ───────────────────────────────────────────────────
    ("cimetiere",        "cimetieres"),

    # ── Ingalsses / Rocky ────────────────────────────────────────────
    ("ingalsse",         "ingalsses"),
    ("rocky",            "rocky_plains"),    ("rocailleu",      "rocky_plains"),

    # ── Sidimote ─────────────────────────────────────────────────────
    ("sidimote",         "sidimote"),

    # ── Cania ────────────────────────────────────────────────────────
    ("cania",            "cania"),           ("massif",         "cania"),

    # ── Brakmar ──────────────────────────────────────────────────────
    ("bordure de br",    "brakmar_bordure"), ("haras de br",    "brakmar_bordure"),
    ("labyrinthe des vents", "brakmar_bordure"), ("cimetiere des tortures", "brakmar_bordure"),
    ("brakmar",          "brakmar"),         ("cuirasse",       "brakmar"),
    ("faubourg de br",   "brakmar"),         ("fumerolle",      "brakmar"),
    ("marmite",          "brakmar"),         ("ancre",          "brakmar"),
    ("enclume",          "brakmar"),         ("entrailles",     "brakmar"),
    ("sousouriciere",    "brakmar"),

    # ── Bonta ────────────────────────────────────────────────────────
    ("bonta",            "bonta"),           ("cite des vents", "bonta"),
    ("dopeul",           "bonta"),           ("sufol",          "bonta"),
    ("faubourg",         "bonta"),

    # ── Astrub ───────────────────────────────────────────────────────
    ("astrub",           "astrub"),
    ("prairies d astrub","astrub"),

    # ── Donjons — AVANT amakna pour ne pas être écrasés ─────────────
    ("donjon",           "donjon_generique"),
    ("antre",            "donjon_generique"),
    ("repaire",          "donjon_generique"),
    ("caverne",          "donjon_generique"),
    ("souterrain",       "donjon_generique"),
    ("labyrinthe",       "donjon_generique"),
    ("creuset",          "donjon_generique"),
    ("fort thune",       "donjon_generique"),
    ("palais du roi",    "donjon_generique"),

    # ── Amakna (tout ce qui reste) ───────────────────────────────────
    ("marecage",         "amakna"),          ("craqueleur",     "amakna"),
    ("bouftou",          "amakna"),          ("bwork",          "amakna"),
    ("tofu",             "amakna"),          ("madrestam",      "amakna"),
    ("scarafeuille",     "amakna"),          ("dragoeufs",      "amakna"),
    ("porco",            "amakna"),          ("kawaii",         "amakna"),
    ("milifutaie",       "amakna"),          ("brouce",         "amakna"),
    ("istairameur",      "amakna"),          ("bandits",        "amakna"),
    ("biblioth",         "amakna"),          ("chateau d amakna","amakna"),
    ("campagne d amakna","amakna"),          ("foret d amakna", "amakna"),
    ("village d amakna", "amakna"),          ("cloaque",        "amakna"),
    ("cote d asse",      "amakna"),          ("amakna",         "amakna"),
]

def normalize(s):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

def name_to_key(name):
    n = normalize(name)
    for kw, key in KEYWORDS_MUSIC:
        if normalize(kw) in n:
            return key
    return "amakna"

def build():
    print("\n" + "="*60)
    print("  🗺️  Construction base de données maps Dofus")
    print("="*60 + "\n")

    if not os.path.exists("data.zip"):
        print("✗ data.zip introuvable dans", os.path.abspath('.'))
        return False

    print("📂 Lecture de data.zip...")
    with zipfile.ZipFile("data.zip") as z:
        def load(name):
            with z.open(name) as f:
                return json.loads(f.read().decode("utf-8"))

        map_coords = load("map-coordinates.json")  # [{position:{x,y}, map-ids:[...]}, ...]
        sub_areas  = load("sub-areas.json")         # [{id, name-id, area-id, ...}, ...]
        areas      = load("areas.json")             # [{id, name-id, ...}, ...]
        fr_i18n    = load("fr.i18n.json")           # {entries:[{id,value},...], language-code}
        # map-positions.json : [{id (=mapId), sub-area-id, ...}, ...]
        map_pos    = load("map-positions.json")

    print(f"  map-coordinates : {len(map_coords)} entrées")
    print(f"  map-positions   : {len(map_pos)} entrées")
    print(f"  sub-areas       : {len(sub_areas)} entrées")
    print(f"  areas           : {len(areas)} entrées")

    # ── Construire index i18n : id → texte français ──────────────────
    i18n = {}
    entries = fr_i18n.get("entries", fr_i18n) if isinstance(fr_i18n, dict) else fr_i18n
    if isinstance(entries, list):
        for e in entries:
            i18n[str(e.get("id",""))] = e.get("value","") or e.get("text","") or e.get("name","")
    elif isinstance(entries, dict):
        i18n = {str(k): v for k, v in entries.items()}
    print(f"  i18n fr         : {len(i18n)} entrées")

    # ── Index area id → nom ──────────────────────────────────────────
    area_names = {}
    for a in areas:
        aid    = a.get("id")
        nid    = a.get("name-id")
        name   = i18n.get(str(nid), f"Area_{aid}") if nid else f"Area_{aid}"
        area_names[aid] = name

    # ── Index sub-area id → nom + area nom ──────────────────────────
    subarea_names = {}
    subarea_area  = {}
    for sa in sub_areas:
        sa_id  = sa.get("id")
        nid    = sa.get("name-id")
        name   = i18n.get(str(nid), f"Zone_{sa_id}") if nid else f"Zone_{sa_id}"
        area_id = sa.get("area-id")
        subarea_names[sa_id] = name
        subarea_area[sa_id]  = area_names.get(area_id, "")

    print(f"\n  Exemples sub-areas :")
    for sa_id, name in list(subarea_names.items())[:8]:
        print(f"    {sa_id} → {name} (zone: {subarea_area.get(sa_id,'')})")

    # ── Index mapId → sub-area-id depuis map-positions ───────────────
    # map-positions a les clés avec tirets : "id", "sub-area-id"
    mapid_to_subarea = {}
    for mp in map_pos:
        mid  = mp.get("id") or mp.get("map-id")
        said = mp.get("sub-area-id") or mp.get("subAreaId") or mp.get("subarea-id")
        if mid is not None and said is not None:
            mapid_to_subarea[str(mid)] = said

    print(f"\n  mapId→subAreaId : {len(mapid_to_subarea)} mappings")
    if map_pos:
        print(f"  Clés map-positions : {list(map_pos[0].keys())[:10]}")

    # ── Construire la DB finale ──────────────────────────────────────
    print(f"\n🔧 Construction de la base...")
    db = {}

    # map-coordinates : [{position:{x,y}, map-ids:[id1, id2, ...]}, ...]
    for coord in map_coords:
        pos     = coord.get("position", {})
        x       = pos.get("x", 0)
        y       = pos.get("y", 0)
        map_ids = coord.get("map-ids", [])

        for mid in map_ids:
            mid_str    = str(mid)
            subarea_id = mapid_to_subarea.get(mid_str)
            subname    = subarea_names.get(subarea_id, f"Zone_{subarea_id}") if subarea_id else "Inconnue"
            areaname   = subarea_area.get(subarea_id, "") if subarea_id else ""

            # Pour les cartes de combat, l'areaName est prioritaire
            combined = areaname + " " + (subname or "")
            db[mid_str] = {
                "subAreaId":   subarea_id,
                "subAreaName": subname,
                "areaName":    areaname,
                "musicKey":    name_to_key(combined),
                "x": x, "y": y,
            }

    print(f"  ✓ {len(db)} maps extraites")

    if not db:
        print("  ✗ Aucune map. Clés map-positions[0] :", list(map_pos[0].keys()) if map_pos else "vide")
        return False

    with open("map_database.json", "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"  ✓ map_database.json ({os.path.getsize('map_database.json')//1024} KB)")

    print("\n📌 Exemples :")
    for mid, info in list(db.items())[:8]:
        print(f"  {mid} → {info['subAreaName']} [{info['musicKey']}]  ({info['x']},{info['y']})")

    counts = {}
    for v in db.values():
        counts[v["musicKey"]] = counts.get(v["musicKey"], 0) + 1
    print("\n📊 Répartition :")
    for k, n in sorted(counts.items(), key=lambda x: -x[1])[:15]:
        print(f"  {k:<30} {n} maps")

    print("\n✅ Terminé ! Relancez main.py")
    return True

if __name__ == "__main__":
    build()
