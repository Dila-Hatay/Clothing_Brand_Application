# Clothing Brand Application
This project implements a multithreaded client-server application in Python for a clothing brand.
It was developed as a team university assignment to practice multithreading, concurrent programming, network programming, and GUI development with Tkinter.

The client application will be used by the various stores of the brand. The customers can visit a store to look at item samples and try them on.
If the customer would like to purchase items, the store owner then places an order from the central warehouse to be delivered to the customer. 
A store owner will be responsible for reporting the purchases and returns of the store, and sending them to the server, and the analysis team at headquarters will be 
responsible for requesting some statistics related to the operations, which will be generated on the server.

When running the program, first you need to run the server file then client file to make the connection and the program will start. 
In your terminal, you can run them by typing the path of your python.exe followed by the file path.

An example is shown below:
& 'C:\Users\dilah\AppData\Local\Programs\Python\Python312\python.exe' 'C:\Users\dilah\OneDrive\Desktop\Clothing_Brand_Application\server.py' --> For server side
& 'C:\Users\dilah\AppData\Local\Programs\Python\Python312\python.exe' 'C:\Users\dilah\OneDrive\Desktop\Clothing_Brand_Application\client.py' ---> For client side

# Features
- Authentication
  - Client connects to the server and logs in with username & password.
  - Credentials are stored in users.txt (username;password;role)
  - Login supports two roles: store and analyst.

 # Store Panel
  - Store owners can:
      - Add purchase operations.
      - Add return operations (validated against past purchases).
  - The system updates:
    - items.txt → maintains stock availability.
    - operations.txt → logs purchases/returns.
  - Error handling for unavailable stock or invalid returns.
  - GUI includes product selection, quantity, color, and customer name input.

# Analyst Panel
- Analysts can request statistics from the server:
  - Most bought item overall.
  - Store with the highest number of operations.
  - Total generated income by each store.
  - Most returned color of the Basic T-shirt.
- Reports are calculated on the server and returned to the client.

# File Management
- users.txt → Stores user credentials and roles.
- items.txt → Tracks clothing items, colors, prices, and stock.
- operations.txt → Stores purchase and return operations.
- All files are updated consistently with thread-safe operations using RLock.
