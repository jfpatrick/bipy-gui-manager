"""
Original script from jbetz. Created on Jul 1, 2013
"""
import subprocess


def validate_cern_id(cern_id: str) -> bool:
    phonebook = Phonebook(cern_id)
    entries = phonebook.query_data()
    print(entries[0].login_list)
    if len(entries) == 1 and cern_id in [id for id, shell, home in entries[0].login_list]:
        return True
    return False


def discover_full_name(cern_id: str) -> str:
    phonebook = Phonebook(cern_id)
    entries = phonebook.query_data()
    if len(entries) == 1 and cern_id in [id for id, shell, home in entries[0].login_list]:
        return entries[0].display_name
    raise ValueError("Data for CERN ID {} not found (or multiple matches were returned).".format(cern_id))


def discover_email(cern_id: str) -> str:
    phonebook = Phonebook(cern_id)
    entries = phonebook.query_data()
    # TODO return all cern emails instead of just the first one
    if len(entries) == 1 and cern_id in [id for id, shell, home in entries[0].login_list] and len(entries[0].emails) > 0:
        return entries[0].emails[0]
    raise ValueError("Data for CERN ID {} not found (or multiple matches were returned).".format(cern_id))


class Phonebook:
    
    def __init__(self, search_string=''):
        if search_string == '':
            raise ValueError('At least any search string should be provided!')
        self.search_string = search_string
        self.results = list()
        self.found_entries = list()

    # def __itr__(self):
    #     pass

    def query_data(self):
        arguments = ['phonebook', '-all', self.search_string]
        process_handle = subprocess.Popen(args=arguments, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process_handle.communicate()
        if len(stderr) > 0:
            print('Error: {}'.format(stderr))
            self.found_entries = list()
        else:
            results = self.split_result(stdout.decode())
            for result in results:
                entry = PhonebookEntry(result)
                self.found_entries.append(entry)
        return self.found_entries

    def split_result(self, data):
        possible_results = list()
        line_data = data.split("\n")
        line_number = 0
        start_line = None
        end_line = None
        while line_number < len(line_data):
            if start_line is None and line_data[line_number].startswith('#--'):
                start_line = line_number + 1
                line_number = line_number + 1
                continue

            if end_line is None and line_data[line_number].startswith('#--') :
                end_line = line_number - 1
                dataset = line_data[start_line:end_line+1]
                possible_results.append(dataset)
                start_line = line_number + 1
                end_line = None

            line_number = line_number + 1

        results = list()
        for possible_result in possible_results:
            if possible_result[0].startswith('Surname'):
                results.append(possible_result)

        return results


class PhonebookEntry(object):
    def __init__(self, data):
        self.surname = ''
        self.first_name = ''
        self.display_name = ''
        self.emails = list()
        self.phones = list()
        self.mobiles = list()
        self.fax_list = list()
        self.department = ''
        self.group = ''
        self.post_box = ''
        self.location = ''
        self.organizations = list()
        self.computer_center_id = ''
        self.login_list = list()
        self.process_data(data)

    def process_data(self, data):
        start_account_section_found = False
        for line in data:
            if len(line.strip()) == 0:
                continue
            if line.startswith('#'):
                continue
            if line.startswith('Surname'):
                self.extract_surname(line)
                continue
            if line.startswith('Firstname'):
                self.extract_first_name(line)
                continue
            if line.startswith('Display Name'):
                self.extract_display_name(line)
                continue
            if line.startswith('E-mail') or line.startswith('Other E-mail'):
                # Ignoring "External E-mail line"
                self.extract_email(line)
                continue
            if line.startswith('Telephone'):
                self.extract_phone(line)
                continue
            if line.startswith('Mobile'):
                self.extract_mobile(line)
                continue
            if line.startswith('Facsimile'):
                self.extract_fax(line)
                continue
            if line.startswith('Department'):
                self.extract_department(line)
                continue
            if line.startswith('Group'):
                self.extract_group(line)
                continue
            if line.startswith('POBox'):
                self.extract_post_box(line)
                continue
            if line.startswith('Bld. Floor-Room'):
                self.extract_location(line)
                continue
            if line.startswith('Organization'):
                self.extract_organization(line)
                continue
            if line.startswith('Computer Center ID'):
                self.extract_computer_center_id(line)
                continue
            if line.startswith('Login'):
                start_account_section_found = True
                continue

            if start_account_section_found:
                self.extract_account_data(line)

    def __str__(self):
        string  = 'Phonebook entry\n'
        string += 'Surname      : %s\n' % self.surname
        string += 'Firstname    : %s\n' % self.first_name
        string += 'Display name : %s\n' % self.display_name
        for email in self.emails:
            string += 'Email        : %s\n' % email
        for phone in self.phones:
            string += 'Phone        : %s\n' % str(phone)
        for mobile in self.mobiles:
            string += 'Mobile       : %s\n' % str(mobile)
        for fax in self.fax_list:
            string += 'Fax          : %s\n' % str(fax)
        string += 'Department   : %s\n' % self.department
        string += 'Group        : %s\n' % self.group
        string += 'Building     : %s\n' % self.location
        for organisation in self.organizations:
            string += 'Organization : %s\n' % organisation
        string += 'Computer Center ID : %s\n' % self.computer_center_id
        for login in self.login_list:
            string += 'Login name   : %s\n' % login[0]
            string += 'Shell        : %s\n' % login[1]
            string += 'Home         : %s\n' % login[2]
        return string

    def extract_surname(self, line):
        element, data = line.split(':', 1)
        self.surname = data.strip(' ')

    def extract_first_name(self, line):
        element, data = line.split(':', 1)
        self.first_name = data.strip(' ')

    def extract_display_name(self, line):
        element, data = line.split(':', 1)
        self.display_name = data.strip(' ')

    def extract_email(self, line):
        element, data = line.split(':', 1)
        data = data.strip(' ')
        self.emails.append(data)

    def extract_phone(self, line):
        numbers = self.extract_fax_phone(line)
        self.phones.append(numbers)

    def extract_mobile(self, line):
        numbers = self.extract_fax_phone(line)
        self.mobiles.append(numbers)

    def extract_fax(self, line):
        numbers = self.extract_fax_phone(line)
        self.fax_list.append(numbers)

    def extract_fax_phone(self, line):
        element, data = line.split(':', 1)
        data = data.strip(' ')
        number_external, number_internal = data.split('(')
        number_external = number_external.strip(' (')
        number_internal = number_internal.replace('internal:', '')
        number_internal = number_internal.strip(' ()')
        return number_external, number_internal

    def extract_department(self, line):
        element, data = line.split(':', 1)
        data = data.strip(' ')
        self.department = data

    def extract_group(self, line):
        element, data = line.split(':', 1)
        data = data.strip(' ')
        self.group = data

    def extract_post_box(self, line):
        element, data = line.split(':', 1)
        data = data.replace('(internal mail)', '')
        data = data.strip(' ')
        self.post_box = data

    def extract_location(self, line):
        element, data = line.split(':', 1)
        data = data.strip(' ')
        self.location = data

    def extract_organization(self, line):
        element, data = line.split(':', 1)
        data = data.strip(' ')
        self.organizations.append(data)

    def extract_computer_center_id(self, line):
        element, data = line.split(':', 1)
        data = data.strip(' ')
        self.computer_center_id = data

    def extract_account_data(self, line):
        data = line.split(' ')
        self.login_list.append((data[0].strip(), data[-2].strip(), data[-1].strip()))
