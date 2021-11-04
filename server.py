import os
import random
import socket
import datetime
import getpass
import csv


HOST = '127.0.0.1'
PORT = 64000
key = str(random.randint(99999, 10000001))

listening = True

users_info = 'users_info.csv'

log_file = 'log.txt'
log_info = {1: 'Сервер начал работу', 2: 'Сервер отключен', 3: 'Соединение установлено', 4: 'Прослушивание порта',
                5: 'Смена порта',
                6: 'Получение данных от клиента', 7: 'Отправка данных', 8: 'Соединение с клиентом прервано',
                9: 'Показ логов', 10: 'Показ команд',
                11: 'Повторная попытка ввода пароля'}

help_com = ['listen - прослушивание порта', 'quit - отключение сервера', 'show logs - показ логов']

class Server():

    def __init__(self, now_using, host):
        self.now_using = now_using
        self.host = host

    @staticmethod
    def main():
        if users_info in os.listdir(os.getcwd()):
            pass
        else:
            s = open(users_info, 'w')
            s.close()

        used_port = getpass.getpass(prompt="Введите порт: ", stream=None)
        used_port = Server.check(used_port)
        if used_port == False:
            while used_port == False:
                print('Попробуйте еще раз')
                used_port = getpass.getpass(prompt="Введите порт: ", stream=None)
                used_port = Server.check(used_port)
                if used_port != False:
                    break
        s = Server(used_port, HOST)
        s.commands()

    def commands(self):
        Server.create_log(1)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while True:
                try:
                    s.bind((HOST, self.now_using))
                    break
                except:
                    self.change_port(self.now_using+1)
                    Server.create_log(5)
            s.listen(5)
            print(f'Прослушивание порта: {self.now_using}')
            Server.create_log(4)
            while True:
                command = input('Введите команду: ')
                if command == 'help':
                    print(' '.join(Server.help_com))
                    Server.create_log(10)
                elif command == 'quit':
                    Server.create_log(2)
                    raise SystemExit
                elif command == 'show logs':
                    print('Логи: ')
                    Server.create_log(9)
                    with open(log_file, 'r') as ss:
                        text = ss.read()
                        print(text)

                elif command == 'listen':
                    print(f'Прослушивание порта: {self.now_using}')
                    if listening:
                        try:
                            conn, addr = s.accept()
                            Server.create_log(3)
                            Server.identify_users(addr[0], conn)
                            with conn:
                                while True:
                                    text = Server.receive_info(conn)
                                    if text == 'exit':
                                        comm = []
                                        # чтение и запись файла
                                        with open(users_info, 'r') as file:
                                            reader = csv.reader(file, delimiter=',')
                                            for i, row in enumerate(reader):
                                                comm.append(row)
                                                if row[0] == addr[0]:
                                                    comm[i][3] = 'False'
                                                    break
                                        with open(users_info, 'w') as file:
                                            writer = csv.writer(file, delimiter=',')
                                            writer.writerows(comm)
                                    elif text:
                                        Server.send_info(conn, text)
                                    else:
                                        break
                        except:
                            break
                elif command != '':
                    print('Такой команды нет')

    @staticmethod
    def identify_users(ip, sock):
        comm = []
        with open(users_info) as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                comm.append(row)
        for i, row in enumerate(comm):
            if row[0] == ip:
                if row[3] == 'True':
                    sock.send(f'Добро пожаловать, {row[1]}'.encode())
                    break
                else:
                    count_pass = 1
                    while True:
                        sock.send(f'check {row[1]}'.encode())
                        answer = sock.recv(1024).decode()
                        data = Server.code(row[4], answer)
                        if data == row[2]:
                            sock.send(f'Добро пожаловать, {row[1]}'.encode())
                            comm[i][3] = 'True'
                            break
                        else:
                            if count_pass == 3:
                                Server.create_log(8)
                                sock.send(f'again {count_pass}'.encode())
                                break
                            count_pass +=1
                            Server.create_log(11)
                            # sock.send(f'Введен неправильно пароль, повторите еще'.encode())

                    break
        else:
            sock.send('login'.encode())
            name = sock.recv(1024).decode()
            sock.send('password'.encode())
            password = sock.recv(1024).decode()
            password = Server.code(key, password)
            sock.send(f'Добро пожаловать, {name}'.encode())
            comm.append([ip, name, password, 'True', key])
        with open(users_info, 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(comm)

    @staticmethod
    def check(used_port):
        try:
            used_port = int(used_port) if used_port != '' else PORT
            used_port = used_port if 1 < used_port < 64000 else PORT
            return used_port
        except:
            return False
        
    @staticmethod
    def code(n, m):
        n = n*(len(m)//len(n)) + n[-(len(m) % len(n)):]
        return ''.join(map(chr, [i ^ x for i, x in zip(map(ord, m), map(ord, n))]))


    def user_info(self):
        # Создание файла для хранение данных о пользователей
        if users_info in os.listdir(os.getcwd()):
            pass
        else:
            s = open(users_info, 'w')
            s.close()



    @staticmethod
    def send_info(sock, data):
        msg = bytearray(f'Сообщение: {data}\n(Сообщение длиной {len(data)} символов)'.encode('utf-8'))
        Server.create_log(7)
        sock.send(msg)

    @staticmethod
    def receive_info(sock):
        msg = sock.recv(1024)
        if msg:
            print(msg.decode('utf-8'))
            text = msg.decode('utf-8').split('\t')[0]
            Server.create_log(6)
            return msg
        else:
            Server.create_log(8)
            return False

    @staticmethod
    def create_log(code):
        with open(log_file, 'a') as file:
            file.write(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') + '\t' + log_info[code] + '\n')

    def change_port(self, port):
        self.now_using = port

if __name__ == '__main__':
    Server.main()
