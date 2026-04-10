from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models, llm_service
import sys

def rebuild_graph():
    db = SessionLocal()
    try:
        # 1. Fetch all memories
        memories = db.query(models.Memory).all()
        print(f"Found {len(memories)} memories to process.")
        
        # 2. Clear existing graph data to avoid duplicates
        print("Clearing existing graph data...")
        db.query(models.Relationship).delete()
        db.query(models.Entity).delete()
        db.commit()
        
        # 3. Process each memory
        for memory in memories:
            print(f"\nProcessing Memory #{memory.id}: {memory.text}")
            extracted = llm_service.extract_entities_and_relations(memory.text)
            print(f"Extracted: {extracted}")
            
            # Save entities
            for ent_data in extracted.get("entities", []):
                entity = db.query(models.Entity).filter(models.Entity.name == ent_data["name"]).first()
                if not entity:
                    entity = models.Entity(name=ent_data["name"], type=ent_data["type"])
                    db.add(entity)
                    db.commit()
                    db.refresh(entity)
            
            # Save relationships
            for rel_data in extracted.get("relations", []):
                src = db.query(models.Entity).filter(models.Entity.name == rel_data["source"]).first()
                tgt = db.query(models.Entity).filter(models.Entity.name == rel_data["target"]).first()
                if src and tgt:
                    relation = models.Relationship(
                        source_id=src.id,
                        target_id=tgt.id,
                        relation_type=rel_data["type"],
                        memory_id=memory.id
                    )
                    db.add(relation)
                else:
                    print(f"  Warning: Entities {rel_data['source']} or {rel_data['target']} not found. Skipping relation.")
            
            db.commit()
            
        print("\nGraph rebuild complete!")
        
    finally:
        db.close()

if __name__ == "__main__":
    rebuild_graph()
