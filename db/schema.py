from sqlalchemy import Column, Text, VARCHAR, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class Dataset(Base):
    __tablename__ = "dataset"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    title = Column(Text, nullable=False)
    market = Column(Text, nullable=True)
    topic = Column(Text, nullable=True)

    chart_type = Column(VARCHAR(10), nullable=False)
    axis_title = Column(Text, nullable=True)
    column_number = Column(Integer, nullable=False)
    column_type = Column(VARCHAR(10), nullable=False)
    row_number = Column(Integer, nullable=False)
    row_type = Column(VARCHAR(10), nullable=False)
    data = Column(Text, nullable=False)

    raw_caption = Column(Text, nullable=False)
    source_sequence = Column(Text, nullable=True)
    target_sequence = Column(Text, nullable=True)