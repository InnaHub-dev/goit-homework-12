import calendar
import functools
import pickle
import re
from datetime import datetime
from collections import UserDict
from typing import Callable


class MyException(Exception):
    pass

class AddressBook(UserDict):

    index: str = 0
        
    def __getitem__(self, name):
        if not name in self.data.keys():
            raise MyException("This user isn't in the Book")
        user = self.data[name]
        return user
 
    def add_record(self, record) -> str:
        self.data.update({record.name.value:record})
        return 'Done!'
    
    def delete_record(self, name) -> str:
        try:
            self.data.pop(name)
            return f"{name} was removed"
        except KeyError:
            return "This user isn't in the Book"
        
    def get_contacts(self, file_name):
        with open(file_name, 'ab+') as fh:
            fh.seek(0)
            try:
                self.data = pickle.load(fh)
            except EOFError:
                pass   
        
    def iterator(self, n = 2):
        if len(self.data) > self.index:
            yield from [self.data[name] for name in sorted(self.data.keys())[self.index:self.index + n]]
            self.index += n
        else:
            raise StopIteration
            
    def show_records(self):
        batch = self.iterator()
        try:
            return "\n".join([record.show_record() for record in batch])
        except RuntimeError:
            self.index = 0
            return 'the end'
        
    
    def write_contacts(self, file_name) -> None:
        with open(file_name, "wb") as fh:
            pickle.dump(self, fh)
            

class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

class Birthday(Field):

    format: str = None
    formats = ['%d/%m', '%d/%m/%Y', '%d-%m', '%d-%m-%Y']

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, birthday):  
        format = self.validate_date(birthday)
        if format != None:
            self.__value = birthday
            self.format = format
        else:
            raise ValueError(f"The birthday wasn't added, it should be in one of the formats: {', '.join([f for f in Birthday.formats])}")  

    def validate_date(self, date):
        for format in Birthday.formats:
            try:
                datetime.strptime(date, format)
                return format
            except ValueError:
                pass


class Name(Field):
    pass


class Phone(Field):
   
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, phone):
        digits = sum([d.isdigit() for d in phone])
        match = re.match('^[+0-9-()]{7,18}$', phone)
        if digits < 7:
            raise ValueError("The number wasn't added. It should have at least 7 digits.")
        elif not match:
            raise ValueError("The number wasn't added. It can contain only the following characters: digits 0-9, '-', '(', ')', '+'.")
        self.__value = phone

class Record:

    def __init__(self, name: Name, phone: Phone=None, birthday: Birthday=None) -> None:
        self.name = name
        self.phones = [phone] if phone else []
        self.birthday = birthday

    def add_birthday(self, date: Birthday) -> None:
        self.birthday = date

    def add_phone(self, phone: Phone) -> None:
        self.phones.append(phone)

    def add_phones(self, phones: list[Phone]):
        if phones[0].value != '':
            self.phones.extend(phones)

    def days_to_birthday(self):
        if not self.birthday:
            return f"{self.name.value}'s birthday is unknown"
        date_bd = datetime.strptime(self.birthday.value, self.birthday.format)
        current_day = datetime.now()
        date_bd = datetime(year=current_day.year, month=date_bd.month, day=date_bd.day)
        difference = (date_bd - current_day).days
        if difference == 0:
            return f"{self.name.value}'s birthday is today!"
        elif difference < 0:
                difference = difference + 365 + calendar.isleap(current_day.year)
        return f"{self.birthday.value} It's {difference} days to {self.name.value}'s birthday."


    def delete_phone(self, pos: int = 0) -> None:
        if len(self.phones) > 1:
            pos = self.ask_index()
        try:
            self.phones.remove(self.phones[pos])
            return 'Done!'
        except:
            return pos

    def edit_phone(self, phone: Phone, pos: int = 0) -> str:    
            if len(self.phones) > 1:
                pos = self.ask_index()
            elif len(self.phones) == 0:
                self.phones.append(phone)
            try:
                self.phones[pos] = phone
                return 'Done!'
            except:
                return pos

    def show_record(self):
        return f"{self.name.value}: {', '.join([phone.value for phone in self.phones])} {self.birthday.value if self.birthday else ''}"
    
    def show_phone(self):
        return f"{self.name.value}: {', '.join([phone.value for phone in self.phones])}"

    def ask_index(self):
        print(self.name.value) 
        for i, number in enumerate([phone.value for phone in self.phones], 0): 
            print(f'{i}: {number}')
        while True: 
            try:        
                pos = int(input('Enter the index of a phone you want to edit >>> '))
                if pos > len(self.phones) - 1:
                    raise IndexError
                return pos
            except IndexError:
                return 'Wrong index. Try again.'
            except ValueError:
                return 'Index should be a number. Try again.'


def decorator_input(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*words):
        try:
            return func(*words)
        except KeyError as err:
            return err
        except IndexError:
            return "You didn't enter the phone/birthday or a user"
        except TypeError:
            return "Sorry, this command doesn't exist"
        except Exception as err:
            return err
    return wrapper

@decorator_input
def add_birthday(*args: str) -> str:
    record = contacts.get(args[0])
    record.add_birthday(Birthday(args[1]))
    return 'Done!'

@decorator_input
def add_phone(*args: str) -> str:
    record = contacts.get(args[0])
    record.add_phone(Phone(args[1]))
    return 'Done!'

@decorator_input
def add_user(*args: str) -> str:
    name = Name(args[0])
    if name.value in contacts.keys():
        return "This user already exists."
    else:
        record = Record(name)
        mes = 'The user was added!'
        try:
            phone = Phone(args[1])
            record.add_phone(phone)
        except IndexError:
            phone = None
        except ValueError as err:
            mes = f'{mes} {err}'
        try:
            birthday = Birthday(args[2])
            record.add_birthday(birthday)
        except IndexError:
            birthday = None
        except ValueError as err:
            mes = f"{mes} {err}"  
        contacts.add_record(record)
        
        return mes

@decorator_input   
def birthday(*args: str) -> str:
    record = contacts.get(args[0])
    return record.days_to_birthday()

@decorator_input
def change(*args: str) -> str:
    record = contacts.get(args[0])
    mes = record.edit_phone(Phone(args[1]))
    return mes

@decorator_input
def delete_phone(*args: str) -> str:
    record = contacts.get(args[0])
    mes = record.delete_phone()
    return mes

@decorator_input
def delete_user(*args: str) -> str:
    return contacts.delete_record(args[0])

def get_command(words: str) -> Callable:
    for key in commands_dict.keys():
        try:
            if re.search(fr'\b{words[0].lower()}\b', str(key)):
                func = commands_dict[key]
                return func
        except re.error:
            break
    raise KeyError("This command doesn't exist") 

@decorator_input
def goodbye() -> str:
    return 'Goodbye!'

@decorator_input
def hello() -> str:
    return 'How can I help you?'

@decorator_input
def phone(*args: str) -> str:
    record = contacts[args[0]]
    return record.show_phone()

@decorator_input
def show(*args: str) -> str:
    found = []
    arg = re.sub('\+', '\\+', args[0])
    for record in contacts.values():
        match = re.search(arg, f"{record.name.value}|{'|'.join([phone.value for phone in record.phones])}")
        if match:
            found.append(record)
    if len(found) == 0:
        return "No matches"
    return "\n".join([record.show_record() for record in found])

contacts = AddressBook()
contacts.get_contacts('contacts.bin')

commands_dict = {('hello','hi', 'hey'):hello,
                 ('add',):add_user,
                 ('add_birthday',): add_birthday,
                 ('add_phone',):add_phone,
                 ('birthday',): birthday,
                 ('show',): show,
                 ('change',):change,
                 ('delete_phone',):delete_phone,
                 ('delete',):delete_user,
                 ('phone',):phone,
                 ('showall',):contacts.show_records,
                 ('goodbye','close','exit','quit'):goodbye
}

def main():

    while True:
        words = input(">>> ").split(' ')
        try:
            func = get_command(words)
        except KeyError as error:
            print(error)
            continue
        print(func(*words[1:])) 
        if func.__name__ == 'goodbye':
            contacts.write_contacts('contacts.bin')
            break

if __name__ == '__main__':
    main()