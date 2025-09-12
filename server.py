from socket import *
from threading import Thread, RLock
import re

#initiailizng threads and arrays(temporary data storage)
threadLock= RLock()
itemList = []
userList = []
operationList = []

class ClientThread(Thread):
    #Constructor
    def __init__(self, clientsocket, clientaddress):
        Thread.__init__(self)
        self.clientsocket = clientsocket #For sending and receiving messages
        self.clientaddress = clientaddress #Useful for logging or identifying the connected client
        self.load() #load the arrays from the txt files


    #When we run the program this function will run
    def run(self):
        msg = "Message: Connection successful".encode()
        self.clientsocket.send(msg)

        customer_purchase_list=[] #This array is for checking if customer exist in the system

        while True:
            clientMsg = self.clientsocket.recv(1024).decode()
            #Seperate message into a list
            message = clientMsg.split(";")


            #If login panel opened
            if message[0] == "login":
                with threadLock:
                    userRole = self.checking(message[1], message[2]) #call checking function

                #If user found with correct password and username
                if userRole != -1:
                    #Send login success message to the client
                    serverMsg = ("loginsuccess;" + message[1] + ";" + userRole).encode()
                    self.clientsocket.send(serverMsg)
                #If user not found with correct password and username
                else:
                    #Send failure message to the client
                    serverMsg = ("loginfailure").encode()
                    self.clientsocket.send(serverMsg)

            #If store panel opened by the store owner and the operation which will be done is purchase
            if message[0] == "purchase":
                with threadLock:  # We used "with" because in this way we prevent deadlock. It releases the thread by itself
                    for operation in operationList:
                        if operation[1] == message[1] and operation[0] == "purchase" and operation[
                            2] not in customer_purchase_list:
                            customer_purchase_list.append(operation[2])

                purchasedItemList = message[3].split(",") #Split the purchased items
                itemDetailList = []
                error_flag=0
                total_cost=0

                not_available_items=""

                for item in purchasedItemList: #Seperate each item details for checking
                    itemDetailList.append(item.split("-"))

                #For checking if there is enough purchased item that is stocked
                for detail in itemDetailList:
                    for item in itemList:
                        if detail[1] == item[0] and detail[2].lower() == item[2]:
                            if int(detail[0]) > int(item[4]):
                                not_available_items += item[1] + "-" + item[2] + ";"
                                error_flag=1
                            break

                #If not send availability error to the client
                if error_flag==1:
                    proper_format_item_list = not_available_items[:-1]
                    availability_message=("availabilityerror;"+proper_format_item_list).encode()
                    self.clientsocket.send(availability_message)

                #If there is enough items we must update the item quantity int items.txt
                else:
                    for item in itemList:
                        for itemDetail in itemDetailList:
                            if item[0] == itemDetail[1] and item[2] == itemDetail[2].lower():
                                total_cost += int(item[3]) * int(itemDetail[0])
                                item[4] = int(item[4]) - int(itemDetail[0])

                    self.updatingFile("items.txt") #Updating the file

                    found = 0
                    subList_purchase = []

                    #If operation details match with the one that is in operations.txt then we must append it to that operation
                    with threadLock:
                        for operation in operationList:
                            if operation[2] == message[-1] and operation[0] == "purchase" and operation[1] == message[1]:
                                for item in purchasedItemList:
                                    operation.append(item)
                                found = 1
                                break

                    #If not create a new operation and append it to the operation list
                        if found == 0:
                            subList_purchase.append(message[0])
                            subList_purchase.append(message[1])
                            subList_purchase.append(message[-1])
                            for i in purchasedItemList:
                                subList_purchase.append(i)
                            operationList.append(subList_purchase)

                    self.updatingFile("operations.txt") #Updating the file

                    #Sending Purchase successful message to the client
                    successmessage_purchase = ("purchasesuccess;"+ str(total_cost)).encode()
                    self.clientsocket.send(successmessage_purchase)

            # If store panel opened by the store owner and the operation which will be done is return
            if message[0] == "return":
                with threadLock:  # We used "with" because in this way we prevent deadlock. It releases the thread by itself
                    for operation in operationList:
                        if operation[1] == message[1] and operation[0] == "purchase" and operation[
                            2] not in customer_purchase_list:
                            customer_purchase_list.append(operation[2])

                # Split the purchased items
                returnItemList = message[3].split(",")
                returnItemListSplitted=[]
                flag=0

                for x in returnItemList: #Seperate each item details for checking
                    returnItemListSplitted.append(x.split("-"))


                for operation in operationList:
                    # If no items have been purchased, there are no items that can be returned by the specific customer.
                    if operation[1] == message[1] and operation[2] == message[4] and operation[0] == "purchase":
                        for returnItem in returnItemList:
                            if returnItem not in operation[3:]:
                                flag = 1
                                break

                    #If item is already returned
                    elif operation[1] == message[1] and operation[2] == message[4] and operation[0] == "return":
                        for returnItem in returnItemList:
                            if returnItem in operation[3:]:
                                flag = 1
                                break
                    #If there is no customer with that name exists
                    elif message[4] not in customer_purchase_list:
                        flag=2
                        break

                if flag == 1:
                    errorMessage = ("returnerror").encode()
                    self.clientsocket.send(errorMessage)
                elif flag == 2:
                   errorMessage = ("returnfailure").encode()
                   self.clientsocket.send(errorMessage)
                else:
                    for item in itemList:
                        for returnItem in returnItemListSplitted:
                            if item[0] == returnItem[1] and item[2] == returnItem[2]:
                                # If item is returned update the quantity of that item
                                item[4] = int(item[4]) + int(returnItem[0])

                    self.updatingFile("items.txt")

                    found = 0
                    with threadLock:
                        # If operation details match with the one that is in operations.txt then we must append it to that operation
                        for operation in operationList:
                            if operation[2] == message[-1] and operation[0] == "return" and operation[1] == message[1]:
                                for item in returnItemList:
                                     operation.append(item)
                                found = 1
                                break
                        # If not create a new operation and append it to the operation list
                        if found==0:
                            sublist = []
                            sublist.append(message[0])
                            sublist.append(message[1])
                            sublist.append(message[-1])
                            for i in returnItemList:
                                sublist.append(i)
                            operationList.append(sublist)

                    self.updatingFile("operations.txt")

                    successmessage_return="returnsuccess".encode()
                    self.clientsocket.send(successmessage_return)

            #Creating dictionary for each of the item ID's and assigning them for finding total quantity
            if clientMsg == "report1":
                d = {}
                for operation in operationList:
                    for o in operation[3:]:
                        if operation[0] == "purchase":
                            newList = o.split("-")
                            if newList[1] in d.keys():
                                d[newList[1]] = d[newList[1]] + int(newList[0])
                            else:
                                d[newList[1]] = int(newList[0])

                # Finding the key with the highest number of bought items
                maximumValue = max(d.values())
                maximumKeys = [key for key, value in d.items() if value == maximumValue] #list comprehension

                answer = ""
                #Making it string so that we can send to the client
                for i in maximumKeys:
                    answer += ";" + str(i)

                report_answer = (clientMsg + answer).encode()
                self.clientsocket.send(report_answer)

            #Creating the dictionary for each of the store that will have a number of purchase+return operations
            elif clientMsg == "report2":
                d_counting = {}
                for operation in operationList:
                    if operation[1] not in d_counting.keys():
                        d_counting[operation[1]] = 0

                for operation in operationList:
                    if operation[1] in d_counting.keys():
                        d_counting[operation[1]] = d_counting[operation[1]] + 1

                maximumValue = max(d_counting.values())
                maximumKeys = [key for key, value in d_counting.items() if value == maximumValue]

                answer_counting = ""
                for i in maximumKeys:
                    answer_counting += ";" + str(i)

                report_answer = (clientMsg + answer_counting).encode()
                self.clientsocket.send(report_answer)

            #Creating the purchase dictionary for each of the stores that will have number of purchased items
            #Creating the return dictionary for each of the stores that will have number of returned items
            #Creating the income dictionary for each of the stores that will have the number of incomes(purchased-returned)
            elif clientMsg == "report3":
                d_income = {}
                d_purchase = {}
                d_return = {}

                # Creating dictionary for each store
                for operation in operationList:
                    if operation[0] == "purchase":
                        if operation[1] not in d_purchase.keys():
                            #example: {"magusa3":0} This is the format for each return and purchase dictionary
                            d_purchase[operation[1]] =  0

                    elif operation[0] == "return":
                        if operation[1] not in d_return.keys():
                            d_return[operation[1]] = 0

                for operation in operationList:
                    for o in operation[3:]:
                        newList = o.split("-")
                        for item in itemList:
                            if item[0] == newList[1] and operation[0] == "purchase" and item[2] == newList[2]:
                                #Total_purchase_price=quantity*price
                                d_purchase[operation[1]] = d_purchase[operation[1]] + (int(item[3]) * int(newList[0]))
                                break

                            elif item[0] == newList[1] and operation[0] == "return" and item[2] == newList[2]:
                                #Total_return_price=quantity*price
                                d_return[operation[1]]= d_return[operation[1]] + (int(item[3]) * int(newList[0]))
                                break

                for key in d_purchase.keys():
                    #Calculating income
                    if key not in d_return.keys():
                        d_income[key] = d_purchase[key] - 0 #This 0 is when there is no returned items
                    elif key in d_return.keys():
                        d_income[key] = d_purchase[key] - d_return[key]

                stringFormat = ""
                for items in d_income.items():
                    stringFormat += ";" + items[0] + ";" + str(items[1])

                income_answer = (clientMsg + stringFormat).encode()
                self.clientsocket.send(income_answer)

            elif clientMsg == "report4":
                d_color = {"red": 0, "black": 0}
                for operation in operationList:
                    for o in operation[3:]:
                        if operation[0] == "return":
                            newList = o.split("-")
                            if newList[1] == "1":
                                if newList[2] == "red":
                                    d_color["red"] = d_color["red"] + int(newList[0])
                                elif newList[2] == "black":
                                    d_color["black"] = d_color["black"] + int(newList[0])

                if d_color["red"] == 0 and d_color["black"] == 0:
                    color_answer = (clientMsg + ";No sales").encode()
                    self.clientsocket.send(color_answer)
                elif d_color["red"] > d_color["black"]:
                    color_answer = (clientMsg + ";Red").encode()
                    self.clientsocket.send(color_answer)
                elif d_color["black"] > d_color["red"]:
                    color_answer = (clientMsg + ";Black").encode()
                    self.clientsocket.send(color_answer)
                elif d_color["black"] == d_color["red"]:
                    color_answer = (clientMsg + ";Both Black and Red").encode()
                    self.clientsocket.send(color_answer)

    #This method is for checking the password and username
    def checking(self,username,password):
        for user in userList:
            if user[0] == username and user[1] == password:
                return user[2]

        return -1

    def updatingFile(self, filename):
        try:
            with threadLock:
                fileToBeReturned = ""
                itemsFile = open(filename, "w")  # writing to the file

                last_line_index = 0
                #If item is the last item in the list then don't add new line
                for item in itemList:
                    for i in item:
                        fileToBeReturned = fileToBeReturned + str(i) + ";"
                    fileToBeReturned = fileToBeReturned[:-1]
                    if last_line_index != len(itemList) - 1:
                        fileToBeReturned = fileToBeReturned + "\n"
                    last_line_index = last_line_index + 1

                itemsFile.write(fileToBeReturned)
                itemsFile.close()
        except IOError:  # If it cannot be opened print the appropriate message
            print("File cannot be opened!")
            exit(1)

        try:
            with threadLock:
                new_string = ""
                operationsFile = open("operations.txt", "w")

                last_line_index = 0
                # If operation is the last operation in the list then don't add new line
                for operation in operationList:
                    i = 0
                    for o in operation:
                        if i == len(operation) - 1:  # Check if it's the last element
                            new_string += str(o)
                        else:
                            new_string += str(o) + ";"
                        i = i + 1
                    if last_line_index != len(operationList) - 1:
                        new_string += "\n"
                    last_line_index = last_line_index + 1

                operationsFile.write(new_string)
                operationsFile.close()

        except IOError:  # If it cannot be opened print the appropriate message
            print("File cannot be opened!")
            exit(1)

    def load(self):
        #Clearing it so there will be no duplication
        itemList.clear()
        userList.clear()
        operationList.clear()
        try:
            usersFile = open("users.txt", "r") # Read the file
            operationsFile = open("operations.txt", "r")
            itemsFile = open("items.txt", "r")
        except IOError: # If it cannot be opened print the appropriate message
            print("File cannot be opened!")
            exit(1)

        records_users = usersFile.readlines()
        records_items = itemsFile.readlines()
        records_operations = operationsFile.readlines()

        # User List
        for each_record in records_users:
            eachUserList = re.sub(r'\n', '', each_record).split(";")
            userList.append(eachUserList)

        for x in userList:
            for y in userList:
                if x[2] == "store" and y[2] == "store" and x[0] == y[0] and x != y:
                    userList.remove(y)
            break   # Looking the list once is enough to check

        # Item List
        for each_record in records_items:
            eachItemList = re.sub(r'\n', '', each_record).split(";")
            if(eachItemList[2] == "red" or eachItemList[2] == "black"):
                itemList.append(eachItemList)

        # Operation List
        for each_record in records_operations:
            eachOperationList = re.sub(r'\n', '', each_record).split(";")
            operationList.append(eachOperationList)

        # Close the file
        usersFile.close()
        itemsFile.close()
        operationsFile.close()

        #Test Case
        #print(userList)
        #print(itemList)
        #print(operationList)

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 5000

    serversocket = socket(AF_INET, SOCK_STREAM)
    serversocket.bind((HOST, PORT))
    serversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    while True:
        serversocket.listen()
        clientsocket, clientaddress = serversocket.accept()
        newClient = ClientThread(clientsocket, clientaddress)
        newClient.start()
