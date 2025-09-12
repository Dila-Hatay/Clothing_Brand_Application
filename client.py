from doctest import master
from socket import *
from tkinter import *
from tkinter import messagebox

class ClientScreen(Frame):  # For the Login Panel:
    def __init__(self,clientsocket):
        Frame.__init__(self, master)
        self.clientsocket = clientsocket

        servermsg = self.clientsocket.recv(1024).decode()
        print(servermsg)

        # Login Window
        self.master.title("Login")
        self.pack()

        self.frame1 = Frame(self)
        self.frame1.pack(padx=5, pady=5)

        self.usernameLabel=Label(self.frame1,text="Username:")
        self.usernameLabel.pack(side=LEFT,padx=5,pady=5)
        self.usernameEntry=Entry(self.frame1,name="username")
        self.usernameEntry.pack(side=LEFT,padx=5,pady=5)

        self.frame2=Frame(self)
        self.frame2.pack(padx=5, pady=5)

        self.passwordLabel=Label(self.frame2,text="Password:")
        self.passwordLabel.pack(side=LEFT,padx=5,pady=5)
        self.passwordEntry=Entry(self.frame2,name="password",show="*")
        self.passwordEntry.pack(side=LEFT,padx=5,pady=5)

        self.frame3=Frame(self)
        self.frame3.pack(padx=5, pady=5)

        self.loginButton=Button(self.frame3,text="Login",command=self.buttonPressed)
        self.loginButton.pack(padx=5,pady=5)

    def buttonPressed(self):
        username=self.usernameEntry.get()
        password=self.passwordEntry.get()

        # Sending the entered user details to check
        clientMsg=("login;" + username + ";" + password).encode()
        self.clientsocket.send(clientMsg)

        # Getting the result of checking
        serverMsg=self.clientsocket.recv(1024).decode()
        resulted_message=serverMsg.split(";")

        if resulted_message[0]=="loginsuccess":
            self.master.destroy()
            if resulted_message[2] == "store":  # If the user is store owner open the store panel
                storePanel = StorePanel(self.clientsocket, username)
                storePanel.mainloop()

            elif resulted_message[2] == "analyst":  # If the user analyst open the analyst panel
                analyst = AnalystPanel(self.clientsocket)
                analyst.mainloop()

        elif resulted_message[0]=="loginfailure":
            messagebox.showinfo("Error","Login failed")

class StorePanel(Frame):    # For the Store Panel:
    def __init__(self,clientsocket, usernameEntry):
        Frame.__init__(self, master)
        self.usernameEntry=usernameEntry
        self.clientsocket = clientsocket
        self.master.title("Store Panel")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.geometry()
        self.grid(sticky=W+E+N+S)

        self.frame1=Frame(self)
        self.frame1.grid(sticky=W, padx=160)

        self.itemLabel=Label(self.frame1,text="Items",font=("Arial",22))
        self.itemLabel.grid()

        self.clothingItem=[(BooleanVar(),"Basic T-shirt"),(BooleanVar(),"Leather Jacket"),(BooleanVar(),"Robe of the Weave"),
                           (BooleanVar(),"Plaid Shirt"),(BooleanVar(),"D4C Graphic T-shirt"),(BooleanVar(),"Denim Jeans"),
                           (BooleanVar(),"Hodd-Toward Designer Shorts")]
        self.colorList=["red","black"]

        self.colorListList=[]

        self.itemList=[]

        self.frame2 = Frame(self)
        self.frame2.grid()

        row=1
        i = 0
        for item in self.clothingItem:
            self.eachItem=[]
            self.color_var = StringVar()
            self.color_var.set("red")   # Setting default color as red
            self.colorListList.append(self.color_var)

            self.itemSelection=Checkbutton(self.frame2,text=item[1],variable=item[0], command=self.checking)
            self.itemSelection.grid(row=row,column=0,padx=30 ,pady=20,sticky=W)
            self.eachItem.append(item)

            self.quantityLabel=Label(self.frame2,text="Quantity:")
            self.quantityLabel.grid(row=row,column=1,padx=(0,20))

            self.quantityEntry=Entry(self.frame2, width=5)
            self.quantityEntry.config(state=DISABLED)   # Making them disabled so that user need to first select the item name then quantity and color.
            self.quantityEntry.grid(row=row,column=2,padx=5,pady=5)
            self.eachItem.append(self.quantityEntry)

            self.colorLabel=Label(self.frame2,text="Color:")
            self.colorLabel.grid(row=row,column=3,padx=(30,5),pady=5)

            column=4

            for color in self.colorList:
                self.colorSelection=Radiobutton(self.frame2, text=color, variable=self.colorListList[i], value=color, selectcolor="#42c8f5") # color code of light blue
                self.colorSelection.config(state=DISABLED)
                self.colorSelection.grid(row=row,column=column,padx=5,pady=5)
                self.eachItem.append(self.colorSelection)

                column=column+1
            row=row+1
            i=i+1
            self.itemList.append(self.eachItem)

        self.frame3=Frame(self)
        self.frame3.grid()

        self.customerNameLabel=Label(self.frame3,text="Customer Name:")
        self.customerNameLabel.grid(row=1, column = 2, padx=(115,0))
        self.customerNameEntry=Entry(self.frame3)
        self.customerNameEntry.grid(row=1, column=3,padx=5,pady=5)

        self.frame4=Frame(self)
        self.frame4.grid()

        self.button = Button(self.frame4, text="Purchase", command=self.purchaseFunction)
        self.button.grid(row=1, column=2,padx=(130,0),pady=20)

        self.button = Button(self.frame4, text="Return", command=self.returnFunction)
        self.button.grid(row=1, column=3, padx=(20,15), pady=20)

        self.button = Button(self.frame4, text="Close", command=self.closeFunction)
        self.button.grid(row=1, column=4, padx=5, pady=20)

    def purchaseFunction(self): # When the purchase button pressed
        total=0
        list_selected = ""

        if self.check_empty_button():   # Checks if quantity is empty
            return
        if self.check_all_disabled_error(): # Checks if no item selected
            return
        if self.check_customer_text_area(): # Checks if the customer name is empty
            return

        # Calculate total quantity:
        for item in self.itemList:
           if item[0][0].get()==True:
                value=float(item[1].get())
                total+=value

        # For each item quantity:
        i=0
        for item in self.itemList:
            eachList = ""
            color = self.colorListList[i].get()
            if item[1].get() != "":
                if color == "red" or color == "black":
                    eachList += item[1].get() + "-" + str(i+1) +"-" + color + ","

            if eachList != "":
                list_selected += eachList
            i=i+1

        proper_format_list = list_selected[:-1] # Removing the last "," in the format

        messagePurchase=("purchase;"+ self.usernameEntry+";"+str(total)+";" + proper_format_list + ";" + self.customerNameEntry.get()).encode()
        self.clientsocket.send(messagePurchase)

        purchase_message= self.clientsocket.recv(1024).decode()
        purchase_message_list=purchase_message.split(";")

        if purchase_message_list[0] == "availabilityerror":   # If availability error happened (one of the item is out of stock or have less than needed)
            message_format = ""
            for x in purchase_message_list[1:]: # Getting the error message from the format [item1,item2,...] and making it as --> item1\n item2\n
                message_format += x + "\n"
            messagebox.showinfo("Purchase Error", message_format)

        elif purchase_message_list[0]=="purchasesuccess":   # If no error occured while purchase
            messagebox.showinfo("Purchase successful", "Total cost: " + purchase_message_list[1])

    def returnFunction(self):   # When the return button pressed
        total = 0
        list_selected = ""

        if self.check_empty_button(): # Checks if quantity is empty
            return
        if self.check_all_disabled_error(): # Checks if no item selected
            return
        if self.check_customer_text_area(): # Checks if the customer name is empty
            return

        # Calculate total quantity:
        for item in self.itemList:
            if (item[0][0].get() == True):
                value = float(item[1].get())
                total += value

        # For each item quantity:
        i = 0
        for item in self.itemList:
            eachList = ""
            color = self.colorListList[i].get()
            if item[1].get() != "":
                if color == "red" or color == "black":
                    eachList += item[1].get() + "-" + str(i + 1) + "-" + color.lower() + ","

            if eachList != "":
                list_selected += eachList
            i = i + 1

        proper_format_list_return = list_selected[:-1]

        messageReturn = ("return;"+self.usernameEntry+ ";" + str(total) + ";" + proper_format_list_return + ";" + self.customerNameEntry.get()).encode()
        self.clientsocket.send(messageReturn)

        return_message = self.clientsocket.recv(1024).decode()
        if return_message=="returnerror":
            messagebox.showinfo(return_message,"Unsuccessful operation - please recheck the items")
        elif return_message=="returnfailure":
            messagebox.showinfo(return_message,"No customer exist with that name try again")
        elif return_message=="returnsuccess":
            messagebox.showinfo(return_message,"Success!")

    def closeFunction(self):    # When the close button pressed, closes the socket and the store panel
        self.clientsocket.close()
        self.master.destroy()

    # Checking Functions:
    # 1)This function will check if the item button is pressed. If it is pressed activate the other entries and buttons
    def checking(self):
        for items in self.itemList:
            if items[0][0].get():
                for i in range(1,len(items)):
                    items[i].config(state=NORMAL)
            if not items[0][0].get():
                items[1].delete(0, END)
                for i in range(1, len(items)):
                    items[i].config(state=DISABLED)

    # 2)This function will check there is any empty entry
    def check_empty_button(self):
        for item in self.itemList:
            if item[0][0].get()==True:
                if item[1].get() == "":
                    messagebox.showinfo("Empty Entry", "Empty Entry detected. Please try again.")
                    return True
        return False

    # 3)This function will check if the there is a selected item or not
    def check_all_disabled_error(self):
        flag=0
        for item in self.itemList:
            if item[0][0].get()==True:
                flag=1
        if flag==0:
            messagebox.showinfo("Error", "No item box is selected please try again")
            return True
        else:
            return False

    # 4)This function will check if customer name entry area is empty
    def check_customer_text_area(self):
        if self.customerNameEntry.get() == "":
            messagebox.showinfo("Error", "Please enter the customer name")
            return True
        return False


class AnalystPanel(Frame):  # For the Analyst Panel:
    def __init__(self, clientsocket):
        Frame.__init__(self)
        self.clientsocket = clientsocket
        self.master.title("Analyst Panel")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.geometry()
        self.grid(sticky=W + E + N + S)

        self.frame1 = Frame(self)
        self.frame1.grid(sticky=W, padx=160)

        self.itemLabel = Label(self.frame1, text="Reports", font=("Arial", 22))
        self.itemLabel.grid()

        self.reports = ["   (1) What is the most bought item?",
                        "   (2) Which store has the highest number of operations?",
                        "   (3) What is the total generated income of the store?",
                        "   (4) What is the most returned color for the Basic T-shirt?"]

        self.frame2 = Frame(self)
        self.frame2.grid()

        self.report_var = StringVar()
        self.report_var.set(self.reports[0])    # Setting the first report1 as a default selected report

        row = 0
        for report in self.reports:
            self.reportSelection = Radiobutton(self.frame2, text=report, variable=self.report_var, value=report)
            self.reportSelection.grid(row=row, column=0, padx=(0, 60), pady=5, sticky=W)
            row += 1

        self.frame3 = Frame(self)
        self.frame3.grid()

        self.createButton = Button(self.frame3, text="Create", command=self.create, width=10)
        self.createButton.grid(row=1, pady=5, sticky=W)

        self.closeButton = Button(self.frame3, text="Close", command=self.closeFunction, width=10)
        self.closeButton.grid(row=1, padx=100)

    def create(self):   # If create button is pressed
        if self.report_var.get() == self.reports[0]:    # If report1 is selected
            reportMessage = "report1".encode()
            self.clientsocket.send(reportMessage)

            answer = self.clientsocket.recv(1024).decode()

            # Making the answer message in proper format for meesagebox
            answer_split = answer.split(";")
            answer = ""
            for i in answer_split[1:]:
                answer = answer + i + ","

            messagebox.showinfo(answer_split[0], "The maximum bought item(s) with ID: " + answer[:-1])  # [:-1] --> Deletes the last "," in the string

        elif self.report_var.get() == self.reports[1]:  # If report2 is selected
            reportMessage = "report2".encode()
            self.clientsocket.send(reportMessage)

            answer = self.clientsocket.recv(1024).decode()

            # Making the answer message in proper format for meesagebox
            answer_split = answer.split(";")
            answer = ""
            for i in answer_split[1:]:
                answer = answer + i + ","

            messagebox.showinfo(answer_split[0], "The store(s) with highest number of operation: " + answer[:-1])   # [:-1] --> Deletes the last "," in the string

        elif self.report_var.get() == self.reports[2]:  #If report3 is selected
            reportMessage = "report3".encode()
            self.clientsocket.send(reportMessage)

            answer_income = self.clientsocket.recv(1024).decode()
            answer_split = answer_income.split(";")
            answer_income_split = answer_split[1:]

            formatted_answer_income = ""
            for i in range(len(answer_income_split)):
                if i+1 > len(answer_income_split)-1:    # To check the i + 1 is out of range which means the message is complete
                    break
                elif i % 2 == 0:    # Getting the elements in the even index (store name) and combining them with the i + 1 index (income)
                    formatted_answer_income += answer_income_split[i] + " - " + answer_income_split[i + 1] + "\n"

                    # Example: [magusa3, 42, dereboyucd1, 41] which will be then in the form:
                    #          magusa3 - 42
                    #          dereboyucd1 - 41

            messagebox.showinfo(answer_split[0], "The income for each store: \n" + formatted_answer_income)

        elif self.report_var.get() == self.reports[3]:  # If report4 is selected
            reportMessage = "report4".encode()
            self.clientsocket.send(reportMessage)

            answer_color = self.clientsocket.recv(1024).decode()
            answer_color_split = answer_color.split(";")

            messagebox.showinfo(answer_color_split[0], answer_color_split[1])   # Shows message as only the most returned color for the Basic T-shirt

    def closeFunction(self):    # If close button pressed closes the analyst panel and client socket
        self.clientsocket.close()
        self.master.destroy()

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 5000

    clientsocket = socket(AF_INET, SOCK_STREAM)
    clientsocket.connect((HOST, PORT))
    window = ClientScreen( clientsocket)
    window.mainloop()