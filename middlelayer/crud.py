from sqlalchemy.orm import Session

from uuid import UUID

from . import models, schemas


def get_consumer_by_backend_id(db: Session, workflow_backend_id: UUID):
    return db.query(models.Consumer).filter(models.Consumer.workflow_backend_id == workflow_backend_id).first()


def get_consumer_by_consumer_id(db: Session, consumer_id: str):
    return db.query(models.Consumer).filter(models.Consumer.id == consumer_id).first()


def get_consumers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Consumer).offset(skip).limit(limit).all()


def create_consumer(db: Session, consumer: schemas.ConsumerCreate):
    db_consumer = models.Consumer(
        id=consumer.id,
        workflow_backend_id=consumer.workflow_backend_id,
        workflow_api_access_token=consumer.access_token)
    db.add(db_consumer)
    db.commit()
    db.refresh(db_consumer)
    return db_consumer


def delete_consumer_by_backend_id(db: Session,
                                  workflow_backend_id: UUID):
    consumer = get_consumer_by_backend_id(db=db,
                                          workflow_backend_id=workflow_backend_id)
    db.delete(consumer)
    db.commit()


def create_workflow_asset(db: Session, asset: schemas.WorkflowAsset, consumer_id: str):
    db_asset = models.WorkflowAsset(**asset.dict(), consumer_id=consumer_id)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


def consumer_has_workflow_asset(db: Session,
                                consumer_id: str,
                                workflow_asset_id: str):
    return db.query(models.Consumer).filter(models.Consumer.id == consumer_id,
                                            models.WorkflowAsset.id == workflow_asset_id).join(models.WorkflowAsset).count() > 0


def workflow_backend_exists(db: Session,
                            workflow_backend_id: UUID):
    print(type(workflow_backend_id))
    consumer = get_consumer_by_backend_id(db=db,
                                          workflow_backend_id=workflow_backend_id)
    print(consumer)
    if consumer is not None:
        return True

    return False
