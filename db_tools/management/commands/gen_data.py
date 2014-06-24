from random import randint
import random

class Gen_data(object):
    """Zapewnia dostep do algorytmow generowania losowych danych."""
    
    
    def __init__(self):
        # wszystkie dane oraz ustawienia generowania
        self.organizationalUnitNames = ("Katedra Informatyki", "Katedra Matematyki")
        self.employees_count = 20;
        self.students_count = 30;
        self.namesM = ("Adam", "Marcin", "Krzysztof", "Krystian", "Damian", "Dariusz", "Rafal", "Bogumil", "Piotr", "Maciej")
        self.namesF = ("Maria", "Anna", "Ewa", "Julita", "Zaneta", "Agata", "Milena", "Olga", "Kaludia")
        self.surname = ("Nowak", "Kowalski", "Wisniewski", "Dabrowski", "Lewandowski", "Wojcik", "Kaminski", "Kowalczyk",
                        "Zielinski", "Szymanski", "Wozniak", "Kozlowski", "Jankowski", "Wojciechowski", "Kwiatkowski")
        self.grades = (2, 3, 3.5, 4, 4.5, 5)
        self.study_cycles = (u"informatyka, in¿ynierskie, stacjonarne, 2011Z-2014Z",u"informatyka, in¿ynierskie, niestacjonarne, 2012Z-2014Z",
                             u"matematyka, in¿ynierskie, stacjonarne, 2011Z-2015Z")
        self.titles = ("dr", u"dr in¿.", "prof.", "prof. nzw.", u"dr hab. in¿.")

        # zmienne pomocnicze 
        self.last_int = 0
        self.unique_users_list = []


    def get_name(self, count=1):
        list_size = len(self.namesM)-1
        return_list = []
        for i in range(0, count): 
            return_list.append(self.namesM[randint(0, list_size)])
        return return_list


    def get_surname(self, count=1):
        pass



    def get_next_user(self):
        u'''Generuje unikalna krotke (name, surname, email, username).'''
        next_id = self.get_next_int()
        name_index = next_id % len(self.namesM)
        surname_index = next_id % len(self.surname)
        email = "%s@%s%d.com" % (self.namesM[name_index], self.surname[surname_index], next_id)
        username = "%s_%s_%d" % (self.namesM[name_index], self.surname[surname_index], next_id)
        return (self.namesM[name_index], self.surname[surname_index], email, username)


    def get_rand_int_list(self, count, max):
        u'''Pozwala na pobranie listy liczb int, podajemy ilosc oraz maksymalna wartosc, liczby moga sie powatazac.'''
        return_list = []
        for i in range(0, count): 
            return_list.append(randint(0, max))
        return return_list


    def get_rand_int(self):
        u'''Pozwala na wylosowanie pojedynczej losowej liczby int.'''
        return randint(0, 999999)


    def get_next_int(self):
        u'''Zwraca kolejna niepowtarzaln¹ liczbe int.'''
        self.last_int += 1
        return self.last_int 


    def choose_tuple(self, data):
        u''' Wybiera jeden losowy element z krotki.'''
        index = randint(0, len(data)-1)
        return data[index]


    def get_random_grade(self):
        u'''Pozwala na pobranie losowego stponia (oceny) z zakresu 2-5.'''
        index = randint(0, len(self.grades)-1)
        return self.grades[index]


    def get_random_title(self):
        u'''Pozwala na pobranie losowego tytulu naukowego.'''
        index = randint(0, len(self.titles)-1)
        return self.titles[index]