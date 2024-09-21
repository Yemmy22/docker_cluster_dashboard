from sqlalchemy import Column, String, Integer, Text
from models.base_model import BaseModel

class Cluster(BaseModel):
    __tablename__ = 'clusters'

    cluster_name = Column(String(128), nullable=False)
    image_name = Column(String(128), nullable=False)
    num_instances = Column(Integer, nullable=False)
    container_ids = Column(Text, nullable=True)  # To store container IDs as a comma-separated list

    def set_container_ids(self, containers):
        self.container_ids = ','.join(containers)

    def get_container_ids(self):
        return self.container_ids.split(',') if self.container_ids else []

