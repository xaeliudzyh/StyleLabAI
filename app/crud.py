from sqlalchemy.orm import Session
from . import models, schemas


def create_client(db: Session, data: schemas.ClientCreate):
    obj = models.Clients(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_client(db: Session, client_id: int):
    return db.get(models.Clients, client_id)


def delete_client(db: Session, client_id: int):
    obj = db.get(models.Clients, client_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
