class UserExistException(Exception):
    def __init__(self):
        self.message = "Вы уже выбрали стол"
    
    def __str__(self):
        return self.message
    
