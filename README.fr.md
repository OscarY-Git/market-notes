[🇬🇧 English](README.md) | 🇫🇷 Français

# Market Notes — Tableau de bord marché cross-asset quotidien/hebdomadaire

Un outil de suivi de marché cross-asset qui automatise la collecte de données,le calcul d'indicateurs de risque, et la génération d'une note de marché 
structurée à la manière d'une morning note de desk.

## Pourquoi ce projet

Étudiant en master de finance visant des postes front office (sales ou trading), j'ai construit cet outil pour reproduire, à mon échelle, une démarche 
quotidienne du métier : collecter l'information, identifier les mouvements significatifs, et construire un raisonnement macro rigoureux plutôt que de
forcer des explications narratives.

## Instruments suivis

| Instrument | Ticker (Yahoo Finance) | Classe d'actif |
|---|---|---|
| US 10Y Yield | `^TNX` | Taux |
| EUR/USD | `EURUSD=X` | Change |
| S&P 500 | `^GSPC` | Actions |
| Gold | `GC=F` | Matières premières |
| Crude Oil (WTI) | `CL=F` | Matières premières |

### Pourquoi ces instruments ?

Le choix s'est porté sur un panier restreint mais délibérément **cross-asset** plutôt que sur une seule classe d'actifs pour deux raisons :

- **Éviter la dilution** : suivre trop d'instruments dès le départ pousse à produire des observations superficielles sur chacun plutôt qu'une analyse 
  rigoureuse sur quelques-uns.
- **Capturer des dynamiques inter-marchés** : ces 5 instruments permettent de raconter des histoires macro cohérentes (ex : une hausse des taux US qui
  se traduit par un dollar plus fort, qui pèse à son tour sur l'or et les actifs risqués) — un raisonnement cross-asset central dans une lecture de 
  marché en sales ou en trading macro.

Chaque instrument sert de **baromètre** pour sa classe d'actif :
- **US 10Y Yield** : le point de référence du marché des taux, très suivi car il influence quasiment toutes les autres classes d'actifs
- **EUR/USD** : la paire de change la plus liquide, sensible aux différentiels de taux et au sentiment de risque global
- **S&P 500** : l'ETF le plus regardé
- **Gold** : valeur refuge classique, souvent utilisée comme indicateur de sentiment risk-on/risk-off
- **Crude Oil (WTI)** : reflète à la fois la demande économique mondiale et les tensions géopolitiques

Cette liste n'est pas figée : le projet permet d'ajouter ponctuellement un instrument "focus" (ex : une action spécifique) en cas d'actualité particulière, 
sans modifier le socle de suivi permanent.

## Source des données

Toutes les données de marché sont récupérées via **Yahoo Finance** (librairie `yfinance`), en accès gratuit et sans clé API. C'est une source pratique pour
un projet étudiant, mais qui a des limites par rapport à un terminal professionnel (Bloomberg, Refinitiv) — voir la section "Limites connues" ci-dessous.

## Architecture
                                                                                                                       
```
market-notes/
├── src/
│   ├── data_fetch.py       # Récupération et nettoyage des prix (Yahoo Finance)
│   ├── analysis.py         # Rendements multi-horizons, volatilité, corrélations
│   └── note_builder.py     # Génération de la note markdown + graphique
├── notes/                  # Notes générées, une par jour (archivées)
├── charts/                 # Graphiques associés à chaque note
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone <url-du-repo>
cd market-notes
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
python3 src/note_builder.py
```

Génère automatiquement :
- Une note datée dans `notes/YYYY-MM-DD.md`
- Un graphique associé dans `charts/YYYY-MM-DD.png`

La note contient un résumé rapide ("En bref"), un focus sur les mouvements notables (seuil ±1.5%), un détail complet des calculs (repliable), et deux 
sections à compléter manuellement : l'explication du mouvement du jour, et une vue à court terme — la partie qui reflète le raisonnement de marché, 
volontairement non automatisée.

## Méthodologie et choix techniques

- **Fenêtre de données (3 mois)** : les indicateurs de volatilité (fenêtre glissante de 20 jours) et de corrélation (fenêtre de 30 jours) nécessitent 
  un minimum d'historique pour être statistiquement stables. 3 mois offre un compromis entre stabilité statistique et réactivité aux conditions récentes 
  — un choix assumé, ajustable selon l'usage souhaité.
- **Normalisation base 100** : chaque instrument est indexé sur sa première valeur *valide* (et non systématiquement la première ligne du tableau), 
  pour éviter qu'une donnée manquante en début de période ne fasse disparaître tout un instrument du graphique.
- **Seuil de mouvement notable (±1.5%)** : seuil fixe pour l'instant, appliqué uniformément à tous les instruments — une amélioration future consisterait 
  à le rendre relatif à la volatilité propre de chaque actif.

## Limites connues

- **Roll des contrats futures** : les tickers `GC=F` (or) et `CL=F` (pétrole) peuvent présenter des sauts de prix ponctuels liés au changement de contrat 
  mensuel, non représentatifs d'un vrai mouvement de marché. À interpréter avec prudence sur les graphiques de tendance longue.
- **Source de données** : Yahoo Finance (gratuite), donc soumise à d'éventuelles latences ou trous de données ponctuels, contrairement à un terminal 
  professionnel (Bloomberg/Refinitiv).
- **Corrélations sur fenêtre courte (30 jours)** : à interpréter comme un instantané plutôt qu'une relation structurelle stable dans le temps.
