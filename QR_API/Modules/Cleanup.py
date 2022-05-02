import gc
import Config
import os

class Cleanup:
    def __init__(self, filename):
        self.filename = filename
        self.clear_directories()
        self.force_garbagecollection()        
    
    @staticmethod
    def force_garbagecollection():
        gc.collect()
    
    def clear_directories(self):
        f = self.filename
        try:
            os.remove(f"{Config.Filepath.DATA.value}/{f}.pdf")
        except FileNotFoundError:
            pass #File does not exist, so no need to delete it.
