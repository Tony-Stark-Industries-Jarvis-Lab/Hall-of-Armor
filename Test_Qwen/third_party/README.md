# Dependances externes
Toutes les commandes sont à exécuter dans l'ordre depuis le dossier courant (/Test_Qwen/third_party/).
Tout le dosser /Test_Qwen/third_party à l'exception de ce README sont ajoutés au .gitignore.

## Installation de llama.cpp

```bash
git clone https://github.com/ggerganov/llama.cpp
```

Se placer dans le dépôt :

```bash
cd llama.cpp
```

Compiler le projet :

```bash
cmake -B build
cmake --build build
```

Une fois la compilation terminée, le binaire principal est disponible dans :

```text
build/bin/llama-cli
```
