from shares.modules.log import system_module_log
from shares.modules.minio import MinioModule

class AppInitHandler():

    def __init__(self):
        self.log = system_module_log
        self.init_minio()
    
    def init_minio(self):
        minio_module = MinioModule()
        minio_module.init_workspace()
    