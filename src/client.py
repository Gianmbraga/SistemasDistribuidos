## PROJETO SISTEMAS DISTRIBUIDOS - Prof. Calebe ##
# 
# INTEGRANTES:
# 
# Aline Stolai - RA: 22.121.003-2
# Gian Malheiros Braga - RA: 22.121.054-5
# João Lucas Freitas de Almeida Rocha - RA: 22.121.004-0
# Lucca Kirsten da Costa - RA: 22.121.121-2
# 
##################################################

import socket
import struct
import time
import threading
import json
from numpy import random 

host = '127.0.0.1'  # Server IP address
port = 5000         # Server port    

class Controller:
    def __init__(self, socket: socket):
        self.client_socket_control = socket
    
    def sendRequest(self, message: str) -> None:
        # Send message length and message
        message_data = message.encode('utf-8')
        message_length = len(message_data)
        self.client_socket_control.sendall(struct.pack('>H', message_length) + message_data)
        #print(f"Sent: {struct.pack('>H', message_length) + message_data}")       

    def receiveRequest(self) -> str:
        # Receive message length 4-byte long
        message_length_data = self.client_socket_control.recv(4)
        if not message_length_data:
            raise BufferError("Message has no length.") 
        message_length = struct.unpack('>I', message_length_data)[0]

        # Receive message data
        received_data = b''
        while len(received_data) < message_length:
            data = self.client_socket_control.recv(message_length - len(received_data))
            if not data:
                break
            received_data += data
        return received_data.decode('utf-8')

class Client:
    def __init__(self, user: str, auto_opt: int = -1, prod_l: list = [], qtd_l: list = []):
        self.user_name = user
        self.address = host
        self.addr_port = port
        self.auto_option = auto_opt
        self.buy_prod_id = prod_l
        self.buy_qtd = qtd_l
        
        self.IsRobotMode = False
        #assert(check_prod == check_qtd, "Para automatizar é necessário ambos os vetores com tamanhos IQUAIS!")
        if (auto_opt != -1):
            self.IsRobotMode = True
            if ((len(prod_l) == 0 or len(qtd_l) == 0) and auto_opt == 1):
                self.Mensagem("Modo autonomo desativado, falta parametros de lista!")
                self.IsRobotMode = False
         
    def Mensagem(self, msg: str) -> None:
        print("[LOJA ZAP-2] " + msg)
         
    def showOptions(self) -> int:

        if self.IsRobotMode:
            self.Mensagem("Modo Autonomo ativo!")
            return self.auto_option
        
        self.Mensagem("Bem-vindo, selecione uma das opções abaixo:")
        option = -1;
        while (True):

            print("[1] Comprar");
            print("[2] Extrato\n");            

            try:

                print("Escolha: ", end="");
                option = int(input())

                if (option > 0 and option <= 2):
                    return option
                self.Mensagem("Opção invalida! Tente novamente\n\n")
                continue
            except ValueError:
                self.Mensagem("Só é permitido apenas números! Tente novamente\n\n")
                continue

    def printBuyResults(self, json_str: str) -> None:     
        json_Result = json.loads(json_str)
        self.Mensagem("RESULTADO DA COMPRA:")
        # Iterate over the "resultado" list
        for result in json_Result["resultado"]:
            print(f"[{result['id']}] {result['descricao']}")
        print()

    def run(self) -> None:
        self.Mensagem("Cliente inicializado aguarde...");
        while True:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((host, port))
                
                self.control = Controller(self.client_socket)
                
                self.Mensagem("Conectado! Obtendo informações da loja...");
                break
            except (ConnectionRefusedError, TimeoutError) as ce:
                print(f"Aguardando conexão com o servidor... [PING STATUS]\n{ce}")
                time.sleep(2.5)
            except OSError as e:
                print("An error occurred:", e)
                return
        ######################
        try:
            
            request = ""
            option = self.showOptions()
            
            if option == 1:
                self.control.sendRequest("""{"processo": "sincronizar"}""")
                
                ServerItems = self.control.receiveRequest()
                
                self.Mensagem("Lista de produtos obtida!")
                self.Mensagem("Escolha item por ID das opções:" + ServerItems + "\n")                 
                buyRequest = self.CreateBuyList()
                request = buyRequest
                
                self.control.sendRequest(request)
                
                ServerResultResponse = self.control.receiveRequest()

                self.printBuyResults(ServerResultResponse)
                
            elif option == 2:
                self.control.sendRequest("""{"processo": "extrato"}""")
            
                ServerExtrato = self.control.receiveRequest()
                self.Mensagem("\n====================[Extrato]====================\n" + ServerExtrato)
                print("\n=================================================\n")  
            else:
                self.Mensagem("Opção INVALIDA! Tente novamente.");
            
            self.Mensagem("Cliente finalizado!");
            pass
        except Exception as e:
            print(e)
        finally:
            self.client_socket.close()  
            
    def CreateBuyList(self) -> str:
        itemID = []
        itemQtd = []
        
        if self.IsRobotMode:
            return self.ClientShopCartToJson(self.buy_prod_id, self.buy_qtd)
        
        while True:
            HasAddItem = False
            HasAddQtd = False

            try:
                print("Item: ", end='')
                itemID.append(int(input()))
                HasAddItem = True
                
                print("Quantidade: ", end='')
                itemQtd.append(int(input()))
                HasAddQtd = True

                self.Mensagem("Item adicionado com sucesso!")

                print("\nAdicionar mais itens (s/n)? ", end='')
                add_answer = input()

                if add_answer == "s":
                    continue
                elif add_answer == "n":
                    self.Mensagem("Carrinho criado! Enviando pedido para o servidor...")
                    break
                else:
                    raise ValueError("lixo")

            except ValueError:
                if HasAddItem and HasAddQtd:
                    self.Mensagem("Utilize apenas 's' ou 'n' para mais itens! Tente novamente.\n")
                    continue
                else:
                    if HasAddItem:
                        itemID.pop()

                    if HasAddQtd:
                        itemQtd.pop()
                self.Mensagem("Só é permitido apenas números! Tente novamente\n")
        return self.ClientShopCartToJson(itemID, itemQtd)
    
    def ClientShopCartToJson(self, item_ids: list, item_qtd: list) -> str:
        json_data = {}

        # Create the root object
        json_data["usuario"] = self.user_name
        json_data["processo"] = "comprar"
        json_data["compra"] = []

        for item_id, item_qtd in zip(item_ids, item_qtd):
            json_data["compra"].append({"id": item_id, "quantidade": item_qtd})

        json_string = json.dumps(json_data, indent=4)
        #print(json_string)  # Print the JSON string for verification
        return json_string                    


def randlist(min_inclusive: int, max_inclusive: int, amount: int) -> list:
    rand_list = []

    for _ in range(amount):
        randnum = random.randint(min_inclusive, max_inclusive+1)
        rand_list.append(randnum)    
    return rand_list

#Teste com parametros customizado (tudo com comentario acima é editavel)
def TesteNClientes() -> list[Client]:
    print("Insira quantidade de Clientes:", end='')
    users = int(input())
    
    #Quantidade de produtos na loja (ou entre 1 a N)
    productRangeToBuy = 5
    #modo de cliente: 1 = COMPRAR | 2 = EXTRATO
    clientMode = 1
    
    ClientObjects = []
    for i in range(users):
        
        #Quantidade de items para comprar
        amountToBuy = random.randint(2, 4+1) #2 a 4

        #Quantidade de itens para comprar um mesmo produto
        quantityToBuy = 1
        
        products_id = randlist(1, productRangeToBuy, amountToBuy)
        quantity    = randlist(1, quantityToBuy, amountToBuy)        
        ClientObjects.append(Client(f"ROBOT-{i}", clientMode, products_id, quantity))
    return ClientObjects

#Testes exemplo no PDF
def Teste2Clientes():
    users = 2
    
    ClientObjects = []
    for i in range(users):
        amountToBuy = random.randint(2, 4+1) #2 a 4
        
        products_id = randlist(1, 5, amountToBuy)
        quantity    = randlist(1, 1, amountToBuy)        
        ClientObjects.append(Client(f"T02_ROBOT-{i}", 1, products_id, quantity))
    return ClientObjects

def Teste10Clientes():
    users = 10
    
    ClientObjects = []
    for i in range(users):
        amountToBuy = random.randint(2, 4+1) #2 a 4
        
        products_id = randlist(1, 10, amountToBuy)
        quantity    = randlist(1, 1, amountToBuy)        
        ClientObjects.append(Client(f"T10_ROBOT-{i}", 1, products_id, quantity))
    return ClientObjects

def Teste1000Clientes():
    users = 1000
    
    ClientObjects = []
    for i in range(users):
        amountToBuy = 1 #i tem
        
        products_id = randlist(1, 10, amountToBuy)
        quantity    = randlist(1, 1, amountToBuy)        
        ClientObjects.append(Client(f"T1K_ROBOT-{i}", 1, products_id, quantity))
    return ClientObjects
#FIM dos Testes exemplo no PDF ##


if __name__ == "__main__":
    #apenas altere a funcao desejada e a magica acontecera
    ClientObjects = Teste1000Clientes()
    
    #Client(f"TESTE").run()
    
    #Run Client(s)
    for ClientObj in ClientObjects:
        
        thread = threading.Thread(target=ClientObj.run)
        thread.start()
        #note, thread.join nao e usado pois n queremos threads aguardarem outras, 
        # queremos rodando ao mesmo tempo!
    pass
