# Résumé de recherche — MongoDB (modèle document)

PLD Alternative Data Models · Holberton School Toulouse

---

## 1. C'est quoi ce modèle et pourquoi existe-t-il ?

MongoDB est une base de données **orientée documents** : au lieu de stocker des lignes dans des tables, elle stocke des **documents JSON** (en interne BSON — Binary JSON) regroupés dans des **collections**. Chaque document est un objet autonome qui peut contenir des champs scalaires, des tableaux, et des sous-documents imbriqués.

Le modèle document est apparu au milieu des années 2000 pour répondre à des limites concrètes du relationnel face aux applications web modernes :

- Les schémas SQL sont rigides : ajouter un champ impose un `ALTER TABLE` sur toute la table, parfois des millions de lignes.
- Les `JOIN` entre tables sont coûteux à l'échelle (sharding horizontal difficile quand les données sont réparties).
- Les données du monde réel sont souvent hiérarchiques (un utilisateur a une liste d'adresses, un produit a des variantes) — le modèle document les représente naturellement sans table de jonction.

MongoDB est aujourd'hui la base NoSQL la plus utilisée (rang 5 mondial toutes catégories, rang 1 document sur db-engines.com, juin 2025).

---

## 2. Comment les données sont-elles représentées ?

### Vocabulaire de base

| Relationnel (SQL) | MongoDB |
|---|---|
| Base de données | Base de données |
| Table | Collection |
| Ligne | Document |
| Colonne | Champ (field) |
| `JOIN` | Document imbriqué ou `$lookup` |
| Schéma fixe | Schéma flexible (optionnel) |

### Structure d'un document

```json
{
  "_id": ObjectId("..."),
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965,
  "tags": ["sci-fi", "classic"],
  "publisher": {
    "name": "Chilton Books",
    "country": "USA"
  }
}
```

- `_id` est généré automatiquement (clé primaire garantie unique).
- Les champs sont optionnels : un autre document de la même collection peut ne pas avoir `tags` ou `publisher`.
- Les tableaux et objets imbriqués sont des citoyens de première classe — pas besoin de table séparée.

---

## 3. Comment fonctionnent les opérations de base (CRUD) ?

Toutes les opérations utilisées dans notre POC (`poc_mongodb.py`) :

| Opération | MongoDB | SQL équivalent |
|---|---|---|
| Insérer | `insert_many([...])` | `INSERT INTO ... VALUES ...` |
| Lire | `find({"author": "Frank Herbert"})` | `SELECT * FROM ... WHERE author = ...` |
| Lire dans un tableau | `find({"tags": "sci-fi"})` | `SELECT ... JOIN tags ON ... WHERE tag = ...` |
| Modifier un champ | `update_one({...}, {"$set": {...}})` | `UPDATE ... SET ... WHERE ...` |
| Ajouter dans un tableau | `update_one({...}, {"$push": {...}})` | `INSERT INTO tag_table ...` |
| Supprimer | `delete_one({...})` | `DELETE FROM ... WHERE ...` |

Les opérateurs `$set` et `$push` sont des **mises à jour atomiques** : MongoDB ne réécrit pas le document entier, il modifie uniquement le champ ciblé.

---

## 4. En quoi est-il performant ? (cas d'usage)

**Lectures rapides sur données hiérarchiques** : un document contient tout ce qui le décrit. Récupérer un article de blog avec ses commentaires est une seule lecture, pas un `SELECT ... JOIN ...`.

**Index flexibles** : on peut indexer n'importe quel champ, y compris des champs à l'intérieur de sous-documents ou dans des tableaux. Notre POC mesure l'impact concret : `COLLSCAN` (scan complet) → `IXSCAN` (index) après `create_index([("author", ASCENDING)])`.

**Schéma évolutif** : ajouter une nouvelle propriété à un type de document ne casse pas les documents existants. Idéal pour des équipes qui itèrent vite.

**Cas d'usage typiques :**
- Catalogues produits e-commerce (variantes, attributs différents par catégorie)
- Profils utilisateurs (préférences, historique, adresses)
- CMS / gestion de contenu (articles avec structures variées)
- Applications mobiles (synchronisation de documents offline)
- Journaux d'événements et logs semi-structurés

---

## 5. Quels compromis ou limites ?

**Pas de contraintes référentielles natives** : il n'existe pas d'équivalent au `FOREIGN KEY` de SQL. Rien n'empêche un document de référencer un `_id` qui n'existe pas. La cohérence des relations est à la charge de l'application.

**Pas de `JOIN` natif efficace** : `$lookup` existe (depuis MongoDB 3.2) mais reste moins performant qu'un `JOIN` SQL optimisé sur des données normalisées. Si votre cas d'usage est très relationnel, MongoDB n'est pas le bon outil.

**Duplication de données** : pour éviter les `$lookup`, on imbrique souvent des données (ex. nom de l'auteur dans chaque livre). Si l'auteur change de nom, il faut mettre à jour tous les documents qui le contiennent — c'est une dénormalisation délibérée.

**Consommation mémoire** : les index MongoDB sont en mémoire. Sur de très grandes collections avec beaucoup d'index, la RAM devient un facteur limitant.

**Transactions multi-documents** : disponibles depuis MongoDB 4.0 (2018), mais plus complexes à configurer et moins performantes qu'une transaction SQL simple. Dans le modèle document bien conçu, la plupart des opérations sont atomiques au niveau du document unique — donc les transactions multi-documents sont rarement nécessaires.

---

## 6. Comparaison avec le relationnel

| Critère | MongoDB | SQL (ex. PostgreSQL) |
|---|---|---|
| Schéma | Flexible, optionnel | Fixe, contraint |
| Relations | Imbrication ou référence manuelle | `FOREIGN KEY`, `JOIN` |
| Mise à l'échelle | Horizontale (sharding natif) | Verticale principalement |
| Transactions | Document-level atomique, multi-doc depuis 4.0 | ACID complet nativement |
| Requêtes complexes | Agrégation pipeline puissante | SQL expressif et mature |
| Cas idéal | Données hiérarchiques, schéma évolutif | Données fortement relationnelles, intégrité critique |

**Ce que MongoDB fait mieux que SQL :**
- Stocker des documents aux structures différentes dans la même collection (notre POC : `Dune` a `tags`, `1984` n'en a pas, `Foundation` a `series`).
- Requête dans un tableau sans table de jointure : `find({"tags": "sci-fi"})` retourne directement les documents dont le tableau `tags` contient `"sci-fi"`.
- Faire évoluer la structure sans migration de schéma.

**Ce que SQL fait mieux que MongoDB :**
- Garantir l'intégrité référentielle entre entités (pas d'orphelins).
- Requêtes ad hoc complexes avec plusieurs jointures et agrégations.
- Reporting et analytics sur des données normalisées.
- Transactions ACID multi-tables sans configuration supplémentaire.

---

## 7. Où le placer dans une architecture polyglotte ?

La **persistance polyglotte** (Fowler & Sadalage, *NoSQL Distilled*, 2012) consiste à utiliser plusieurs bases de données spécialisées dans la même application, chacune là où elle excelle.

**Exemple d'architecture e-commerce polyglotte :**

| Besoin | Base choisie | Pourquoi |
|---|---|---|
| Catalogue produits | **MongoDB** | Attributs variables selon la catégorie |
| Sessions utilisateurs | Redis (clé-valeur) | TTL automatique, accès ultra-rapide |
| Commandes, paiements | PostgreSQL (SQL) | ACID, intégrité financière critique |
| Recommandations | Neo4j (graphe) | Traversée de relations "clients similaires" |
| Métriques, monitoring | InfluxDB (time series) | Requêtes temporelles, rétention automatique |

MongoDB se place naturellement là où les données sont **semi-structurées**, **hiérarchiques**, et où le **schéma évolue souvent**. Il n'a pas vocation à remplacer le SQL dans les parties où l'intégrité relationnelle est critique — il les complète.

---

## Sources

- MongoDB Documentation officielle — [mongodb.com/docs](https://www.mongodb.com/docs/) (2025)
- Fowler, M. & Sadalage, P. — *NoSQL Distilled*, Addison-Wesley, 2012
- DB-Engines Ranking (document stores) — [db-engines.com/en/ranking/document+store](https://db-engines.com/en/ranking/document+store) (juin 2025)
- MongoDB University — M001: MongoDB Basics — [university.mongodb.com](https://university.mongodb.com)
- Banker, K. — *MongoDB in Action*, Manning, 2e éd., 2016
