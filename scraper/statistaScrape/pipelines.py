# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem


from statistaScrape.models import create_table, db_connect, Statista

class StatistascrapePipeline:
    
    def __init__(self) -> None:
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
    
    def process_item(self, item, spider):
    
        session = self.Session()
        table = Statista()
        table.id = item['id']
        table.title = item['title']
        table.market = item['market']
        table.topic = item['topic']
        table.spec = item['spec']
        table.caption = item['caption']
        
        try:
            session.add(table)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        
        return item
    
class CheckExistencyPipeline:
    def __init__(self) -> None:
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
    
    def process_item(self, item, spider):
        session = self.Session()
        check = session.query(Statista).filter_by(id = item["id"]).first()
        session.close()
        
        if check is not None:
            raise DropItem("Already Exist! : ", item["id"])
        else:
            return item