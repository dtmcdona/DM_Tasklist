import os
import pickle
import socket
import struct
import datetime
import time


class Taskboard:
    def __init__(self):
        self.tasks = self.load_tasks()

    def main_loop(self):
        while True:
            self.sort_list()
            print('===[Main Menu]===')
            print('1. View Taskboard')
            print('2. Add Task')
            print('3. Edit Task')
            print('4. Delete Task')
            print('5. Update status')
            print('6. Sync Taskboard')
            print('7. Quit')
            user_input = input()
            tasks_len = len(self.tasks)
            if len(user_input) > 0:
                user_input = int(user_input)
            else:
                break
            if user_input == 1:
                for index in range(0, len(self.tasks)):
                    print('Task '+str(index+1)+'\n'+self.tasks[index][0]+'\nStatus: '+self.tasks[index][1]+'\nDescription:')
                    self.word_wrap(self.tasks[index][2], 45)
                    print('Last updated: '+self.tasks[index][3])
                    print('Task ('+str(index+1)+' of '+str(tasks_len)+')')
                    print('Press enter to continue...')
                    next = input()
                    if len(next) > 0:
                        break
            elif user_input == 2:
                print('What is the name of the task?')
                name = input()
                print('Current status?')
                status = input()
                print('Describe the task.')
                description = input()
                task_datetime = datetime.datetime.now()
                task_updated = task_datetime.strftime("%x")
                self.tasks.append([name, status, description, task_updated])
                print('Added '+name+' to the task board.')
            elif user_input == 3:
                question = 'Which task do you want to edit?'
                selection = self.show_taskboard(question)
                print('New task name? Press enter to skip.')
                name = input()
                if len(name) > 0:
                    self.tasks[int(selection)-1][0] = name
                print('New Description? Press enter to skip.')
                description = input()
                if len(description) > 0:
                    self.tasks[int(selection)-1][2] = description
                    if self.tasks[int(selection)-1][2] == description or self.tasks[selection-1][0] == name:
                        task_datetime = datetime.datetime.now()
                        task_updated = task_datetime.strftime("%x")
                        self.tasks[int(selection) - 1][3] = task_updated
            elif user_input == 4:
                question = 'Which would you like to delete? Press enter to skip.'
                selection = self.show_taskboard(question)
                if len(selection) > 0 and int(selection)-1 < len(self.tasks):
                    self.tasks.pop(int(selection)-1)
            elif user_input == 5:
                question = 'Which task do you want to change the status? Press enter to skip.'
                selection = self.show_taskboard(question)
                if len(selection) > 0:
                    print('What is the new status? Press enter to skip.')
                    user_input = input()
                    if len(user_input) > 0:
                        self.tasks[int(selection)-1][1] = user_input
                        task_datetime = datetime.datetime.now()
                        task_updated = task_datetime.strftime("%x")
                        self.tasks[int(selection) - 1][3] = task_updated
            elif user_input == 6:
                print('Do you want to (u)pload or (d)ownload the tasklist?')
                user_input = input()
                if user_input == 'u' or user_input == 'upload':
                    self.sync_taskboard(True)
                if user_input == 'd' or user_input == 'download':
                    self.sync_taskboard(False)
                print('Sync complete!')
            elif user_input == 7:
                break
            self.save_tasks()

    def sync_taskboard(self, is_server):
        if is_server:
            # Initiate server connection
            print("Creating server socket...")
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            host_name = socket.gethostname()
            print('What ip address do you want to use?')
            user_input = input()
            if user_input.count('.') == 3:
                host_ip = user_input
            else:
                host_ip = '127.0.0.1'
            print('What port do you want to use?')
            user_input = input()
            if len(user_input) == 4:
                port = int(user_input)
            else:
                port = 8080
            socket_address = (host_ip, port)
            server_socket.bind(socket_address)
            server_socket.listen(5)
            print("Server:", socket_address)
            running = True
            while running:
                client_socket, addr = server_socket.accept()
                print('Syncing tasklist with:', addr)
                if client_socket:
                    client_connected = True
                    while client_connected:
                        pickled_tasks = pickle.dumps(self.tasks)
                        network_packet = struct.pack("Q", len(pickled_tasks)) + pickled_tasks
                        client_socket.sendall(network_packet)
                        running = False
                        client_connected = False
                        client_socket.close()
        else:
            # Client
            # Initiate server connection
            print('Connecting to server...')
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print('What ip address do you want to connect to?')
            user_input = input()
            if user_input.count('.') == 3:
                host_ip = user_input
            else:
                host_ip = '127.0.0.1'
            print('What port do you want to use?')
            user_input = input()
            if len(user_input) == 4:
                port = int(user_input)
            else:
                port = 8080
            client_socket.connect((host_ip, port))
            print('Connected!')
            data = b""
            payload_size = struct.calcsize("Q")
            running = True
            previous_tasks = self.tasks
            while running:
                while len(data) < payload_size:
                    packet = client_socket.recv(4*256)
                    if not packet:
                        break
                    data += packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]
                while len(data) < msg_size:
                    data += client_socket.recv(1024)
                tasks_data = data[:msg_size]
                data = data[msg_size:]
                tasklist_unpicked = pickle.loads(tasks_data)
                for task in tasklist_unpicked:
                    if task not in self.tasks:
                        self.tasks.append(task)
                running = False
                client_socket.close()

    def word_wrap(self, mystr, maxlen):
        mystr_arr = mystr.split(' ')
        arr_len = len(mystr_arr)
        printstr = ''
        for index in range(0, arr_len):
            if len(printstr +' '+ mystr_arr[index]) < maxlen:
                printstr = printstr +' '+ mystr_arr[index]
            else:
                print(printstr)
                printstr = mystr_arr[index]
        print(printstr)


    def show_taskboard(self, prompt):
        print('1. Show new tasks')
        print('2. Show done tasks')
        print('3. Show all tasks')
        choices = ['New', 'Done', 'All']
        shown_done = False
        user_input = int(input())
        show = choices[user_input-1]
        index = 0
        if show == 'New' or show == 'All':
            print('===New Tasks===')
        tasks_len = len(self.tasks)
        for index in range(0, tasks_len):
            if not choices[user_input-1] == 'All':
                if not self.tasks[index][1] == choices[user_input-1]:
                    continue
            if self.tasks[index][1] == 'Done' and not shown_done:
                print('===Tasks Done===')
                shown_done = True
            print('Task '+str(index+1)+' Name - '+str(self.tasks[index]))
        print(prompt)
        number = input()
        return number

    def save_tasks(self):
        with open('taskboard.txt', 'wb') as fh:
           pickle.dump(self.tasks, fh)

    def load_tasks(self):
        myFile = open ('taskboard.txt', 'rb')
        tasklist = pickle.load(myFile)
        return tasklist

    def new_tasklist(self):
        task_datetime = datetime.datetime.now()
        task_updated = task_datetime.strftime("%x")
        self.tasks = [['Make taskboard', 'Done', 'Make a new taskboard', str(task_updated)]]

    def sort_list(self):
        for i in range(0, len(self.tasks)):
            if self.tasks[i][1] == 'Done':
                self.tasks.append(self.tasks[i])
                self.tasks.pop(i)


myTaskboard = Taskboard()
# myTaskboard.new_tasklist()
myTaskboard.main_loop()
