
class ErrorWhileSavingFile(Exception):

    def __init__(self):
        super().__init__("An error occurred while saving the file")
