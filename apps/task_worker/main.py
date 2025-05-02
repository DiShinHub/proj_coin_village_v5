from shares.middlewares.app_init_handler import AppInitHandler
from shares.middlewares.service_process_handler import ProcessHandler

class TaskWorkerMain(ProcessHandler):
    
    def __init__(self):
        super().__init__(execution_type="task_worker")

    def run(self):
        super().run_handler()
            
if __name__ == "__main__":
    
    AppInitHandler()
    
    task_worker_main = TaskWorkerMain()
    task_worker_main.run()