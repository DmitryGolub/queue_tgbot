from database import add_user, get_users


class QueueLab:
    def __init__(self, title):
        self.__title = title
        self.__queue_set = set()
        self.__queue = []
    

    def add_user(self, user: dict) -> str:
        if user not in self.__queue_set:
            self.__queue.append(user)
            self.__queue_set.add(user)
            return True
        else:
            return False
        
    
    def remove_user(self, user: dict) -> None:
        if user in self.__queue_set:
            pop_user = self.__queue.pop()
            self.__queue_set.remove(pop_user)

    
    def __str__(self):
        users = get_users()
        response =f"{self.__title}\n"
        for user in users:
            response += f'{user["name"]}\n'
            
        return response
