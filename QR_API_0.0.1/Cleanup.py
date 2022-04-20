import gc
import Config
import os

class Cleanup:
    def __init__(self, filename):
        self.filename = filename
        self.force_garbagecollection()
        self.clear_directories()
    
    @staticmethod
    def force_garbagecollection():
        gc.collect()
    
    def clear_directories(self):
        f = self.filename
        folders_to_empty = [Config.Filepath.DATA_IN.value, Config.Filepath.RAW_IMAGES.value, Config.Filepath.TRANSFORMED_IMAGES.value, Config.Filepath.DOCUMENTS.value]
        try:
            for folder in folders_to_empty:
                os.remove(f"{folder}/{f}.pdf")
        except FileNotFoundError:
            pass #File does not exist, so no need to delete it.
