# Environnement conda
Toutes les commandes sont à exécuter dans l'ordre depuis le dossier courant (/Test_Qwen/env).
Tout le dosser /Test_Qwen/env à l'exception de ce README sont ajoutés au .gitignore.
## Installation
Suivre les étapes suivantes:
- Création de l'environnement (depuis le dossier)
```bash
conda create --prefix ./test_qwen
```
- Activation
```bash
conda activate test_qwen/
```
- Installation des paquets conda
```
conda install python=3.12 numpy pandas scipy matplotlib jupyterlab ipython requests rich tqdm git cmake ninja
```
- Installation des paquets pip
```
pip install transformers huggingface_hub accelerate sentencepiece
```
