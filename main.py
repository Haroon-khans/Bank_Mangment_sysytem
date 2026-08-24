import json
import random
import string
from pathlib import Path

class Bank:

    database="data.json"
    data= []

    try:
        if Path(database).exists():
            with open(database) as fs:
                data = json.loads(fs.read())
        else:
            print("no such file exist")

    except Exception as err:
        print(f"error occured as {err} ")


    @classmethod
    def __update(cls):
        with open(Bank.database,"w") as fs:
            fs.write(json.dumps(Bank.data))
    @classmethod
    def __accountnumbergenerate(cls):
        alpha = random.choices(string.ascii_letters,k=3)
        dig = random.choices(string.digits,k=3)
        spchr= random.choices("!@#$%&*",k=1)
        id = alpha + dig + spchr
        random.shuffle(id)
        return"".join(id)

    



    
    

    def creataccount(self):
        info={
            "name":input("enter a name:-"),
            "age" :int(input("Enter a age:-")),
            "email":input("enter your email:-"),
            "acc_no" : Bank.__accountnumbergenerate(),
            "pin" : int(input("Enter a pin number:-")),
            "balance": 0

        }

        if info['age']<18 or len(str(info['pin']))!=4:
            print("sorry you cannot create account")

        else:
            for i in info:
                print(f"{i}:{info[i]}")
            print("Account Creates Successfully")
            Bank.data.append(info)
            Bank.__update()
    def depositingmoney(self):
        acc_no = input("Enter a Account Number:-")
        pin = int(input("Enter a pin number:-"))

        userdata= [i for i in Bank.data  if i['acc_no']==acc_no and i["pin"]==pin]

        if userdata==False:
            print("no such user data found")
        else:
            amount=int(input("Enter an amount you want to deposit:-"))
            if amount>10000 or amount<0:
                print("invalid amount,deposit under 1 to 10000")
            else:
                userdata[0]['balance']+=amount
                print("Amount deposit successfully")
                Bank.__update()

    def withdrawmoney(self):
        acc_no = input("Enter a Account Number:-")
        pin = int(input("Enter a pin number:-"))
        
        userdata= [i for i in Bank.data  if i['acc_no']==acc_no and i["pin"]==pin]
        
        if userdata==False:
                print("no such user data found")
        else:
             amount=int(input("Enter an amount you want to deposit:-"))
             if amount>userdata[0]['balance']:
                print("you dont have that much money")
             else:
                userdata[0]['balance']-=amount
                print("Amount Withdraw successfully")
                Bank.__update()
    def showdetails(self):
        acc_no = input("Enter a Account Number:-")
        pin = int(input("Enter a pin number:-"))
                
        userdata= [i for i in Bank.data  if i['acc_no']==acc_no and i["pin"]==pin]
                
        if userdata==False:
            print("no such user found")
        else:
            print("your details are\n\n\n")
            for i in userdata[0]:
                print(f"{i}:{userdata[0][i]}")

    def updatedetails(self):
        acc_no = input("Enter a Account Number:-")
        pin = int(input("Enter a pin number:-"))
                        
        userdata= [i for i in Bank.data  if i['acc_no']==acc_no and i["pin"]==pin]
                        
        if userdata==False:
            print("no such user found")
        else:
            print("press enter to skip or update")
            print("you cannot update age,account number and balance")
            newdata={
                "name":input("Enter a new name:-"),
                "email":input("Enter a new email or press enter to skip:-"),
                "pin" : int(input("Enter a new pin number or press enter to skip:-"))

            }

            if newdata['name']=="":
                newdata['name'] = userdata['name']
            if newdata["email"]=="":
                newdata["email"]=userdata["email"]
            if newdata['pin']=="":
                newdata["pin"]= userdata["pin"]

            newdata['age']= userdata[0]['age']
            newdata['acc_no'] = userdata[0]['acc_no']
            newdata['balance'] =userdata[0]['balance']

            if type(newdata['pin'])==str:
                newdata['pin']==int(newdata['pin'])

            for i in newdata:
                if newdata[i]==userdata[0][i]:
                 continue
                else:
                    userdata[0][i]= newdata[i]
            Bank.__update()
            print('details updated successfully')
    def delete(self):
        acc_no = input("Enter a Account Number:-")
        pin = int(input("Enter a pin number:-"))
                                
        userdata= [i for i in Bank.data  if i['acc_no']==acc_no and i["pin"]==pin]
                                
        if userdata==False:
            print("no such user found")
        else:
            print("press y for deleting account and press n to skip")

            if userdata=="n" or userdata=="N":
                print("bypassed")
            else:
                index = Bank.data.index(userdata[0])
                Bank.data.pop(index)
                print("Account Deleted Successfuly")
                Bank.__update()




    
user= Bank()
print("press 1 for creating account")
print("press 2 for depositing money")
print("press 3 for withdraw money")
print("press 4 for show details")
print("press 5 for updating details")
print("press 6 for deleting account")


check = int(input("enter your response:-"))

if check ==1:
    user.creataccount()
if check==2:
    user.depositingmoney()
if check==3:
    user.withdrawmoney()
if check==4:
    user.showdetails()
if check==5:
    user.updatedetails()
if check==6:
    user.delete()
