from shares.middlewares.service_process_handler import ProcessHandler

class SchedulerMain(ProcessHandler):
    
    def __init__(self):
        super().__init__(execution_type="scheduler")

    def run(self):
        super().run_handler()
            
if __name__ == "__main__":
    scheduler_main = SchedulerMain()
    scheduler_main.run()