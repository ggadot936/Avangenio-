import re
import socket
import logging
import sys
import time
logger = logging.getLogger(__name__)
logging.basicConfig(filename='server.log',encoding='utf-8',format="{asctime}-{levelname}-{message}",level=logging.DEBUG,style="{",datefmt="%d-%m-%Y %H:%M:%S")
# logging.basicConfig(level=logging.DEBUG)

HOST,PORT,SIZE,FORMAT=socket.gethostname(),6000,1024,'utf-8'


def socket_service(port_to_use):
    if not port_to_use:
        sys.stdout.write(f"Type port server or press Enter to use default({PORT})\n")
        port_input=input('->')
    else:
        port_input=port_to_use
    # create a socket at server side using TCP / IP protocol
    instance=socket.socket()
    try:
        # bind socket using tupla(Host,Port)
        instance.bind((HOST,int(port_input) if port_input else PORT))
        # allow maximum connection to the socket
        instance.listen(1)
        logger.info(f"Service up on HOST: {socket.gethostbyname(HOST)}, PORT: {int(port_input) if port_input else PORT}")
        sys.stdout.write(f"Service up on HOST: {socket.gethostbyname(HOST)}, PORT: {int(port_input) if port_input else PORT}\n")
        return instance
    except Exception as e:
        logger.critical(f'Service down: {e}')
        sys.stdout.write(f'Service down: {e}\n')
        raise

def analisys(data_params):
    answer={'result':[]}
    for ch in data_params:
        if len(ch.lower().split('aa'))==1:
            # get all numbers from chain
            numbers_cant="".join(re.split(r'[^0-9]*',ch))
            # get all letters from chain
            words_cant="".join(re.split(r'[^a-zA-Z]*',ch))
            # ponderate the chain
            res=(len(words_cant)*1.5+len(numbers_cant)*2)/ch.count(" ")
            type_metric='normal'
        else:
            res=1000
            type_metric='discard'
            logger.warning(f"Chain rule (aa, AA, aA, Aa) detected, the metric will be 1000 by default >> {ch}")
        data={
            'metric':res,
            'chain':ch,
            'typeMetric':type_metric.capitalize()
        }
        answer['result'].append(data)
    return answer

def server_service(port_used=None):
    socket_instance=socket_service(port_used)
    # wait till a client accept connection
    connection,address=socket_instance.accept()
    # Display client address
    logger.info(f"Connection from: {address}")
    sys.stdout.write(f'Connection from: {address}\n')
    chains=[]
    while True:
        # get message from client after decoding from binary string
        data_received=connection.recv(SIZE).decode(FORMAT)
        if not data_received or data_received=='exit':
            sys.stdout.write("No request, closed connection\n")
            break
        if data_received=='finish':
            sys.stdout.write("All chains for file chains.txt received\n")
            msg_to_send=analisys(chains)
            sys.stdout.write("Analisys completed\nSending results\n")
            for x in msg_to_send['result']:
                # send message to the client after encoding into binary string
                connection.send(f'Chain: {x['chain']}\nMetric: {x['metric']}\nTypeMetric: {x['typeMetric']}\n'.encode(FORMAT))
                connection.recv(SIZE).decode(FORMAT)
            connection.send('completed'.encode(FORMAT))
            sys.stdout.write("Results sended\nWaiting for client to close connection\n")
        else:
            chains.append(data_received)
            connection.send('OK'.encode(FORMAT))
    # close the connection
    connection.close()
    socket_bind=socket_instance.getsockname()
    socket_instance.close()
    logger.warning(f'Service restarting')
    sys.stdout.write(f'Service restarting\n')
    server_service(socket_bind[1])

if __name__=='__main__':
    start=time.perf_counter()
    server_service()
    end=time.perf_counter()
    logger.info(f"Process finished in {end-start} seconds")
