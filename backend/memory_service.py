from sqlalchemy.orm import Session
from datetime import datetime
from . import models, vector_store, llm_service
import json

SIMILARITY_THRESHOLD = 0.4  # Similarity threshold for merging memories

def process_memory_event(db: Session, user_id: str, prompt_text: str):
    # 1. Vector Search for existing similar memories
    similar_memories = vector_store.search_memories(prompt_text, user_id, limit=1)
    
    decision = "skipped"
    category = "General"
    importance = 0.5
    memory_id = None
    
    # 2. Check for merging
    if similar_memories and similar_memories[0]["distance"] < SIMILARITY_THRESHOLD:
        decision = "merged"
        existing_memory_id = similar_memories[0]["id"]
        existing_memory = db.query(models.Memory).filter(models.Memory.id == existing_memory_id).first()
        
        # Merge meaning using LLM
        merged_text = llm_service.merge_memories_llm(existing_memory.text, prompt_text)
        
        # Update existing memory
        existing_memory.text = merged_text
        existing_memory.importance_score = min(1.0, existing_memory.importance_score + 0.1)
        existing_memory.timestamp = datetime.utcnow()
        db.commit()
        
        # Update vector store
        vector_store.update_memory_in_vector_store(existing_memory_id, merged_text, user_id)
        memory_id = existing_memory_id
    else:
        # 3. Decision Engine: Classify
        classification = llm_service.classify_input(prompt_text)
        decision = classification.get("decision", "skipped")
        
        if decision == "saved":
            category = classification.get("category", "General")
            importance = classification.get("importance", 0.5)
            
            # Save new memory to SQLite
            new_memory = models.Memory(
                user_id=user_id,
                text=prompt_text,
                category=category,
                source=prompt_text,
                importance_score=importance,
                timestamp=datetime.utcnow()
            )
            db.add(new_memory)
            db.commit()
            db.refresh(new_memory)
            memory_id = new_memory.id
            
            # Save to vector store
            vector_store.add_memory_to_vector_store(memory_id, prompt_text, user_id)
            
            # 4. Graph Layer: Extract entities and relations
            print(f"DEBUG: Extracting entities from: {prompt_text}")
            extracted = llm_service.extract_entities_and_relations(prompt_text)
            print(f"DEBUG: Extracted: {extracted}")
            
            for ent_data in extracted.get("entities", []):
                entity = db.query(models.Entity).filter(models.Entity.name == ent_data["name"]).first()
                if not entity:
                    entity = models.Entity(name=ent_data["name"], type=ent_data["type"])
                    db.add(entity)
                    db.commit()
                    db.refresh(entity)
            
            for rel_data in extracted.get("relations", []):
                src = db.query(models.Entity).filter(models.Entity.name == rel_data["source"]).first()
                tgt = db.query(models.Entity).filter(models.Entity.name == rel_data["target"]).first()
                if src and tgt:
                    relation = models.Relationship(
                        source_id=src.id,
                        target_id=tgt.id,
                        relation_type=rel_data["type"],
                        memory_id=memory_id
                    )
                    db.add(relation)
                else:
                    print(f"DEBUG: Could not save relation {rel_data['source']} -> {rel_data['target']} because entities were missing.")
            db.commit()

    # 5. Log Decision
    log = models.DecisionLog(
        user_id=user_id,
        prompt=prompt_text,
        decision=decision,
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    # 6. Chat Engine: Get RAG response
    # Retrieve top 3 relevant memories for context
    context_memories = vector_store.search_memories(prompt_text, user_id, limit=3)
    chat_response = llm_service.generate_chat_response(prompt_text, context_memories)
    
    return {
        "response": chat_response,
        "decision": decision,
        "memory_id": memory_id
    }
