# Présentation — MongoDB · Modèle Document
### PLD Alternative Data Models · Holberton School Toulouse

> **Format :** 10 slides · 10–15 min · Les 7 questions du sujet dans l'ordre

---

## Slide 1 — Titre

**MongoDB & le modèle document**
*Persistance polyglotte : pourquoi une seule base ne suffit pas*

Holberton School Toulouse · PLD · 2025

---

## Slide 2 — Q1 · C'est quoi ce modèle ?

**Le modèle document** stocke des données sous forme d'objets JSON autonomes, regroupés dans des collections.

- Pas de lignes, pas de tables — des **documents**
- Chaque document est **auto-descriptif** : il contient ses données ET leur structure
- MongoDB utilise **BSON** (Binary JSON) en interne pour la performance

**Pourquoi ça existe ?**
Le web des années 2000 a généré des données hiérarchiques et hétérogènes que le modèle relationnel gérait mal : profils utilisateurs, catalogues produits, contenus variables.

> « Le schéma SQL est un contrat signé à l'avance. MongoDB, c'est un contrat qui évolue avec votre application. »

---

## Slide 3 — Q2 · Comment les données sont représentées ?

**Vocabulaire : SQL → MongoDB**

| SQL | MongoDB |
|---|---|
| Table | Collection |
| Ligne | Document |
| Colonne | Champ (field) |
| Clé primaire | `_id` (auto-généré) |

**Un document dans notre POC :**

```json
{
  "_id": ObjectId("..."),
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965,
  "tags": ["sci-fi", "classic"],
  "publisher": { "name": "Chilton Books", "country": "USA" }
}
```

→ Les **tableaux** et **objets imbriqués** sont natifs. Pas besoin de table de jointure.
→ `1984` dans la même collection peut ne **pas avoir** de champ `tags` — c'est valide.

---

## Slide 4 — Q3 · Comment fonctionnent les opérations CRUD ?

**Demo live — `poc_mongodb.py`**

```python
# INSERT — 3 docs, structures différentes
books.insert_many([
    {"title": "Dune",       "author": "Frank Herbert", "year": 1965, "tags": ["sci-fi", "classic"]},
    {"title": "1984",       "author": "George Orwell",  "year": 1949},
    {"title": "Foundation", "author": "Isaac Asimov",   "year": 1951, "series": "Foundation"}
])

# READ simple
books.find({"author": "Frank Herbert"})

# READ dans un tableau (sans JOIN)
books.find({"tags": "sci-fi"})

# UPDATE atomique
books.update_one({"title": "Dune"},  {"$set":  {"year": 1966}})
books.update_one({"title": "1984"},  {"$push": {"tags": "dystopia"}})

# DELETE
books.delete_one({"title": "Foundation"})
```

`$set` modifie un champ · `$push` ajoute dans un tableau · les deux sont **atomiques au niveau document**.

---

## Slide 5 — Q3 (suite) · Feature distinctive — Index & explain

**COLLSCAN vs IXSCAN — impact d'un index**

```python
# Sans index → scan de toute la collection
books.find({"author": "George Orwell"}).explain("executionStats")
# → stage: COLLSCAN

# Après create_index
books.create_index([("author", ASCENDING)])
books.find({"author": "George Orwell"}).explain("executionStats")
# → stage: IXSCAN
```

- Sans index : MongoDB lit **tous** les documents (O(n))
- Avec index : accès direct (O(log n))
- `explain("executionStats")` expose le plan d'exécution — équivalent du `EXPLAIN` SQL

---

## Slide 6 — Q4 · En quoi est-il performant ?

**Cas d'usage où MongoDB excelle :**

| Situation | Pourquoi MongoDB gagne |
|---|---|
| Catalogue produits (attributs variables) | Schéma flexible, pas d'`ALTER TABLE` |
| Profils utilisateurs complexes | Imbrication évite les jointures |
| CMS / articles aux structures différentes | Un document = un article complet |
| Applications mobiles offline-first | Sync de documents JSON naturelle |
| Logs et événements semi-structurés | Insert rapide, schéma libre |

**Avantage architectural :** MongoDB scale **horizontalement** (sharding natif). SQL scale surtout **verticalement** (plus de RAM/CPU sur un seul serveur).

---

## Slide 7 — Q5 · Quels compromis et limites ?

**Honnêtement : ce que MongoDB fait moins bien**

| Limite | Détail |
|---|---|
| Pas de `FOREIGN KEY` | Aucune contrainte référentielle native — intégrité à la charge de l'app |
| `$lookup` coûteux | Équivalent du JOIN existe mais moins performant que SQL sur données normalisées |
| Duplication | Pour éviter les jointures, on duplique → mise à jour difficile si une donnée change |
| RAM | Les index doivent tenir en mémoire — coûteux sur grandes collections |
| Transactions | Multi-documents disponibles depuis MongoDB 4.0 mais plus complexes que SQL |

**Règle pratique :** si vos données sont **fortement relationnelles** (intégrité critique, beaucoup de jointures), SQL reste le meilleur choix.

---

## Slide 8 — Q6 · Comparaison avec le relationnel

**Ce que le POC illustre concrètement :**

✅ **Plus simple qu'en SQL avec MongoDB :**
- Insérer 3 documents aux structures différentes → une seule `insert_many`, pas d'`ALTER TABLE`
- Chercher par tag dans un tableau → `find({"tags": "sci-fi"})`, pas de table de jonction
- Ajouter un champ à un document existant → `$push` ou `$set`, les autres documents ne sont pas affectés

❌ **Plus difficile qu'en SQL avec MongoDB :**
- Lister tous les livres avec leur éditeur et tous leurs auteurs (relation N:N) → `$lookup` imbriqué, complexe
- Garantir qu'un auteur référencé existe → impossible nativement, il faut coder la vérification
- Reporting croisé sur plusieurs collections → pipeline d'agrégation verbeux vs SQL déclaratif

---

## Slide 9 — Q7 · Architecture polyglotte

**Une application e-commerce réelle :**

```
┌─────────────────────────────────────────────────────┐
│                   Application                       │
└───┬──────────┬──────────┬──────────┬────────────────┘
    │          │          │          │
    ▼          ▼          ▼          ▼
MongoDB     Redis      PostgreSQL  InfluxDB
(catalogue  (sessions  (commandes  (métriques
 produits)   TTL)       paiements)  monitoring)
```

| Base | Rôle | Pourquoi |
|---|---|---|
| **MongoDB** | Catalogue produits | Attributs variables par catégorie |
| Redis | Sessions, cache | TTL automatique, latence < 1 ms |
| PostgreSQL | Commandes, paiements | ACID, intégrité financière critique |
| InfluxDB | Métriques, logs | Optimisé pour séries temporelles |

→ MongoDB ne remplace pas SQL — il le **complète** là où le schéma est flexible.

---

## Slide 10 — Conclusion & ce qu'on a appris

**En résumé :**

- MongoDB stocke des documents JSON flexibles — parfait pour les données hiérarchiques et évolutives
- CRUD simple, index puissants, schéma libre — mais pas de contraintes référentielles
- Comparaison SQL : MongoDB gagne sur la flexibilité et le scale horizontal, SQL gagne sur l'intégrité et les jointures complexes
- Dans une architecture polyglotte, MongoDB prend la partie "données de contenu" — le SQL garde la partie "données transactionnelles"

**Ce que le POC nous a appris :**
- L'opérateur `$push` sur un tableau remplace une table de jonction entière
- `explain()` révèle exactement comment MongoDB exécute une requête
- Un index sur `author` élimine le COLLSCAN — même logique qu'en SQL

**Sources :** MongoDB Docs · *NoSQL Distilled* (Fowler) · DB-Engines · MongoDB University

---

> *Démonstration live : `python3 poc_mongodb.py`*
