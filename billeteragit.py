# Info: La primera vez que se corre el programa se crean billetera.txt y transacciones.txt
# Porfavor asegurarse de que esos archivos no existan en la carpeta del programa
# Una nueva billetera parte sin monedas ni saldos
# Para agregar monedas a la billetera use el comando 'Recibir'
# Cuando se le solicite direccion de una billetera para transferir fondos, por simplicidad cualquier string basta

import random, requests, string, sys
from datetime import datetime

monedasCMC = dict()
monedasBilletera = dict()
transacciones = list()
direccionBilletera = "HELLO"

# Imprime la lista de Comandos
def imprimirAyuda():
    print("""
Comandos:

Salir:      Salir de su e-wallet
Recibir:    Recibir una tranferencia desde otra cuenta.
Transferir: Transferir a otra cuenta.
Balance:    Balance de una moneda.
General:    Balance General.
Historico:  Movimientos e-wallet.
Ayuda:      Imprime esta lista de comandos.
""")


# Genera un diccionario Llave = Symbol , Valor = Precio en USD desde Coin Market Cap.
def CMC():
    COINMARKET_API_KEY = "2448e9c9-b938-4f0e-85f1-9878a7b41c87"
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': COINMARKET_API_KEY}

    data=requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest",headers=headers).json()

    for cripto in data["data"]:
        monedasCMC[cripto["symbol"]] = float(cripto["quote"]["USD"]["price"])

# Genera un diccionario Llave = codigoMoneda, Valor = tuple(cantidad, cotizacion) a partir de billetera.txt
# Genera una lista de transacciones a partir de transacciones.txt
def leer():
    global direccionBilletera
    f = open("billetera.txt", "r")
    while True:
        a = f.readline()
        l = a.split(":")
        if not a:
            break
        if l[0] == "Direccion":
            direccionBilletera = l[1]
            print("\n    "+direccionBilletera)
        else:
            monedasBilletera[l[0]] = float(l[1])
    f.close()

    f2 = open("transacciones.txt", "r")
    count = 0
    while True:
        a = f2.readline()
        if not a:
            break
        if count == 0:
            pass
        else:
            transacciones.append(a)
        count += 1
    f2.close()

# Graba la informacion de la billetera en billetera.txt
def escribir():
    f = open("billetera.txt", "w")
    f.write("Direccion:"+direccionBilletera.rstrip())
    for key, value in monedasBilletera.items():
        f.write("\n"+key+":"+str(value))
    f.close()

# Graba y Sale
def salir():
    escribir()
    print("\n\tAdios\n")
    sys.exit()

# Recibir fondos
def recibir(cuenta, moneda, cantidad):
    # Se actualizan el archivo transacciones.txt y la lista transacciones
    now = datetime.now()
    fechaHora = now.strftime("%d/%m/%Y %H:%M:%S")
    linea = "IN "+fechaHora+" "+cuenta+" "+moneda+" "+str(cantidad)
    f = open("transacciones.txt", "a")
    f.write("\n"+linea)
    f.close()
    transacciones.append(linea)

    # Se suma el monto si la moneda ya existe
    if moneda in monedasBilletera.keys():
        monedasBilletera[moneda] = monedasBilletera[moneda] + cantidad 
    # Se crea la moneda en la billetera y se le asigna la 'cantidad'
    else:
        monedasBilletera[moneda] = cantidad
    
    # Reportar cambios
    print("\tTransferencia Exitosa")
    print(linea+"\n")

# Transferir fondos
def transferir(cuenta, moneda, cantidad):
    
    # Chequea que la moneda exista en la billetera
    if not moneda in monedasBilletera.keys():
        print(f"**** No tienes { moneda } en tu billetera ****\n")
        return
    
    # Chequea que haya saldo suficiente
    if monedasBilletera[moneda] < cantidad:
        print("**** No tienes suficiente saldo ****\n")
        return

    # Se actualizan el archivo transacciones.txt y la lista transacciones
    now = datetime.now()
    fechaHora = now.strftime("%d/%m/%Y %H:%M:%S")
    linea = "OUT "+fechaHora+" "+cuenta+" "+moneda+" "+str(cantidad)
    f = open("transacciones.txt", "a")
    f.write("\n"+linea)
    f.close()
    transacciones.append(linea)

    # Se resta el monto
    monedasBilletera[moneda] = monedasBilletera[moneda] - cantidad
    
    # Reportar cambios
    print("\tTransferencia Exitosa")
    print(linea+"\n")

# Imprime en pantalla el balance para la 'moneda'
def balance(moneda):
    print()
    if not moneda in monedasBilletera.keys():
        print(f"**** No tienes { moneda } en tu billetera ****\n")
        return
    montoUSD = monedasCMC[moneda]*monedasBilletera[moneda]
    montoRedondeado = "{:.2f}".format(montoUSD)
    print(moneda+": " + str(monedasBilletera[moneda]) + "  =  USD$ " + montoRedondeado)
    print()
    
# Imprime el balance de todas la monedas + su valor total en USD
def general():
    print()
    totalUSD = 0
    for key, value in monedasBilletera.items():
        montoUSD = monedasCMC[key]*monedasBilletera[key]
        montoRedondeado = "{:.2f}".format(montoUSD)
        print(key+": " + str(monedasBilletera[key]) + "  =  USD$ " + montoRedondeado)
        totalUSD += montoUSD
    print()
    totalRedondeado = "{:.2f}".format(totalUSD)
    print("Total USD$ : " + totalRedondeado)
    print()

# Imprime los contenidos de 'transacciones'
def historico():
    print()
    for text in transacciones:
        print(text.rstrip("\n"))
    print()

# Chequea que la moneda exista en CoinMarketCap
def esmoneda(cripto):
    return cripto.upper() in monedasCMC

# Chequea que value sea convertible a float
def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Chequea la existencia de billetera.txt
try: 
    f = open("billetera.txt")
    f.close()
    print("\n\t\t¡Bienvenido a tu e-wallet!")
    
 # Si no existe crea el archivo billetera.txt y crea una direccion aleatorea para la billetera.
 # Crea también un archivo transacciones.txt destinado a registrar transacciones de la billetera.   
except: 
    print("    Es primera ves que corres este programa")
    print("\n\t\t¡Bienvenido a tu e-wallet!\n")
    m = True
    while m:
        a = input("Desea crear una nueva Billetera? S/N: ")
        if a == "s" or a == "S" or a == "si" or a == "Si":
            f = open("billetera.txt","w+")
            f2 = open("transacciones.txt","w+")
            letters = string.ascii_letters + string.digits
            nuevoCodigo = ''.join(random.choice(letters) for i in range(50))
            f.write("Direccion:"+nuevoCodigo)
            f2.write("Direccion:"+nuevoCodigo)
            f.close()
            f2.close()
            m = False

        elif a == "N" or a == "n" or a == "no" or a == "No":
            print("\n\tAdios\n")
            sys.exit()
        
# Inicializar el programa
CMC() # Llenar diccionario 'monedasCMC' con nombres de monedas y precios desde CoinMarketCap
leer() # Leer los archivos billetera.txt y transacciones.txt y llena el diccionario 'monedasBilletera' y la lista 'transacciones'
imprimirAyuda() # Imprime la lista de comandos por primera vez

# Ciclo principal
while True:
    command = input("Ingrese comando: ").rstrip()
    if command == "Salir" or command == "salir":
        salir()
    
    elif command == "Ayuda" or command == "ayuda":
        imprimirAyuda()
    
    elif command == "Recibir" or command == "recibir":
        print()
        
        direccion = input("Ingrese direccion de la billetera: ").rstrip()
        # Chequea que la direccion indicada no sea la direccion de la misma billetera

        while direccion == direccionBilletera.rstrip() or direccion == "":
            print("\n**** Direccion invalida o vacia: ingrese una direccion distinta a la suya ****\n")
            direccion = input("Ingrese direccion de la billetera: ").rstrip()

        nombre = input("Ingrese nombre de 3 letras de la moneda: ").rstrip()
        # Chequea que la moneda indicada exista en CoinMarketCap
        while not esmoneda(nombre):
            print("\n**** Moneda Invalida ****\n")
            nombre = input("Ingrese nombre de 3 letras de la moneda: ").rstrip()
        
        cantidad = input("Ingrese el monto de la transferencia: ").rstrip()
        # Chequea que 'cantidad' no sea un numero o que se usa '.' para indicar la parte decimal
        while "," in cantidad or not isfloat(cantidad) or float(cantidad) <0:
            print("\n**** Use '.' para dar valores decimales ****")
            print("**** Ingresar solamente numeros, no texto ****")
            print("**** Ingresar solamente numeros positivos ****\n")
            cantidad = input("Ingrese el monto de la transferencia: ").rstrip()
        cantidad = float(cantidad)
        print()
    
        recibir(direccion, nombre.upper(), cantidad)
        
    elif command == "Tranferir" or command == "transferir":
        print()
        direccion = input("Ingrese direccion de la billetera: ").rstrip()
        # Chequea que la direccion indicada no sea la direccion de la misma billetera
        while direccion == direccionBilletera.rstrip() or direccion == "":
            print("\n**** Direccion invalida o vacia: ingrese una direccion distinta a la suya ****\n")
            direccion = input("Ingrese direccion de la billetera: ").rstrip()

        nombre = input("Ingrese nombre de 3 letras de la moneda: ").rstrip()
        # Chequea que la moneda indicada exista en CoinMarketCap
        while not esmoneda(nombre):
            print("\n**** Moneda Invalida ****\n")
            nombre = input("Ingrese nombre de 3 letras de la moneda: ").rstrip()
        
        cantidad = input("Ingrese el monto de la transferencia: ").rstrip()
         # Chequea que 'cantidad' no sea un numero o que se usa '.' para indicar la parte decimal
        while "," in cantidad or not isfloat(cantidad) or float(cantidad) <0:
            print("\n**** Use '.' para dar valores decimales ****")
            print("**** Ingresar solamente numeros, no texto ****")
            print("**** Ingresar solamente numeros positivos ****\n")
            cantidad = input("Ingrese el monto de la transferencia: ").rstrip()
        cantidad = float(cantidad)
        print()
        
        transferir(direccion, nombre.upper() , cantidad)
    
    elif command == "Balance" or command == "balance":
        
        print()
        nombre = input("Ingrese nombre de 3 letras de la moneda: ").rstrip()
        # Chequea que la moneda indicada exista en CoinMarketCap
        while not esmoneda(nombre):
            print("\n**** Moneda Invalida ****\n")
            nombre = input("Ingrese nombre de 3 letras de la moneda: ").rstrip()
        balance(nombre.upper())
    
    elif command == "General" or command == "general":
        general()
    
    elif command == "Historico" or command == "historico":
        historico()
    
    else:
        print("\n**** Comando Invalido ****\n")