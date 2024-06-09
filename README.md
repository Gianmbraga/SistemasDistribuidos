# Description
 `NOTE: The project WIKI is in pt-BR.`

 A mini multi-threaded E-commerce college project. 
 
 It uses the Client-Server architecture model aproach to achive the objective. Making easy to understand how a distribued system works and the implications.

 For this project we use the **Python for the Client** and **JAVA for the Server**
 By default the client is set for the 127.0.0.1


***

## Getting started

#### Dependencies and requirements
We tested our project in a **WINDOWS 10** enviroment for both Client and Server. It should work for other OS or Windows 11 __but we can't guarantee that it will work.__

##### Enviroment
```
[Tested] Operating System (OS): Windows 10
```
</br>

##### Client 

```cmd
Python - Version 3.11.5
Dependencies: numpy
```

##### Server 

```md
[DEV/RUN] JAVA JDK - Version 17.0.5

Dependencias: 
- jackson-annotations-2.15.2
- jackson-core-2.15.2.jar
- jackson-databind-2.15.2.jar
```

***
</br>

## Usage

##### Client Configuration
In the client code, change this 2 variables to the desired host and port.
```py
host = '127.0.0.1'  # Server IP address (current is LOCALHOST)
port = 5000         # Server port (Must be the same as the server)
```

We also provide a easy to access function for changing the Multi-threaded Clients to be ran. These functions and their configuration for what product, quantity or amount is especified on the relatory provided.


Current supported easy to access functions:
```py
ClientObjects = Teste2Clientes()
ClientObjects = Teste10Clientes() 
ClientObjects = Teste1000Clientes()

```
Replace any of the `ClientObjects` variable line in the python main to change the Test mode. By default we keep `Teste1000Clientes()` to run.
```py
if __name__ == "__main__":
    #apenas altere a funcao desejada e a magica acontecera
    ClientObjects = Teste1000Clientes()
```


##### Server Configuration

In the server code, you can change the port in the Object's argument as below.
```java
public static void main(String args[]) {
    new Server(5000); // Server port (Must be the same as the client)
}
```

#### Run Server
To run the server use the command below.
```cmd
java -jar .\CalebProjeto-server.jar
```

#### Run Client

To run the client just run the following line in your preferred terminal.
```cmd
python CalebProjeto-client.py
```
