
from random import randint

class Gen_data(object):
    """Zapewnia dostep do algorytmow generowania losowych danych."""
    
    
    def __init__(self):
        self.organizationalUnitNames = ("Katedra Informatyki", "Katedra Matematyki")
        self.namesM = ("Adam", "Marcin", "Krzysztof", "Krystian", "Damian", "Dariusz", "Rafal", "Bogumil", "Piotr", "Maciej")
        self.namesF = ("Maria", "Anna", "Ewa", "Julita", "Zaneta", "Agata", "Milena", "Olga", "Kaludia")
        self.surname = ("Nowak", "Kowalski", "Wisniewski", "Dabrowski", "Lewandowski", "Wojcik", "Kaminski", "Kowalczyk",
                        "Zielinski", "Szymanski", "Wozniak", "Kozlowski", "Jankowski", "Wojciechowski", "Kwiatkowski")
        self.grades = (2, 3, 3.5, 4, 4.5, 5)


    def get_name(self, count=1):
        list_size = len(self.namesM)-1
        return_list = []
        for i in range(0, count): 
            return_list.append(self.namesM[randint(0, list_size)])
        return return_list


    def get_surname(self, count=1):
        pass


    def get_int(self, count=1, max=10000):
        return_list = []
        for i in range(0, count): 
            return_list.append(randint(0, max))
        return return_list


    def get_random_int(self):
        return randint(0, 999999)

    def choose_tuple(self, data):
        index = randint(0, len(data)-1)
        return data[index]


    def get_grade(self):
        index = randint(0, len(self.grades)-1)
        return self.grades[index]