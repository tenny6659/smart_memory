from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models

def manual_populate():
    db = SessionLocal()
    try:
        # Create entities
        user = models.Entity(name="User", type="PERSON")
        hexaware = models.Entity(name="Hexaware", type="COMPANY")
        mumbai = models.Entity(name="Mumbai", type="LOCATION")
        nandu = models.Entity(name="Nandu", type="PERSON")
        
        db.add_all([user, hexaware, mumbai, nandu])
        db.commit()
        
        # Refresh to get IDs
        db.refresh(user)
        db.refresh(hexaware)
        db.refresh(mumbai)
        db.refresh(nandu)
        
        # Create relationships for Memory #2 (Hexaware in Mumbai)
        rel1 = models.Relationship(source_id=user.id, target_id=hexaware.id, relation_type="WORKS_AT", memory_id=2)
        rel2 = models.Relationship(source_id=user.id, target_id=mumbai.id, relation_type="LIVES_IN", memory_id=2)
        
        # Create relationships for Memory #4 (Father Nandu in Mumbai)
        rel3 = models.Relationship(source_id=user.id, target_id=nandu.id, relation_type="HAS_FATHER", memory_id=4)
        rel4 = models.Relationship(source_id=nandu.id, target_id=mumbai.id, relation_type="LIVES_IN", memory_id=4)
        
        db.add_all([rel1, rel2, rel3, rel4])
        db.commit()
        print("Manual population successful!")
        
    finally:
        db.close()

if __name__ == "__main__":
    manual_populate()
