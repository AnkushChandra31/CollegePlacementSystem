#Linked List, Queue, Priority Queue
from student import Student

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
    def insert(self, data):
        new_node = Node(data)

        if self.head == None:
            self.head = new_node
            return

        temp = self.head

        while temp.next != None:
            temp = temp.next

        temp.next = new_node


class Queue:

    def __init__(self):
        self.queue = []

    def enqueue(self, data):
        self.queue.append(data)

    def dequeue(self):
        if len(self.queue) == 0:
            return None

        return self.queue.pop(0)

    def is_empty(self):
        return len(self.queue) == 0


class PriorityQueue:

    def __init__(self):
        self.queue = []

    def insert(self, student):
        self.queue.append(student)
        self.queue.sort(key=lambda x: x.cgpa, reverse=True)

    def remove(self):
        if len(self.queue) == 0:
            return None

        return self.queue.pop(0)

    def is_empty(self):
        return len(self.queue) == 0

