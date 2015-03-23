import json
import exceptions
import sys


class Notes:
    def __init__(self, note_dic=None,
                 bkp_file=None):
        self.note_dic = note_dic or dict()
        self.bkp_file = bkp_file or '.notes'
        self.load()

    def load(self):
        bkp = open(self.bkp_file, 'r')
        self.note_dic = json.loads(bkp.read())

    def read(self):
        while True:
            sys.stdout.write("Which? ")
            name = sys.stdin.readline()\
                .strip()
            try:
                print(self.note_dic[name])
                break
            except exceptions.KeyError:
                pass

    def write(self):
        sys.stdout.write("Name? ")
        name = sys.stdin.readline().strip()
        sys.stdout.write("Body? ")
        body = sys.stdin.readline().strip()
        self.note_dic[name] = body

    def delete(self):
        while True:
            sys.stdout.write("Which? ")
            name = sys.stdin.readline()\
                .strip()
            try:
                del self.note_dic[name]
                break
            except exceptions.KeyError:
                pass

    def list(self):
        for name in self.note_dic:
            print(name)

    def persist(self):
        bkp_file = open(self.bkp_file, 'w')
        bkp_file.write(
            json.dumps(self.note_dic))
        bkp_file.close()


#read, list, write, delete, save

def run():
    notes = Notes()
    while True:
        sys.stdout.write("what? ")
        action = sys.stdin.readline().strip()
        if action == 'r':
            notes.read()
        elif action == 'l':
            notes.list()
        elif action == 'w':
            notes.write()
        elif action == 'd':
            notes.delete()
        elif action == 's':
            notes.persist()
        elif action == 'q':
            break

run()
