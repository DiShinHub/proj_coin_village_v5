from shares.middlewares.service_process_handler import ProcessHandler

class BackgroundMain(ProcessHandler):
    
    def __init__(self):
        super().__init__()

    def run(self):
        super().run_handler()
            
if __name__ == "__main__":
    
    while True:
        print("test")
        
        import time
        time.sleep(10)
    
    # background_main = BackgroundMain()
    # background_main.run()