import socket
import getpass


HOST = '127.0.0.1'
PORT = 64000


def checking(ip, port):
    try:
        ip = ip.group() if ip else HOST
        port = int(port) if port != '' else PORT
        port = port if -1 < port < 64000 else PORT
        return ip, port
    except:
        print("Ошибка")
        return False, False


def identify():
    ip = getpass.getpass(prompt='Введите ip для подключения: ')
    port = getpass.getpass(prompt='Введите порт для подключения: ')
    ip, port = checking(ip, port)
    if ip != False or port != False:
        return ip, port
    else:
        while ip == False or port == False:
            ip = getpass.getpass(prompt='Введите ip для подключения: ')
            port = getpass.getpass(prompt='Введите порт для подключения: ')
            ip, port = checking(ip, port)
            if ip != False and port != False:
                break
    return ip, port


def send_info(sock, data):
    msg = bytearray(f'{data}\t(Длина сообщения: {len(data)})'.encode('utf-8'))
    sock.send(msg)


def receive_info(sock):
    msg = sock.recv(1024)
    if msg:
        return msg.decode('utf-8')
    else:
        return False


def connection():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # получаем данные ip, port
        flag = False
        ip, port = identify()
        tryes = 0
        try:
            while tryes < 3 and flag == False:
                if flag == False:
                    try:
                        flag = True
                        s.connect((ip, port))
                        print('Соединение установлено')
                    except:
                        tryes += 1
                        print('Пробуем установить соединение')

        except:
            print('У вас не осталось попыток')
            exit()


        try:
            while True:
                msg = s.recv(1024).decode()
                if 'check' in msg:
                    s.send(input(f'Введите пароль пользователя {msg.split()[1]}: ').encode())
                elif 'again' in msg:
                    print('Вы ввели пароль неправильно 3 раза, мы вынуждены отключить вас')
                    exit()
                elif 'login' in msg:
                    s.send(input('Введите имя: ').encode())
                elif 'password' in msg:
                    s.send(input('Введите пароль: ').encode())
                else:
                    print(msg)
                    break
            while True:
                text = str(input('Введите сообщение: '))
                if text == 'exit':
                    s.send('exit'.encode())
                    break
                send_info(s, text)
                print('Данные отправлены')
                # получаем данные от сервера и декодируем их
                data = receive_info(s)
                print('Данные получены')
                print(data)
        except:
            print('Соединение прервано')


if __name__ == '__main__':
    connection()
