
from random import randint
import random

class Gen_data(object):
    """Zapewnia dostep do algorytmow generowania losowych danych."""
    
    
    def __init__(self):
        # wszystkie dane oraz ustawienia generowania
        self.organizationalUnitNames = ("Katedra Informatyki", "Katedra Matematyki")
        self.employees_count = 20;
        self.namesM = ("Adam", "Marcin", "Krzysztof", "Krystian", "Damian", "Dariusz", "Rafal", "Bogumil", "Piotr", "Maciej")
        self.namesF = ("Maria", "Anna", "Ewa", "Julita", "Zaneta", "Agata", "Milena", "Olga", "Kaludia")
        self.surname = ("Nowak", "Kowalski", "Wisniewski", "Dabrowski", "Lewandowski", "Wojcik", "Kaminski", "Kowalczyk",
                        "Zielinski", "Szymanski", "Wozniak", "Kozlowski", "Jankowski", "Wojciechowski", "Kwiatkowski")
        self.grades = (2, 3, 3.5, 4, 4.5, 5)

        # zmienne pomocnicze 
        unique_users_list = []


    def get_name(self, count=1):
        list_size = len(self.namesM)-1
        return_list = []
        for i in range(0, count): 
            return_list.append(self.namesM[randint(0, list_size)])
        return return_list


    def get_surname(self, count=1):
        pass



    def get_new_user(self):
        u'''Generuje unikalna krotke (name, surname, email).'''
        



        return ''


    def get_rand_int_list(self, count, max):
        u'''Pozwala na pobranie listy liczb int, podajemy ilosc oraz maksymalna wartosc, liczby moga sie powatazac.'''
        return_list = []
        for i in range(0, count): 
            return_list.append(randint(0, max))
        return return_list


    def get_rand_int(self):
        u'''Pozwala na wylosowanie pojedynczej losowej liczby int.'''
        return randint(0, 999999)


    def choose_tuple(self, data):
        u''' Wybiera jeden losowy element z krotki.'''
        index = randint(0, len(data)-1)
        return data[index]


    def get_grade(self):
        u'''Pozwala na pobranie losowego stponia (oceny) z zkresu 2-5.'''
        index = randint(0, len(self.grades)-1)
        return self.grades[index]