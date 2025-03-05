from collections import deque


class QueueLab:
    def __init__(self, title):
        self.__title = title
        self.__queue_set = {}
        self.__queue = deque()
    

    def add_user(self, user: dict) -> str:
        if user not in self.__queue_set:
            self.__queue.append(user)
            self.__queue_set.add(user)
            return "Succesful append new user"
        else:
            return "User already exist"
    
    def remove_user(self, user: dict) -> None:
        if user in self.__queue_set:
            pop_user = self.__queue.popleft()
            self.__queue_set.remove(pop_user)
            return "Succesful removed user"
        else:
            return "User doesn't exist"
    
    def __str__(self):
        return f"{self.__title}"
