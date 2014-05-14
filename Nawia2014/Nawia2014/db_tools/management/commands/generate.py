
from django.core.management.base import BaseCommand, CommandError
from ldapsync import models as ldap 
from nawia import models as nawia
from db_tools.management.commands import gen_data
import datetime
from django.contrib.auth.models import User
from django.core.management import call_command



class Command(BaseCommand):
    help = 'Wygeneruje testowa baze danych.'
    
        

    def handle(self, *args, **options):
        u''' Implementacja generowania danych dla bazy'''
        gen = gen_data.Gen_data()

        #usuniecie danych z poprzeniej bazy danych
        call_command('flush', interactive=True)


        org_units = []
        employees = []
        tssc = []




        #wygenerowanie jednostek organizacyjnych
        for unitName in gen.organizationalUnitNames:
            # jednostka organizacyjna katedra dziekanat
            org_unit = nawia.OrganizationalUnit(ldapId=gen.get_int(),
                                                name=unitName,
                                                #head=
                                                )
            org_unit.save()
            org_units.append(org_unit)

        '''
        #wygenerowanie puli pracownikow
        seed = gen.get_random_int()
        for i in range(1, 10):
            # pracownik uczelni
            index = seed+i
            user_emp = User.objects.create_user('user{a}'.format(a=index), 'user@user{a}.com'.format(a=index), 'user')
            user_emp.save()
            employee = nawia.Employee(title="prof dr hab",
                                      user=user_emp,
                                      #position=,
                                      #organizationalUnit=org_unit,
                                      )
            employee.save()
            employees.append(employee)



        
        #wiazanie pracownikow z jednostkami organizacyjnmi
        emp_count = len(employees)
        count_emp_in_org_unit = emp_count/len(org_units)
        employee_counter = 0
        for unit in org_units:
            for i in range(0, count_emp_in_org_unit):
                employees[employee_counter].organizationalUnit = unit
                employees[employee_counter].save()
                employee_counter+=1


        
        # zmiana stanu pracy 
        tssc = nawia.ThesisSubjectStateChange(state=gen.choose_tuple(nawia.ThesisSubjectStateChange.THESIS_SUBJECT_STATE_CHOICES)[0],
                                               #initiator=,
                                               comment="jakis comment",
                                               occuredAt=datetime.date.today()
                                               )
        tssc.save()

        
        
        # temat pracy
        thesis_subject = nawia.ThesisSubject(#statesHistory=, # many-to-many sa wykozystywanie dopiero po save() 
                                             title="wygeneruj mnie",
                                             description="bardzo szczegolowy opis",
                                             teamMembersLimit=gen.get_int(1, 10)[0],
                                             author=employee.user
                                             )
        
        thesis_subject.save()
        thesis_subject.statesHistory.add(tssc)

        '''


        
        


        #
        
        '''
        
        # cykl ksztalcenia 
        study_cycle = nawia.StudyCycle(ldapId=gen.get_int(),
                                       name="informatyka, inzynierskie, stacjonarne, 2011Z-2014Z",
                                       submissionsOpenAt = datetime.date.today(),
                                       submissionsCloseAt = datetime.date.today(),
                                       #isLdapSynced=,
                                       )

        
        #Student
        student = nawia.Student(#studyCycles=[study_cycle],
                                )

       
        # powiaznie student - temat pracy
        autorship = nawia.Authorship(state=gen.choose_tuple(nawia.Authorship.AUTHORSHIP_STATE_CHOICES)[0],
                                     thesisSubject=thesis_subject,
                                     comment="autorship comment",
                                     student=student,
                                     createdAt=datetime.date.today(),
                                     updatedAt=datetime.date.today()
                                     )

        
        #recenzja
        review = nawia.Review(authorType=gen.choose_tuple(nawia.Review.REVIEW_AUTHOR_TYPE_CHOICES)[0],
                              author=employee,
                              comment="Review comment",
                              mark=gen.get_grade(),
                              #isDone =,
                              #attachments =,
                              )
        


        # praca dyplomowa
        thesis = nawia.Thesis(authorship=autorship,
                              #isDone=,
                              #attachments=,
                              supervisor=employee,
                              #auxiliarySupervisors=,
                              #advisor=,
                              #reviews=review
                              )
        
        
        # kryteria wzgledem pracy dla studntow
        sub_crit = nawia.SubmissionCriterion(type=gen.choose_tuple(nawia.SubmissionCriterion.CRITERION_TYPE_CHOICES)[0],
                                             label="text opisujacy"
                                            )
          

        
        #
        
        # para kryterium odpowiedz 
        sub_crit_val = nawia.SubmissionCriterionValue(criterion=sub_crit
                                                          )
        '''
         

        
        
        # jednostka zewnetrzna
        org = nawia.Organization(name="organizacja zewnetrzna"
                                 )

        

        # wladze wydzialu
        authority = nawia.Authority(#role=,
                                    )
        
        

        self.stdout.write('---------------------------------------------------')
        self.stdout.write('|Generowanie zawartosci bazy przebieglo pomyslnie.|')
        self.stdout.write('---------------------------------------------------')

