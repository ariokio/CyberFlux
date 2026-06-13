# CyberFlux

> **FR** — Agrégateur de flux RSS cybersécurité, standalone, sans dépendance cloud.  
> **EN** — Standalone cybersecurity RSS feed aggregator, no cloud dependency.

<p align="center">
  <img src="docs/screenshot.png" alt="CyberFlux screenshot" width="900"/>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.7+-3776AB?logo=python&logoColor=white"/>
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green"/>
  <img alt="Sources" src="https://img.shields.io/badge/Sources-250%2B-red"/>
  <img alt="No API" src="https://img.shields.io/badge/No%20API-RSS%20Direct-orange"/>
  <img alt="Standalone" src="https://img.shields.io/badge/Standalone-Single%20HTML-blue"/>
</p>

---

## 🇫🇷 Français

### Présentation

CyberFlux est un agrégateur de flux RSS cybersécurité 100% local, sans compte, sans API tierce, sans tracking. Il agrège **250+ sources** réparties en 7 catégories couvrant la veille française et internationale.

Un proxy Python léger tourne en local pour contourner les restrictions CORS du navigateur et imiter un vrai navigateur auprès des serveurs RSS.

### Fonctionnalités

- 📡 **250+ flux RSS** — Actualités FR, Institutionnel, Recherche, Veille Internationale, Médias, Communauté, Vendors
- ⚡ **Chargement parallèle** — Batch de 12 flux simultanés, rendu incrémental
- 🔍 **Recherche & filtres** — Par source, catégorie, période (aujourd'hui / 7j / 30j / tout), type (articles / médias / social)
- 🏷️ **Tags automatiques** — Ransomware, Vuln, APT, France, Phishing, Data Leak
- 🎬 **Médias intégrés** — YouTube, PeerTube, podcasts, flux Mastodon/Bluesky
- 🔒 **100% local** — Aucune donnée envoyée à l'extérieur, aucun compte requis
- 🖥️ **Standalone** — Un seul fichier HTML + un script Python

### Prérequis

- Python 3.7+
- Module `requests` (généralement déjà installé)

```bash
pip install requests
```

### Installation & lancement

```bash
# 1. Cloner le dépôt
git clone https://github.com/VOTRE_USERNAME/CyberFlux.git
cd CyberFlux

# 2. Lancer le proxy local
python3 cyberflux_proxy.py

# 3. Ouvrir dans le navigateur
# → http://localhost:8765/
# ou ouvrir CyberFlux-v2.html directement (file://)
```

> **Note WSL (Windows Subsystem for Linux)** : le proxy écoute sur `localhost:8765`. Ouvre `http://localhost:8765/` depuis ton navigateur Windows.

### Structure du projet

```
CyberFlux/
├── CyberFlux-v2.html      # Interface web (standalone)
├── cyberflux_proxy.py     # Proxy RSS local (Python)
├── LICENSE
└── README.md
```

### Catégories de sources

| Catégorie | Exemples | Nb sources |
|---|---|---|
| 🌐 Actualités FR | Zataz, Korben, LMI, ZDNet FR, Numerama, 01net | ~70 |
| 🏛️ Institutionnel | ANSSI, CERT-FR, CNIL, CISA, NCSC, ENISA | ~30 |
| 🔬 Recherche & Vulnérabilités | Project Zero, NVD, Exploit-DB, SSTIC, ZDI | ~23 |
| 🌍 Veille Internationale | Krebs, BleepingComputer, Talos, Unit42, Wired | ~30 |
| 🎬 Médias | YouTube cybersec FR, PeerTube ANSSI/CNIL, podcasts | ~50 |
| 👥 Communauté & Blogs | Reddit, Mastodon, Bluesky, blogs perso | ~45 |
| 🏢 Vendors & Solutions | Kaspersky, SentinelOne, Stormshield, Sophos | ~38 |

### Comment ça marche

```
Navigateur (CyberFlux-v2.html)
        │
        │  GET http://localhost:8765/fetch?url=<rss_url>
        ▼
cyberflux_proxy.py
  ├── Headers Firefox complets (User-Agent, Referer, Sec-Fetch-*)
  ├── Retry automatique (2x sur 429/5xx)
  ├── Détection & normalisation charset (ISO-8859-1 → UTF-8)
  └── SSL permissif (certs auto-signés tolérés)
        │
        ▼
Serveur RSS  →  XML brut
        │
        ▼
DOMParser navigateur  →  Cards affichées
```

### Ajouter des sources

Dans `CyberFlux-v2.html`, chaque catégorie est un tableau d'objets dans `SOURCES` :

```javascript
"🌐 Actualités FR": [
    { url: "https://exemple.com/feed", name: "Exemple" },
    // ...
]
```

---

## 🇬🇧 English

### Overview

CyberFlux is a fully local cybersecurity RSS aggregator — no account, no third-party API, no tracking. It aggregates **250+ sources** across 7 categories covering French and international cybersecurity news.

A lightweight Python proxy runs locally to bypass browser CORS restrictions and mimic a real browser when requesting RSS servers.

### Features

- 📡 **250+ RSS feeds** — FR News, Institutional, Research, International Intel, Media, Community, Vendors
- ⚡ **Parallel loading** — Batches of 12 simultaneous feeds, incremental rendering
- 🔍 **Search & filters** — By source, category, time range (today / 7d / 30d / all), type (articles / media / social)
- 🏷️ **Auto-tagging** — Ransomware, Vuln, APT, France, Phishing, Data Leak
- 🎬 **Media support** — YouTube, PeerTube, podcasts, Mastodon/Bluesky feeds
- 🔒 **100% local** — No data sent anywhere, no account needed
- 🖥️ **Standalone** — One HTML file + one Python script

### Requirements

- Python 3.7+
- `requests` module

```bash
pip install requests
```

### Installation & usage

```bash
# 1. Clone the repo
git clone https://github.com/VOTRE_USERNAME/CyberFlux.git
cd CyberFlux

# 2. Start the local proxy
python3 cyberflux_proxy.py

# 3. Open in browser
# → http://localhost:8765/
# or open CyberFlux-v2.html directly (file://)
```

> **WSL note**: the proxy listens on `localhost:8765`. Open `http://localhost:8765/` from your Windows browser.

### How it works

```
Browser (CyberFlux-v2.html)
        │
        │  GET http://localhost:8765/fetch?url=<rss_url>
        ▼
cyberflux_proxy.py
  ├── Full Firefox headers (User-Agent, Referer, Sec-Fetch-*)
  ├── Auto-retry (2x on 429/5xx)
  ├── Charset detection & normalization (ISO-8859-1 → UTF-8)
  └── Permissive SSL (self-signed certs tolerated)
        │
        ▼
RSS Server  →  Raw XML
        │
        ▼
Browser DOMParser  →  Cards rendered
```

### Adding sources

In `CyberFlux-v2.html`, each category is an array of objects inside `SOURCES`:

```javascript
"🌐 Actualités FR": [
    { url: "https://example.com/feed", name: "Example" },
    // ...
]
```

### Source categories

| Category | Examples | Count |
|---|---|---|
| 🌐 FR News | Zataz, Korben, LMI, ZDNet FR, Numerama | ~70 |
| 🏛️ Institutional | ANSSI, CERT-FR, CNIL, CISA, NCSC, ENISA | ~30 |
| 🔬 Research & Vulns | Project Zero, NVD, Exploit-DB, SSTIC, ZDI | ~23 |
| 🌍 International Intel | Krebs, BleepingComputer, Talos, Unit42 | ~30 |
| 🎬 Media | YouTube cybersec FR, PeerTube, podcasts | ~50 |
| 👥 Community & Blogs | Reddit, Mastodon, Bluesky, personal blogs | ~45 |
| 🏢 Vendors | Kaspersky, SentinelOne, Stormshield, Sophos | ~38 |

---

## Contributing / Contribuer

**FR** — Les contributions sont les bienvenues ! Nouvelles sources, corrections d'URLs mortes, améliorations UI — ouvre une issue ou une PR.

**EN** — Contributions welcome! New sources, dead URL fixes, UI improvements — open an issue or a PR.

1. Fork the repo
2. Create a branch (`git checkout -b feature/my-feature`)
3. Commit (`git commit -m 'Add: my feature'`)
4. Push (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

MIT — see [LICENSE](LICENSE)
