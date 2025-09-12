import json

with open("knowledge.json", encoding="utf-8") as f:
    knowledge = json.load(f)

chunks = [entry["content"] for entry in knowledge]

with open("chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"chunks.json created with {len(chunks)} items")
