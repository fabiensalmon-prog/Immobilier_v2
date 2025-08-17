
# Ultimate Invest – Immobilier locatif (Streamlit)

**Version investisseur** avec scoring multi-stratégies, DVF, stress tests, et **financement** (taux 2025‑08).

## Lancer
```bash
python -m venv env
source env/bin/activate  # Windows: .\env\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Données
- `pages/` : Dashboard, Financement, Carte, Paramètres
- `core/` : finance, scoring, DVF, loyers
- `data/examples/` : `listings_example.csv`, `rents_example.csv`, `dvf_medians_example.csv`, `rates_2025-08.csv`

## Taux (août 2025)
- Observatoire **Crédit Logement/CSA** (juillet 2025) : **2,99% (15a), 3,05% (20a), 3,11% (25a)**.  
- Brokers (Meilleurtaux/presse) : ~**3,03% / 3,16% / 3,26%**.  
Mettez à jour via `Financement` > upload CSV.

## Encadrement des loyers
Activez le **plafond €/m²** dans `Paramètres`. Liste des villes et cadres : voir Service-public + guides bailleurs.

> **Disclaimer** : Prototype pédagogique. Les taux et loyers évoluent. Vérifiez DVF, encadrement et fiscalité localement.


---

## Déploiement GitHub ➜ Streamlit Cloud

### A. Depuis iPhone (Safari)
1. Va sur **github.com** → `+` → **New repository** → nom: `ultimate-immobilier-app` → **Create**.
2. Ouvre le repo → **Add file** → **Create new file** :
   - Tape `core/finance.py` → colle le contenu de `core/finance.py` → **Commit new file**.
   - Recommence pour chaque fichier/dossier (vois l’arborescence ci-dessous).
   - Astuce : pour créer un dossier, écris `nom_dossier/nom_fichier.ext`.
3. Quand tout est en ligne, va sur **streamlit.io/cloud** → **Deploy an app** → connecte ton GitHub → choisis le repo → **app.py** → **Deploy**.

### B. Depuis un PC/Mac (plus rapide)
```bash
unzip ultimate_immobilier_app.zip
cd ultimate_immobilier_app
git init
git branch -M main
git add .
git commit -m "Initial commit: Ultimate Invest app"
git remote add origin https://github.com/<ton-user>/ultimate-immobilier-app.git
git push -u origin main
```
Puis sur **Streamlit Cloud** : New app → choisis ce repo + `main` + `app.py` → **Deploy**.

### Arborescence à reproduire
```
ultimate_immobilier_app/
├─ app.py
├─ requirements.txt
├─ README.md
├─ .gitignore
├─ .streamlit/
│  └─ config.toml
├─ core/
│  ├─ finance.py
│  ├─ rents.py
│  ├─ dvf.py
│  └─ scoring.py
├─ pages/
│  ├─ 1_Dashboard.py
│  ├─ 2_Financement.py
│  ├─ 3_Carte.py
│  └─ 4_Parametres.py
└─ data/
   └─ examples/
      ├─ listings_example.csv
      ├─ rents_example.csv
      ├─ dvf_medians_example.csv
      └─ rates_2025-08.csv
```

### Après déploiement
- Ouvre **Paramètres** → règle stratégie & charges.
- Va sur **Financement** → choisis ton **montant à financer** et visualise le **tableau de mensualités** + **amortissement**.
- Sur **Dashboard**, importe `listings_example.csv` + `rents_example.csv` (et **dvf_medians_example.csv** si tu veux l’écart au marché).
- Tu peux mettre l’app sur l’écran d’accueil iPhone : Safari → **Partager** → **Ajouter à l’écran d’accueil**.

