from sqlalchemy import Column, String, DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import relationship


from .database import Base


class Consumer(Base):
    __tablename__ = "consumers"

    id = Column(String, unique=True, index=True)
    workflow_backend_id = Column(Uuid(as_uuid=True), primary_key=True, unique=True, index=True)
    # pylint: disable=not-callable
    deployment_date = Column(DateTime, default=func.current_timestamp())

    workflow_assets = relationship("WorkflowAsset",
                                   back_populates="asset_consumer",
                                   cascade="delete")


class WorkflowAsset(Base):
    __tablename__ = "workflow_assets"

    id = Column(String, primary_key=True)
    consumer_id = Column(String, ForeignKey("consumers.id"))

    asset_consumer = relationship("Consumer", back_populates="workflow_assets")
