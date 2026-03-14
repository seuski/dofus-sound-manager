# 🎵 Dofus Sound Manager

> Retrouvez les musiques de Dofus 2.0 et 1.29 en jouant sur Dofus 3 — en temps réel, automatiquement.

![Version](https://img.shields.io/badge/version-1.3-gold)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📖 C'est quoi ?

Dofus Sound Manager est un outil Windows qui détecte automatiquement votre zone dans Dofus 3 et joue la musique correspondante de votre version préférée (2.0 ou 1.29). Plus besoin de fouiller dans des playlists YouTube — la bonne musique joue au bon moment, y compris en combat et en donjon.

## ✨ Fonctionnalités

- 🗺️ **Détection temps réel** — lecture mémoire du processus Dofus.exe (lecture seule)
- ⚔️ **Musiques de combat par zone** — Frigost, Sufokia, Xélorium, Saharach et plus encore
- 🏰 **95 donjons détectés** — musiques d'ambiance et de combat en shuffle
- 🎵 **3 modes** — OST Dofus 2.0, OST Dofus 1.29, ou votre propre dossier (Custom)
- 🎨 **11 thèmes visuels** — Défaut, Bonta, Brakmar, Tribute, Gold & Steel, Belladone, Unicorn, Emerald Mine, Sufokia, Pandala, Wabbit
- 📌 **Fenêtre flottante** — toujours au premier plan, compacte, redimensionnable
- 🔄 **Mises à jour automatiques** — le logiciel vérifie GitHub au démarrage

## 🚀 Installation

1. Téléchargez le dernier installeur sur la page [Releases](https://github.com/seuski/dofus-sound-manager/releases/latest)
2. Lancez `DofusSoundManager_Setup.exe`
3. Ouvrez Dofus 3 → Options → Son → mettez la **Musique à 0**
4. Lancez Dofus Sound Manager et cliquez sur **ACTIVER**

## 🎮 Utilisation

### Versions musicales
- **1.29** — OST originale de Dofus Rétro
- **2.0** — OST de Dofus 2 avec toutes les zones
- **Custom** — cliquez sur Custom pour sélectionner votre propre dossier de musiques (les fichiers doivent être nommés selon les clés de zones : `amakna.mp3`, `brakmar.mp3`, etc.)

### Mode compact
Cliquez sur la flèche ▲ dans la barre de titre pour réduire la fenêtre au minimum (VERSION + STATUT + MAP + ZONE).

### Thèmes
Cliquez sur un cercle coloré en bas de la fenêtre pour changer le thème visuel. Le choix est sauvegardé automatiquement.

## 🛠️ Développement

### Prérequis
```
pip install pygame pymem Pillow pyinstaller
```

### Lancer en développement
```
python main.py
```

### Compiler le .exe
```
pyinstaller --onefile --noconsole --icon=dofus_logo.ico --add-data "map_database.json;." --add-data "dofus_logo.png;." --add-data "dofus_logo.ico;." --add-data "musiques;musiques" --name "DofusSoundManager" main.py
```

### Structure du projet
```
files/
├── main.py              # Interface graphique + logique principale
├── sniffer.py           # Détection maps via lecture mémoire
├── build_map_db.py      # Génère map_database.json depuis data.zip
├── map_database.json    # Base de 14 437 maps
├── dofus_logo.png       # Logo
└── musiques/
    ├── v20/             # OST Dofus 2.0 (100+ fichiers)
    └── v129/            # OST Dofus 1.29 (33 fichiers)
```

## 🌐 Site web

[dofus-sound-manager.com](https://dofus-sound-manager.com)

## ⚠️ Avertissement

Ce projet est **non officiel** et n'est pas affilié à Ankama Games. Le logiciel lit la mémoire du jeu en **lecture seule** pour détecter les changements de zone — il ne modifie rien. Utilisez-le à votre discrétion.

## 📄 Licence

MIT — libre d'utilisation, de modification et de distribution.
