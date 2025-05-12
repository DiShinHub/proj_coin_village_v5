from shares.middlewares.service_process_handler import ProcessHandler

class TaskWorkerMain(ProcessHandler):
    
    def __init__(self):
        super().__init__(execution_type="task_worker")

    def run(self):
        super().run_handler()
            
if __name__ == "__main__":
    
    task_worker_main = TaskWorkerMain()
    task_worker_main.run()