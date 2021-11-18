import pymongo

client = pymongo.MongoClient()
Database = client.Homework_001
Collection = Database.work
WorkInfo = {'id': 1, 'name': 'Limpid', 'age': 21, 'sex': 'male', 'salary': 3000}
Collection.insert(WorkInfo)

adds = ['add id=']
ups = ['update']
dels = ['del id=']

def Showinfo():
    See = Collection.find()
    for each in See:
        print(each)
HelpInfo = 'The basic usage like this:\n\ncommand [col_title1=info col_title2=info ...]\nfor example:\n\nshow\nshow id=1\nshow age=20 name=jike\n\nadd id=8 name=limpid age=21 sex=male salary=9999\n\ndel id=3\n\nupdate id=2 name=limpid'
print('Please input your command or type "help" to view more usage:')
# InputCom = input()

while 1:
    InputCom = input()
    if InputCom == 'help':
            print(HelpInfo)
    elif InputCom == 'show':
            Showinfo()
    elif InputCom == 'add':
            print('Everyone must have an id ')
    elif InputCom == 'del':
            print('You have to identify who you want to delete')
    elif InputCom[0:7] in adds:
            d = InputCom.find('name')
            i = InputCom.find('age')
            q = InputCom.find('sex')
            p = InputCom.find('salary')
            NewInfo = {'id': int(InputCom[7:d-1]), 'name': InputCom[14:i-1], 'age': int(InputCom[i+4:q-1]), 'sex': InputCom[q+4:p-1], 'salary': int(InputCom[p+7:])}
            Collection.insert(NewInfo)
    elif InputCom[0:7] in dels:
            Collection.delete_many({'id': int(InputCom[-1])})
    elif InputCom[0:6] in ups:
        if InputCom[12:14] == 'na':
            Collection.update({'id': int(InputCom[10])}, {'$set': {'name': InputCom[17:]}})
        elif InputCom[12:14] == 'se':
            Collection.update({'id': int(InputCom[10])}, {'$set': {'sex': InputCom[16:]}})
        elif InputCom[12:14] == 'sa':
            Collection.update({'id': int(InputCom[10])}, {'$set': {'salary': int(InputCom[19:])}})
        else:
            Collection.update({'id': int(InputCom[10])}, {'$set': {'age': int(InputCom[16:])}})
    elif InputCom == 'exit':
        break
    else:
            print(HelpInfo)
