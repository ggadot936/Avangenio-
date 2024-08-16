import logging
import os
import random
import socket
import string
import sys
import time

logger = logging.getLogger(__name__)
logging.basicConfig(filename='client.log',encoding='utf-8',format="{asctime}-{levelname}-{message}",level=logging.INFO,style="{",datefmt="%d-%m-%Y %H:%M:%S")
# logging.basicConfig(level=logging.DEBUG)

HOST,PORT,SIZE,FORMAT,AMOUNT_CHAINS=socket.gethostname(),6000,1024,'utf-8',1000000

def socket_service():
    sys.stdout.write(f"Type IP address server or press Enter to use default({HOST})\n")
    host_input=input('->')
    sys.stdout.write(f"Type port server or press Enter to use default({PORT})\n")
    port_input=input('->')
    # create a socket at server side using TCP / IP protocol
    instance=socket.socket()
    try:
        # connect it to server using tupla(Host,Port)
        instance.connect((host_input if host_input else HOST,port_input if port_input else PORT))
        logger.info("Connection established")
        sys.stdout.write("Connection established\n")
        return instance
    except Exception as e:
        logger.critical(f'Connection refused: {e}')
        sys.stdout.writel(f'Connection refused: {e}\n')
        raise

# Insert 3 to 5 whitspaces so that they are not consecutive
def insert_whitespace(chain,len_chain):
    index_saw,result,cant_whitespces=[0,len(chain)-1],list(chain),random.choice(range(3,6))
    for n in range(cant_whitespces):
        select_index=random.choice(range(len_chain))
        while select_index in index_saw:
            select_index=random.choice(range(len_chain))
        result[select_index]="-"
        index_saw.extend([select_index + si for si in range(3)])
        if n==cant_whitespces:
            logger.debug(f"Whitespaces validated correctly with {n} spaces")
    return "".join(result).replace('-'," ")

def content():
    # character string length from 50 to 100 randomly
    len_chain=random.choice(range(50,100))
    # generate allowed character string
    chain="".join(random.choices(f'{string.ascii_letters}{string.digits}',k=len_chain))
    return insert_whitespace(chain,len_chain)

def generate_content_file():
    msg_info=f"Type amount of chains between 1 and {AMOUNT_CHAINS} or press enter for use default({AMOUNT_CHAINS})\n"
    msg_info_generated=f"Chains generated\n"
    result=None
    sys.stdout.write(msg_info)
    amount_chains=input('->')
    if amount_chains:
        while not amount_chains.isdigit():
            sys.stdout.write(f"Amount is not valid ({amount_chains}), is not a number\n")
            sys.stdout.write(msg_info)
            amount_chains=input('->')
        else:
            while int(amount_chains) > AMOUNT_CHAINS:
                sys.stdout.write(f"Amount is not valid ({amount_chains}), is bigger than {AMOUNT_CHAINS}\n")
                sys.stdout.write(msg_info)
                amount_chains=input('->')
            else:
                sys.stdout.write(f'Generating {amount_chains} chains\n')
                # generate character string list using default amount
                result = list(map(lambda m: content(),range(int(amount_chains))))
                sys.stdout.write(msg_info_generated)
                return result
    else:
        sys.stdout.write(f'Generating {AMOUNT_CHAINS} chains\n')
        # generate character string list using default amount
        result = list(map(lambda m: content(),range(int(AMOUNT_CHAINS))))
        sys.stdout.write(msg_info_generated)
        return result

def make_file(type_file,filename,response):
    with open(filename,'w') as file:
        if type_file:
            # generate file chains.txt
            content_file=list(map(lambda x: x if response.index(x)== len(response)-1 else f"{x}\n",response))
            file.writelines(content_file)
            logger.info(f"Chains saved in {filename}")
            sys.stdout.write(f"Chains saved in {filename}\n")
            file.close()
        else:
            # generate file response from server.txt
            file.writelines(response)
            logger.info(f"Response saved in {filename}")
            sys.stdout.write(f"Response saved in {filename}\n")
            file.close()
    return {"filename":filename,"result":response,'path':os.path.dirname(__file__)}

def client_service():
    socket_instance=socket_service()
    sys.stdout.write("Type start to begin!\n")
    msg_to_write=input('->')
    while msg_to_write.lower().strip() != 'start':
        sys.stdout.write("Wrong command!\n")
        msg_to_write=input("->")
    else:
        answer,done=[],False
        try:
            response=generate_content_file()
            request=make_file(True,'chains.txt',response)
            logger.info(f"Chains file generated, see: {request['path']}\\{request['filename']}")
            sys.stdout.write(f"Chains file generated, see: {request['path']}\\{request['filename']}\n")
            sys.stdout.write(f'Sendig chains from file {request['filename']}\n')
            # sending characters strings to server for analisys
            for chain in request['result']:
                # send message to server after encoding into binary string
                socket_instance.send(chain.encode(FORMAT))
                # get message from server after decoding from binary string
                socket_instance.recv(SIZE).decode(FORMAT)
            logger.info(f'Sended to server {len(request['result'])} chains')
            sys.stdout.write(f'Sended to server {len(request['result'])} chains\n')
            socket_instance.send('finish'.encode(FORMAT))
            # receiving characters strings from server for output
            while not done:
                data_received=socket_instance.recv(SIZE).decode(FORMAT)
                if not data_received or data_received=='completed':
                    done=True
                    output=make_file(False,'Responses.txt',answer)
                    logger.info(f"File generated for all response, see: {output['path']}\\{output['filename']}")
                    sys.stdout.write(f"File generated for all response, see: {output['path']}\\{output['filename']}\n")
                    output_res=make_file(False,'Normal metric.txt',list(filter(lambda b: len(b.split("\nTypeMetric: Normal\n"))>1,answer)))
                    logger.info(f"File generated for metric type normal, see: {output_res['path']}\\{output_res['filename']}")
                    sys.stdout.write(f"File generated onfor metric type normal, see: {output_res['path']}\\{output_res['filename']}\n")
                    break
                answer.append(data_received)
                socket_instance.send('OK'.encode(FORMAT))
            sys.stdout.write("Press Enter to exit\n")
            msg_to_write=input("->")
        except Exception as e:
            logger.error(f"An error has ocurred: {e}")
            sys.stdout.write(f"An error has ocurred: {e}\n")
    socket_instance.close()

if __name__=='__main__':
    start=time.perf_counter()
    client_service()
    end=time.perf_counter()
    logger.info(f"Process finished in {end-start} seconds")