from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import os
from . import models, schemas, database, memory_service

app = FastAPI(title="Smart Memory System")

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

@app.post("/events/prompt", response_model=schemas.ChatResponse)
def process_prompt(request: schemas.EventPromptRequest, db: Session = Depends(database.get_db)):
    try:
        result = memory_service.process_memory_event(db, request.userId, request.promptText)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memories/{memory_id}/neighbors", response_model=schemas.MemoryNeighborsResponse)
def get_memory_neighbors(memory_id: int, db: Session = Depends(database.get_db)):
    memory = db.query(models.Memory).filter(models.Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    # Find all relationships associated with this memory
    relations = db.query(models.Relationship).filter(models.Relationship.memory_id == memory_id).all()
    
    neighbors = []
    for rel in relations:
        # For each relation, find other memories that involve the same entities
        # or just return the related entities/memories if specified by the prompt
        # The prompt says: Return neighbors: { id, text, relation }
        # Let's find memories that share the target entity of this relationship
        related_memories = db.query(models.Memory).join(models.Relationship).filter(
            models.Relationship.target_id == rel.target_id,
            models.Memory.id != memory_id
        ).all()
        
        for rm in related_memories:
            neighbors.append({
                "id": rm.id,
                "text": rm.text,
                "relation": f"{rel.source.type}→{rel.target.type} ({rel.relation_type})"
            })
            
    return {
        "memoryId": memory.id,
        "text": memory.text,
        "neighbors": neighbors
    }

@app.get("/decisions", response_model=List[schemas.DecisionLogSchema])
def get_decisions(userId: str = Query(...), db: Session = Depends(database.get_db)):
    logs = db.query(models.DecisionLog).filter(models.DecisionLog.user_id == userId).all()
    return logs

@app.get("/memories", response_model=List[schemas.MemorySchema])
def get_all_memories(userId: str = Query(...), db: Session = Depends(database.get_db)):
    return db.query(models.Memory).filter(models.Memory.user_id == userId).all()

@app.get("/graph/data")
def get_graph_data(userId: str = Query(...), db: Session = Depends(database.get_db)):
    # Fetch all relationships for the user's memories
    memories = db.query(models.Memory).filter(models.Memory.user_id == userId).all()
    memory_ids = [m.id for m in memories]
    
    relations = db.query(models.Relationship).filter(models.Relationship.memory_id.in_(memory_ids)).all()
    
    nodes = []
    edges = []
    seen_entities = set()
    
    for rel in relations:
        if rel.source_id not in seen_entities:
            nodes.append({"id": rel.source_id, "label": rel.source.name, "title": rel.source.type})
            seen_entities.add(rel.source_id)
        if rel.target_id not in seen_entities:
            nodes.append({"id": rel.target_id, "label": rel.target.name, "title": rel.target.type})
            seen_entities.add(rel.target_id)
            
        edges.append({
            "from": rel.source_id,
            "to": rel.target_id,
            "label": rel.relation_type,
            "title": f"Memory: {rel.memory.text}"
        })
        
    return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
