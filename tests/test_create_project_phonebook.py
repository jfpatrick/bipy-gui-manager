from bipy_gui_manager.create_project.phonebook import Phonebook


TEST_DATA = """#------------------------------------------------------------------------------
Surname:            Betz
Firstname:          Michael
Display Name:       Michael Betz
E-mail:             Michael.Betz@cern.ch
Other E-mail:       mbetz.Service@cern.ch
Telephone:          +41227678143                              (internal:  78143)
Mobile:             -                                         (internal:      -)
Facsimile:          -                                         (internal:      -)
Department:         BE
Group:              BI
POBox:              Z05000                                    (internal mail)
Bld. Floor-Room:    864 1-C12
Organization:       KIT
Organization:       KIT
Organization:        Karlsruhe Institute of  Technology (DE)
Computer Center ID: 700527

Computer account(s):
Login    Grp St Uid   Gid  Last login    Shell    Home directory

mbetz    si  PA 55850 1077 23/06/13 13:20 /bin/bash /afs/cern.ch/user/m/mbetz
mbetzs   sv  sD 37339 1019 --/--/-- --:-- /bin/bash /afs/cern.ch/user/m/mbetzs
#-------------------------------------------------------------------------------
Surname:            Betz
Firstname:          Christine
Display Name:       Christine Betz
E-mail:             Christine.Betz@cern.ch
Telephone:          -                                         (internal:      -)
Mobile:             -                                         (internal:      -)
Facsimile:          -                                         (internal:      -)
Department:         BE
Group:              CO
POBox:              -                                         (internal mail)
Bld. Floor-Room:    -
Organization:       -
Computer Center ID: 713793

Computer account(s):
Login    Grp St Uid   Gid  Last login    Shell    Home directory

cbetz    si  PA 59022 1077 25/04/13 10:14 /bin/bash /afs/cern.ch/user/c/cbetz
#-------------------------------------------------------------------------------
Surname:            Betz
Firstname:          Jochen
Display Name:       Jochen Betz
E-mail:             jochen.betz@cern.ch
Other E-mail:       fesa3.courses.svn@cern.ch
Telephone:          +41227662412                              (internal:  62412)
Mobile:             -                                         (internal:      -)
Facsimile:          -                                         (internal:      -)
Department:         BE
Group:              CO
POBox:              Z03400                                    (internal mail)
Bld. Floor-Room:    864 2-A12
Organization:       CERN
Computer Center ID: 737141

Computer account(s):
Login    Grp St Uid   Gid  Last login    Shell    Home directory

jbetz    si  PA 41372 1077 28/06/13 15:23 /bin/bash /afs/cern.ch/user/j/jbetz
f3course si  sA 49178 1077 21/05/13 11:53 /bin/bash /afs/cern.ch/user/f/f3course
#-------------------------------------------------------------------------------
#Account St(atus): P(rimary), S(econdary), s(ervice), U(nknown)
#                  A(ctive),  D(isabled),  P(assword expired),  L(ocked out)"""

def ttttest():
    testData = [
        'Masoomeh YARMOHAMMADI SATRI',
        'Jochen Dirk BETZ',
        'Jack Raymond TOWLER',
        'Michal REBISZ',
        'Vegard Joa MOSENG',
        'Blazej KOLAD',
        'Jose Enrique VARELA CAMPELO',
        'Javier ALABAU GONZALVO',
        'Ylia YASTREBOV',
        'Luis Fernando RUIZ GAGO',
        'Antonio ROMERO MARIN',
        'Maria ARSUAGA RIOS',
        'Martin NEPSINSKY',
        'Lev MOZHAEV',
        'Mikhail GROZAK',
        'Donat CSIKOS',
        'Lukasz BURDZANOWSKI',
        'Dario PELLEGRINI',
        'Mateusz POLNIK',
        'Severin KACIANKA',
        'Matthias EHRET',
        'Radoslaw Zdzislaw ORECKI',
        'Giorgia FAVIA',
        'Anders MIKKELSEN',
        'Bogna BLASZCZYK',
        'Marko PRSKALO',
        'Simon Paul RAINS',
        'Jack ROBERTS',
        'Alexandros VERIKIOS',
        'Mikko RISSANEN',
        'Felix SMEDS',
        'Ville Karle MAKINEN',
        'Elliot James ROSE',
        'Daria ASTAPOVYCH',
    ]

    for element in testData:
        aPhonebook = Phonebook(element)
        results = aPhonebook.query_data()
        if results:
            for result in results:
                print(result.emails[0])
