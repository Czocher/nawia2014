
from django.core.management.base import BaseCommand, CommandError
from ldapsync import models as ldap 
from nawia import models as nawia
from db_tools.management.commands import gen_data
import datetime
from django.contrib.auth.models import User
from django.core.management import call_command
from faculty.models import Employee, StudyCycle, Student, Organization, Authority
from topics.models import ThesisTopicStateChange, ThesisTopic
from authorships.models import Authorship, SubmissionCriterion
from reviews.models import Review
from theses.models import Thesis



class Command(BaseCommand):
    help = 'Wygeneruje testowa baze danych.'
    
        

    def handle(self, *args, **options):
        u''' Implementacja generowania danych dla bazy'''

        gen = gen_data.Gen_data()

        #usuniecie danych z poprzeniej bazy danych
        call_command('flush', interactive=True)

        self.stdout.write(' ')
        self.stdout.write('---------------------------------------------------')
        self.stdout.write('|Rozpoczeto generowanie danych.                   |')
        self.stdout.write('---------------------------------------------------')
        self.stdout.write('generowanie:')

        org_units = []
        employees = []
        students = []
        study_cycles = []
        thesis_subjects = []
        autorships = []


        self.stdout.write('jenostki organizacyjne')
        #wygenerowanie jednostek organizacyjnych
        for unitName in gen.organizationalUnitNames:
            # jednostka organizacyjna katedra dziekanat
            org_unit = nawia.OrganizationalUnit(ldapId=gen.get_next_int(),
                                                name=unitName,
                                                #head=
                                                )
            org_unit.save()
            org_units.append(org_unit)

        self.stdout.write('wygenerowanie oraz przypianie pracownikow')
        #przypisaie danych
        employees_per_unit = len(employees)/len(org_units)
        for unit in org_units:
            #wygenerowanie puli pracownikow
            for i in range(0, employees_per_unit):
                # pracownik uczelni
                name, surname, email, username = gen.get_next_user()
                user_emp = User.objects.create_user(
                                                    first_name=name,
                                                    email=email,
                                                    last_name=surname,
                                                    username=username
                                                    )
                user_emp.save()
                employee = Employee(title=gen.get_random_title(),
                                          user=user_emp,
                                          #position=,
                                          organizationalUnit=org_units[unit],
                                          )
                employee.save()
                employees.append(employee)


        self.stdout.write('tematy prac')
        #wygenerowanie tematow prac oraz zmian
        for emp in employees:
            # zmiana stanu pracy dyplomowej (po jednej losowej zmianie_samego_tematu na temat)
            tssc = ThesisTopicStateChange(state=gen.choose_tuple(nawia.ThesisTopicStateChange.THESIS_SUBJECT_STATE_CHOICES)[0],
                                                   #initiator=,
                                                   comment="jakis wygenerowany comment",
                                                   occuredAt=datetime.date.today()
                                                   )
            tssc.save()
            # temat pracy
            thesis_subject = ThesisTopic(#statesHistory=, # many-to-many sa wykozystywanie dopiero po save() 
                                             title="wygenerowany temat pracy",
                                             description="bardzo szczegolowy opis",
                                             teamMembersLimit=gen.get_rand_int(),
                                             author=emp.user
                                             )
            thesis_subject.save()
            thesis_subject.statesHistory.add(tssc)
            thesis_subjects.append(thesis_subject)
        
        self.stdout.write('cykle ksztalcenia')
        #wygeneruj cykle ksztalcenia
        for cycle in gen.study_cycles:
            # cykl ksztalcenia 
            study_cycle = StudyCycle(ldapId=gen.get_next_int(),
                                       name=cycle,
                                       submissionsOpenAt = datetime.date.today(),
                                       submissionsCloseAt = datetime.date.today(),
                                       #isLdapSynced=,
                                       )
            study_cycle.save()
            study_cycles.append(study_cycle)

        
        self.stdout.write('wygenerowanie studentow')
        #wygeneruj pule studentow
        for student_id in range(0, gen.students_count):
            name, surname, email, student_username = gen.get_next_user()
            student_userr = User.objects.create_user(
                                                    first_name=name,
                                                    email=email,
                                                    last_name=surname,
                                                    username=student_username
                                                    )
            student_userr.save()
            #Student
            student = Student(#studyCycles=[study_cycle], #many to many
                                    user=student_userr
                                    )
            student.save()
            # zawsze jest dodawany pierwszy, jeden i ten sam cykl nauczania (dla prostoty)
            student.studyCycles.add(study_cycles[0])
            students.append(student)
        

        


        self.stdout.write('powiazanie studentow z tematami prac')       
        # powiaznie student - temat pracy
        i = 0;
        for ts in thesis_subjects:
            autorship = Authorship(state=gen.choose_tuple(nawia.Authorship.AUTHORSHIP_STATE_CHOICES)[0],
                                     thesisTopic=ts,
                                     comment="autorship comment",
                                     student=students[i],
                                     createdAt=datetime.date.today(),
                                     updatedAt=datetime.date.today()
                                     )
            autorship.save()
            autorships.append(autorship)
            i++1; # inkrementacja licznika studentow

        self.stdout.write('losowe recenzje')
        #wygenerowanie losowych reenzji
        review_count = len(thesis_subjects)/2 # polowa prac bedzie zrecnzwana
        for r in range(0, review_count):
            #recenzja
            review = Review(authorType=gen.choose_tuple(nawia.Review.REVIEW_AUTHOR_TYPE_CHOICES)[0],
                              author=employees[r],  #tematow pracy jest tyle ile pracownikow a recenzji polowa tego wiec pierwsza ploowa pracownikow dokona zrecenzowania
                              comment="Review comment",
                              mark=gen.get_grade(),
                              #isDone =,
                              #attachments =,
                              )
            review.save()
        
        self.stdout.write('wygenerowanie prac')
        # wygeneruj tyle prac co powiazan student - temat pracy
        s = 0;
        for ash in autorships:
            # praca dyplomowa
            thesis = Thesis(authorship=ash,
                                  #isDone=,
                                  #attachments=,
                                  supervisor=employees[s],
                                  #auxiliarySupervisors=,
                                  #advisor=,
                                  #reviews=review
                                  )
            s+=1;
            thesis.save()
       

        self.stdout.write('kryteria pracy dla studenta')
        # kryteria wzgledem pracy dla studntow
        sub_crit = SubmissionCriterion(type=gen.choose_tuple(nawia.SubmissionCriterion.CRITERION_TYPE_CHOICES)[0],
                                             label="text opisujacy"
                                            )
          

        
        # para kryterium odpowiedz 
       # sub_crit_val = nawia.SubmissionCriterionValue(criterion=sub_crit
      #                                                    )
        
        

        
        self.stdout.write('jenostki zewnetrzne')
        # jednostka zewnetrzna
        org = Organization(name="organizacja zewnetrzna"
                                 )

        
        self.stdout.write('wladze wydzialu')
        # wladze wydzialu
        authority = Authority(#role=,
                                    )
        self.stdout.write('koniec.')
        
        self.stdout.write(' ')
        self.stdout.write('---------------------------------------------------')
        self.stdout.write('|Generowanie zawartosci bazy przebieglo pomyslnie.|')
        self.stdout.write('---------------------------------------------------')

