import os
import pickle


def main_loop():
    tasks = load_tasks()
    sort_list(tasks)
    while True:
        print('===[Main Menu]===')
        print('1. View Taskboard')
        print('2. Add Task')
        print('3. Edit Task')
        print('4. Delete Task')
        print('5. Update status')
        print('6. Quit')
        user_input = int(input())
        if user_input == 1:
            index = 1
            for task in tasks:
                print('Task '+str(index)+'\n'+task[0]+'\nStatus: '+task[1]+'\nDescription:\n'+task[2])
                index += 1
                print('[Enter] to view next')
                next = input()
                if len(next) > 0:
                    break
        elif user_input == 2:
            print('What is the name of th task?')
            name = input()
            print('Current status?')
            status = input()
            print('Describe the task.')
            description = input()
            tasks.append([name, status, description])
            print('Added '+name+' to the task board.')
        elif user_input == 3:
            question = 'Which task do you want to edit?'
            selection = taskboard(tasks, question)
            print('New task name? Press enter to skip.')
            name = input()
            if len(name) > 0:
                tasks[selection-1][0] = name
            print('New Description? Press enter to skip.')
            description = input()
            if len(description) > 0:
                tasks[int(selection)-1][2] = description
        elif user_input == 4:
            question = 'Which would you like to delete'
            selection = taskboard(tasks, question)
            tasks.pop(int(selection)-1)
        elif user_input == 5:
            question = 'Which task do you want to change the status?'
            selection = taskboard(tasks, question)
            print('What is the new status?')
            tasks[int(selection)-1][1] = input()
        elif user_input == 6:
            break
        save_tasks(tasks)
       
def taskboard(tasklist, prompt):
    print('1. Show new tasks')
    print('2. Show done tasks')
    choices = ['New', 'Done']
    user_input = int(input())
    show = choices[user_input-1]
    index = 0
    if show == 'New':
        print('===New Tasks===')
    else:
        print('===Tasks Done===')
    for task in tasklist:
        index += 1
        if not task[1] == choices[user_input-1]:
            continue
        print('Task '+str(index)+' Name - '+task[0])
    print(prompt)
    number = input()
    return number
      
def save_tasks(tasklist):
    with open('taskboard.txt', 'wb') as fh:
       pickle.dump(tasklist, fh)
    
def load_tasks():
    myFile = open ('taskboard.txt', 'rb')
    tasklist = pickle.load(myFile)
    return tasklist

def sort_list(tasklist):
    for i in range(0, len(tasklist)):
        if tasklist[i][1] == 'Done':
            tasklist.append(tasklist[i])
            tasklist.pop(i)


main_loop()
