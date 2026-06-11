from pymongo import MongoClient, ASCENDING

client = MongoClient("mongodb://host.docker.internal:27017/")
db = client["pld_db"]
books = db["books"]

# Nettoyage
books.drop()

# INSERT - documents avec structures différentes
print("=== INSERT ===")
books.insert_many([
    {"title": "Dune", "author": "Frank Herbert", "year": 1965, "tags": ["sci-fi", "classic"]},
    {"title": "1984", "author": "George Orwell", "year": 1949},
    {"title": "Foundation", "author": "Isaac Asimov", "year": 1951, "tags": ["sci-fi"], "series": "Foundation"}
])
print("3 documents insérés")

# QUERY simple
print("\n=== QUERY simple (author = Frank Herbert) ===")
for doc in books.find({"author": "Frank Herbert"}, {"_id": 0}):
    print(doc)

# QUERY nested (tag dans un array)
print("\n=== QUERY nested (tag = sci-fi) ===")
for doc in books.find({"tags": "sci-fi"}, {"_id": 0}):
    print(doc)

# UPDATE - modifier un champ
print("\n=== UPDATE ($set year de Dune) ===")
books.update_one({"title": "Dune"}, {"$set": {"year": 1966}})
print(books.find_one({"title": "Dune"}, {"_id": 0}))

# UPDATE - ajouter un élément dans un array
print("\n=== UPDATE ($push tag dans 1984) ===")
books.update_one({"title": "1984"}, {"$push": {"tags": "dystopia"}})
print(books.find_one({"title": "1984"}, {"_id": 0}))

# DELETE
print("\n=== DELETE (Foundation) ===")
books.delete_one({"title": "Foundation"})
print(f"Documents restants : {books.count_documents({})}")

# INDEX — COLLSCAN vs IXSCAN avec mesure de temps
print("\n=== INDEX sur author ===")

# Mesure SANS index (COLLSCAN)
books.drop_indexes()
explain_no_idx = books.find({"author": "George Orwell"}).explain("executionStats")
stage_no_idx = explain_no_idx["queryPlanner"]["winningPlan"]["stage"]
ms_no_idx = explain_no_idx["executionStats"]["executionTimeMillis"]
print(f"Sans index  → stage: {stage_no_idx}, temps: {ms_no_idx} ms")

# Mesure AVEC index (IXSCAN)
books.create_index([("author", ASCENDING)])
explain_idx = books.find({"author": "George Orwell"}).explain("executionStats")
stage_idx = explain_idx["queryPlanner"]["winningPlan"]["stage"]
ms_idx = explain_idx["executionStats"]["executionTimeMillis"]
print(f"Avec index  → stage: {stage_idx}, temps: {ms_idx} ms")

print("\nPOC terminé avec succès !")
