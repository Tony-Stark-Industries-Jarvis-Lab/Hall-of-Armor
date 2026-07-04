# Modèles Qwen
Tout le dosser `/models` à l'exception de ce README sont ajoutés au .gitignore.

## Liste des modèles
Les modèles retenus sont les suivants :

| Modèle | Taille | RAM recommandée | Utilisation |
|---------|---------|-----------------|-------------|
| Qwen2.5-Coder 0.5B | 0,5 milliard de paramètres | ≈ 2 Go | Tests rapides |
| Qwen2.5-Coder 3B | 3 milliards de paramètres | 4 à 6 Go | Scripts simples |
| Qwen2.5-Coder 7B | 7 milliards de paramètres | 8 à 10 Go | Développement courant |
| Qwen2.5-Coder 14B | 14 milliards de paramètres | 18 à 20 Go | Projets importants |
| Qwen2.5-Coder 32B (Q4_K_M) | 32 milliards de paramètres | ≈ 24 Go | Analyses complexes |

Le modèle **7B** constitue le meilleur compromis entre vitesse et qualité.

Le modèle **14B** est recommandé pour les projets conséquents.

Le modèle **32B** correspond à la limite raisonnable d'un MacBook Air M3 disposant de 24 Go de mémoire unifiée.

## Quantification

**Définition** La quantification correspond à la compression des poids du modèles. Un modèle est une architecture du réseaux de neurones, la quantification modifie les poids des neuronnes. Analogie humaine: Un modèle correspond à un niveau intellectuel (élève de collège, étudiant, ingénieur, expert/chercheur), une quantification correspond à son état (parfaitement reposé, fatigué, sous stress, ...).

### Listage des quantifications disponibles
Exemple pour le modèle 7B
```
hf models ls Qwen/Qwen2.5-Coder-7B-Instruct-GGUF
```
--> Donne la liste des différentes quantifications. Ignorer les quantifications qui finissent par `0-0000x-of-0000x.gguf`

### Aperçu des quantifications retenues:

| Quantification | Taille | Qualité | Vitesse | RAM | Usage recommandé |
|----------------|:------:|:--------:|:--------:|:---:|------------------|
| FP16 | ★★★★★ | ≈100 % | ★☆☆☆☆ | ★★★★★ | Évaluation, GPU puissants |
| Q8_0 | ★★★★☆ | ≈99 % | ★★☆☆☆ | ★★★★☆ | Haute qualité |
| Q6_K | ★★★★☆ | ≈98 % | ★★★☆☆ | ★★★☆☆ | Très bon compromis |
| Q5_K_M | ★★★★☆ | ≈97–98 % | ★★★★☆ | ★★★☆☆ | Recommandé pour le développement Python |
| Q4_K_M | ★★★☆☆ | ≈95–97 % | ★★★★★ | ★★☆☆☆ | Meilleur compromis vitesse / mémoire |
| Q3_K_M | ★★☆☆☆ | ≈90 % | ★★★★★ | ★☆☆☆☆ | Machines disposant de peu de mémoire |
| Q2_K | ★☆☆☆☆ | ≈80–85 % | ★★★★★ | ★☆☆☆☆ | Tests, démonstrations, matériel très limité |


## Téléchargement
### Authentification
Optionnel, permet d'avoir un téléchargement plus rapide.
- Créer un compte sur https://huggingface.co
- Cliquer sur l'avatar en haut à droite -> Access Token -> Create new token
- Choisir:
  - un nom
  - un rôle (2x "Read access" dans l'onglet repositories est suffisant pour le téléchargement)
  - Cliquer sur Create token (attention, bien sauvegarder le token qui va s'afficher)
- Dans le terminal, exécuter la commande `hf auth login`
  - Le terminal demandera le token. Il faut le coller ici. **Warning**: On ne voit pas le token s'écrire, on ne voit pas non plus de curseur dans le terminal. Il faut faire Ctrl+V, puis Entrée à l'aveugle.
  - Le terminal renvoie une URL et un code.
- Ouvrir l'URL et coller le code
  - Si tout se passe bien, une page s'affiche avec "Congratulations, you're all set!"
  - Vérification avec la commande `hf auth whoami` (Who am I ?) dans le terminal -> doit afficher le username entré lors de l'inscription sur le site.

### Instruction de téléchargement
Les instructions sont à exécuter depuis le dossier `/models`.

L'instruction générale est 

```bash
hf download Qwen/{NOM DU MODELE} {NOM DE LA QUANTIFICATION}.gguf --local-dir {NOM DU DOSSIER LOCAL}
```

Exemple avec le modèle 7B et la quantification q5_k_m:
```bash
hf download Qwen/Qwen2.5-Coder-7B-Instruct-GGUF qwen2.5-coder-7b-instruct-q5_k_m.gguf --local-dir qwen7b
```

## Note sur le format des modèles

Utiliser exclusivement le format **GGUF**.

Ce format est recommandé car il présente plusieurs avantages :

- compatibilité avec llama.cpp ;
- faible consommation mémoire ;
- rapidité d'exécution ;
- compatibilité macOS et Linux ;
- distribution sous la forme d'un unique fichier.
