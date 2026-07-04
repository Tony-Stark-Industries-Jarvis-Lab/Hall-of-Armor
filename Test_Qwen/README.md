# Documentation — Mise en place d'une IA de programmation Python en local

## Objectif

Cette documentation décrit la mise en place d'un environnement permettant d'exécuter une IA spécialisée dans la génération de code Python en local.

### Contraintes du projet

- Compatibilité **macOS (Apple Silicon M3)** et **Linux**.
- Gestion de l'environnement exclusivement avec **Conda**.
- Utilisation de modèles **GGUF**.
- Utilisation de **llama.cpp** comme moteur d'inférence.
- Possibilité d'utiliser plusieurs modèles selon les besoins en performances et en qualité.

---

## Architecture du projet

```text
ProjetIA/
│
├── README.md
│
├── models/
│   ├── qwen3b/
│   ├── qwen7b/
│   ├── qwen14b/
│   ├── qwen32b/
│   └── README.md
│
├── env/
│   └── README.md
│
├── third_party/
│   └── README.md
│
├── scripts/
│
├── src/
│
├── notebooks/
│
├── data/
│
├── logs/
│
└── outputs/
```
**Warning**: Ne jamais versionner les dossiers `models`, `env`, `third_party` (à l'exception des fichiers README.md) avec Git (les dossiers ont été ajoutés au .gitignore)

---

## Installation 

### Installation des paquets
Voir le fichier `env/README.md`

### Installation de llama.cpp
Voir le fichier `third_party/README.md`

### Téléchargement des modèles
Voir le fichier `models/README.md`

---

## Exécution d'un modèle
Activer l'environnement conda (voir le fichier `env/README.md`)

Commande générale pour lancer un modèle:

```bash
./build/bin/llama-cli -m models/qwen7b/Qwen2.5-Coder-7B-Instruct-Q5_K_M.gguf
```

Exemple avec la modèle 7B et la quantification `q5_k_m`

```bash
./third_party/llama.cpp/build/bin/llama-cli -m models/qwen7b/qwen2.5-coder-7b-instruct-q5_k_m.gguf
```

Et voilà !
---

## Paramètres utiles

### Taille du contexte

Définir la taille du contexte :

```bash
-c 8192
```

Pour des projets volumineux, augmenter cette valeur :

```text
16384
32768
65536
```

---

### Nombre de threads CPU

Adapter le nombre de threads utilisés :

```bash
-t 8
```

---

### Utilisation du GPU

Charger toutes les couches du modèle sur le GPU :

```bash
-ngl 999
```

---

### Température

Utiliser une faible température pour obtenir un code plus déterministe :

```bash
--temp 0.2
```

Valeurs conseillées :

- 0.1
- 0.2
- 0.3

---

### Top-p

Limiter la diversité des générations :

```bash
--top-p 0.9
```

---

### Top-k

Limiter le nombre de candidats considérés :

```bash
--top-k 20
```

---

### Prompt système

Définir un rôle spécialisé pour le modèle :

```bash
-sys "You are a Python programming assistant."
```

---
# A ignorer pour le moment
La suite est à ignorer pour le moment. 
## Fichier `environment.yml`

Créer le fichier suivant à la racine du projet :

```yaml
name: ia_python

channels:
  - conda-forge

dependencies:
  - python=3.12
  - numpy
  - pandas
  - scipy
  - matplotlib
  - jupyterlab
  - ipython
  - requests
  - rich
  - tqdm
  - git
  - cmake
  - ninja
  - pip

  - pip:
      - transformers
      - huggingface_hub
      - accelerate
      - sentencepiece
```

Créer ensuite l'environnement :

```bash
conda env create -f environment.yml
```

L'activer :

```bash
conda activate ia_python
```

---

# Recommandations

Pour un usage quotidien, utiliser :

- **Qwen2.5-Coder 7B Instruct (Q5_K_M)**

Pour les projets plus importants, privilégier :

- **Qwen2.5-Coder 14B Instruct (Q4_K_M ou Q5_K_M)**

Pour les analyses les plus complexes compatibles avec un MacBook Air M3 (24 Go), utiliser :

- **Qwen2.5-Coder 32B Instruct (Q4_K_M)**

Cette architecture garantit :

- la compatibilité entre macOS et Linux ;
- un environnement entièrement reproductible grâce à Conda ;
- une excellente portabilité ;
- des performances adaptées au développement Python local.