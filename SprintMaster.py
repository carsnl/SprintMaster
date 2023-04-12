from msilib.schema import ComboBox
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.ttk import Combobox
import sqlite3
import re
from datetime import *
import random

MainWindow = None
TaskTab = None
SprintTab = None
TeamTab = None
SprintDisplay = None # Child frame of sprint tab for the better
memberDisplay = None # parent frame of member cards
cardStorage = [] # stores tasks as cards
newCardList = [] # card list for the 
sprintCardStorage = [] # card list for sprints
memberStorage = [] # stores members of a sprint
sprintCount = 0 # number of exisiting sprints

def main():
    
    # connect to database during start
    connect_db = sqlite3.connect('tasks.db')
    
    # create cusror
    cursor = connect_db.cursor()
        
    # create table "tasks" in same dir if it does not exist locally
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tasks
                    ([task_name], [task_description], [story_points], [priority], [status], [assigned_to], [tag], [id], [pos], [belongs])
                    ''')
          
    # attributes

    # create master window
    requiredRow = 9
    requiredCol = 6
    mainWindow = init_main_window("Sprint Master", "2000x630", requiredRow, requiredCol)
    
    # logo = PhotoImage(file = "sprintmaster.png")
    # mainWindow.iconphoto(False, logo)
    
    MainWindow = mainWindow
    
    # setup tabs
    notebook = ttk.Notebook(mainWindow)
    notebook.grid(pady = 15, sticky = N+S+E+W)

    task_tab = Frame(notebook, width = 2000, height = 630)
    team_tab = Frame(notebook, width = 2000, height = 630)
    team_tab.grid(row = 0, column = 0, sticky = N+S+E+W)

    task_tab.grid_rowconfigure(requiredRow, weight = 1)
    task_tab.grid_columnconfigure(requiredCol, weight = 1)
    
    team_tab.grid_rowconfigure(2, weight = 1)
    team_tab.grid_columnconfigure(1, weight = 1)

    global TaskTab
    global TeamTab

    TaskTab = task_tab
    TeamTab = team_tab

    # Task Board widgets
    createTaskButton = Button(task_tab, text = "Create New Task", command = createNewTaskWindow, bg = "#234d97", fg = "white")
    filterLabel = Label(task_tab ,text = "Filter: ") 
    current_tag = StringVar()
    tags = Combobox(task_tab, textvariable = current_tag)

    tags['values'] = ('ALL','UI', 'CORE', 'TESTING')
    tags['state'] = 'readonly'
    tags.current(0)
    
    filterButton = Button(task_tab, text = "Filter", bg = "#234d97", fg = "white", command = lambda: filter(tags.get()))
    
    # create spacing in grid for C1 and C6
    spaceStart = Frame(task_tab, width=50, height=50)
    spaceEnd = Frame(task_tab, width=50, height=50)
    spaceStart.grid(row = 3, column = 1, padx = 3, pady = 3, sticky = "nw")
    spaceEnd.grid(row = 3, column = 6, padx = 3, pady = 3, sticky = "ne")

    # place buttons within main window
    
    # filter uses absolute position
    filterXStart = 965 # start of X coord filter frames 
    filterYStart = 15 # start of Y coord filter frames
    
    filterLabel.place(x = filterXStart, y = filterYStart)
    tags.place(x = filterXStart + 45, y = filterYStart)
    filterButton.place(x = filterXStart + 200, y = filterYStart - 2)
    
    startRow, startCol, spanRow, spanCol = 2, 2, 1, 2 # create task button
    createTaskButton.grid(row = startRow, column = startCol, rowspan = spanRow, columnspan = spanCol, padx = 5,pady = 12, sticky = "w")

    # add tabs to the notebook
    notebook.add(task_tab, text = "Task Board")
    notebook.add(team_tab, text = "Team Board")
    
    # display all task cards
    display(cardStorage)

    # display all sprint cards
    # connect to database
    connect_db = sqlite3.connect("sprints.db")
    
    # create cusror
    cursor = connect_db.cursor()
    
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS sprints
                ([sprint_name], [start_date], [end_date], [status], [id])
                ''')
        
    # Team Board widgets
    global memberDisplay
    memberDisplay = init_team_board(TeamTab)
    
    # printing each member of a sprint
    # connect to database
    connect_db = sqlite3.connect("members.db")
    
    # create cusror
    cursor = connect_db.cursor()
    
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS members
                ([member_name], [member_email], [member_analytics])
                ''')
        
    # select all data from table    
    cursor.execute("SELECT * from members")
    members = cursor.fetchall()
    
    # [0]: member_name
    # [1]: member_email
    # [2]: member_analytics
    
    row = 1
    col = 1
    
    global memberStorage
    
    # print each card
    for member in members:
        name = (member[0])
        email = (member[1])
        analytics = (member[2])
        end = (member[2])
    
        memberCard = create_member_card(memberDisplay, name, email)
        memberCard.grid(row = row, column = col)
        memberStorage.append(memberCard)
        
        row += 1

    # Create/Connect to a database
    connect_db = sqlite3.connect('log.db')
    # Create cusror
    cursor = connect_db.cursor()

    # create table "log" in same dir if it does not exist locally
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS log
                ([member_name], [hours_logged], [times_logged])
                ''')

    # run   
    mainWindow.mainloop()

def add_member_window(root):

    # Toplevel object which will
    # be treated as a new window
    addMemberWindow = Toplevel(root)
 
    # sets the title of the
    # Toplevel widget
    addMemberWindow.title("Add Member")
 
    # sets the geometry of toplevel
    addMemberWindow.geometry("400x200")
    
    def check_valid_email(email):
        valid_email = False

        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        if re.fullmatch(email_regex, email):
            valid_email = True

        return valid_email


    def add_member(window):

        if not check_valid_email(member_email_entry.get()):

            messagebox.showerror("Email Error", "Invalid email input entered!")
            return 

        # Create/Connect to a database
        connect_db = sqlite3.connect('members.db')
        
        # Create cusror
        cursor = connect_db.cursor()

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS members
                ([member_name], [member_email], [member_analytics])
                ''')

        connect_db.execute("INSERT INTO members VALUES (:member_name, :member_email, :member_analytics)", 
                        {
                            'member_name': member_name_entry.get(),
                            'member_email': member_email_entry.get(),
                            'member_analytics': 0
                        }
                            )
        
        #Update the log database with new member

        # Create/Connect to a database
        connect_log_db = sqlite3.connect('log.db')
        # Create cusror
        cursor_log = connect_log_db.cursor()

        # create table "log" in same dir if it does not exist locally
        cursor_log.execute('''
                    CREATE TABLE IF NOT EXISTS log
                    ([member_name], [hours_logged], [times_logged])
                    ''')
        
        connect_log_db.execute("INSERT INTO log VALUES (:member_name, :hours_logged, :times_logged)", 
                {
                    'member_name': member_name_entry.get(),
                    'hours_logged': 0,
                    'times_logged': 0
                }
                    )

        # Commit changes
        connect_db.commit()
        # Close Connnection
        connect_db.close()

        # Commit changes
        connect_log_db.commit()
        # Close Connnection
        connect_log_db.close()

        # Clear input boxes
        member_name_entry.delete(0, END)
        member_email_entry.delete(0, END)
        refresh_member_cards()
        window.destroy()

    frame = Frame(addMemberWindow, width = 400, height = 200)
    frame.pack()

    member_name = Label(frame, text = "Member Name:")
    member_name.place(x = 20, y = 50)

    member_email = Label(frame, text = "Member Email:")
    member_email.place(x = 20, y = 90)

    member_name_entry = Entry(frame, width = 40)
    member_email_entry = Entry(frame, width = 40)
    member_name_entry.place(x = 110, y = 50)
    member_email_entry.place(x = 110, y = 90)

    addButton = Button(frame, text = "Add Member", bg = "#234d97", fg = "white", command = lambda: add_member(addMemberWindow))
    addButton.place(x = 200, y = 150, anchor = CENTER)


def init_team_board(root):
    ''' Initialise team board. '''
    
    # frame storing buttons at top
    buttonFrame = Frame(root, height = 20, width = 1100)
    buttonFrame.grid_rowconfigure(1, weight = 1)
    buttonFrame.grid_columnconfigure(4, weight = 1)
    buttonFrame.grid_propagate(False)
    buttonFrame.grid(row = 1, column = 2, pady = (30, 40))
    
    # left padding
    leftPadding = Frame(root, height = 5, width = 150)
    leftPadding.grid(row = 1, column = 1)  
      
    # "+"
    plusButton = Button(buttonFrame, text = "+", font = ("Arial", 12), width = 2, height = 10,
                        bg = "#234d97", fg = "white",
                        command = lambda: add_member_window(root))
    plusButton.grid(row = 1, column = 1, sticky = W)
    
    # "Add Team Member"
    addMemberButton = Button(buttonFrame, text = "Add Team Member", width = 16, height = 10, bg = "#234d97",
                             fg = "white", command = lambda: add_member_window(root))
    addMemberButton.grid(row = 1, column = 2, sticky = W)
    
    # table listing members of sprint
    memberTableFrame = Frame(root, height = 450, width = 1000)
    memberTableFrame.grid_rowconfigure(10, weight = 1)
    memberTableFrame.grid_columnconfigure(4, weight = 1)
    memberTableFrame.grid_propagate(False)
    memberTableFrame.grid(row = 2, column = 2, sticky = "")
    
    # headers for table
    nameHeader = Label(memberTableFrame, text = "NAME", font = ("Roboto", 9, "bold")
                       , width = 52, height = 2, bg = "#234d97", fg = "white",
                       highlightbackground = "black", highlightthickness = 1)
    nameHeader.grid(row = 0, column = 1, sticky = W+E)
    
    emailHeader = Label(memberTableFrame, text = "EMAIL", font = ("Roboto", 9, "bold")
                       , width = 60, height = 2, bg = "#234d97", fg = "white",
                       highlightbackground = "black", highlightthickness = 1)
    emailHeader.grid(row = 0, column = 2, sticky = W+E)
    
    deleteHeader = Label(memberTableFrame, text = "", font = ("Roboto", 9, "bold")
                       , width = 7, height = 2, bg = "#234d97", fg = "white",
                       highlightbackground = "black", highlightthickness = 1)
    deleteHeader.grid(row = 0, column = 3, sticky = W+E)
    
    return memberTableFrame

def create_member_card(root, name, email):
    ''' Creates an entry of a member in the table '''
    # turn name into string
    memberName = ""
    
    for char in name:
        memberName += str(char)
        
    # frame storing all fields of a member
    entryFrame = Frame(root, height = 2, width = 1000)
    entryFrame.grid_rowconfigure(1, weight = 1)
    entryFrame.grid_columnconfigure(4, weight = 1)
    entryFrame.grid(columnspan = 3)
    
    # member name
    nameFrame = Label(entryFrame, text = name, font = ("Roboto", 9)
                       , width = 52, height = 2, bg = "white",
                       highlightbackground = "black", highlightthickness = 1)
    nameFrame.grid(row = 1, column = 1, sticky = W+E)
    
    # member email
    emailFrame = Label(entryFrame, text = email, font = ("Roboto", 9)
                       , width = 60, height = 2, bg = "white",
                       highlightbackground = "black", highlightthickness = 1)
    emailFrame.grid(row = 1, column = 2, sticky = W+E)
    
    # delete
    deleteFrame = Label(entryFrame, width = 7, height = 2, bg = "white",
                       highlightbackground = "black", highlightthickness = 1)
    deleteFrame.grid(row = 1, column = 3, sticky = W+E)
    
    deleteButton = Button(deleteFrame, width = 3, height = 1, text = "X", font = ("Arial", 8, "bold"),
                          bg = "red", fg = "white", command = lambda: remove_member())
    deleteButton.place(x=7, y=3)
    
    def remove_member():
        ''' Nested method that removes a member '''
        connection = sqlite3.connect("members.db")
        cursor = connection.cursor()

        query = ''' DELETE from members where member_name = ?'''
        cursor.execute(query, (memberName,))
        connection.commit()

        ''' Nested method that removes a member '''
        connection = sqlite3.connect("log.db")
        cursor = connection.cursor()

        query = ''' DELETE from log where member_name = ?'''
        cursor.execute(query, (memberName,))
        connection.commit()


        refresh_member_cards()
    
    return entryFrame

def createNewTaskWindow():

    def createTask(window):

        # Create/Connect to a database
        connect_db = sqlite3.connect('tasks.db')
        # Create cusror
        cursor = connect_db.cursor()
        
        # create table "tasks" in same dir if it does not exist locally
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS tasks
                       ([task_name], [task_description], [story_points], [priority], [status], [assigned_to], [tag], [id])
                       ''')
        
        # determine current max ID, so new task can be assigned a unique ID
        cursor.execute("SELECT MAX(id) FROM tasks")
        resultMax = cursor.fetchone()
        if resultMax[0] is None:
            currentTaskNumber = 1 # table empty
        else:
            currentTaskNumber = resultMax[0] + 1
        
        # input data
        connect_db.execute("INSERT INTO tasks VALUES (:task_name, :task_description, :story_points, :priority, :status, :assigned_to, :tag, :id, :pos, :belongs)", 
                        {
                            'task_name': entry1.get(),
                            'task_description': entry2.get(),
                            'story_points': entry3.get(),
                            'priority': priority.get(),
                            'status': status.get(),
                            'assigned_to': assigned_to.get(),
                            'tag': tag.get(),
                            'id': currentTaskNumber,
                            'pos': 1,
                            'belongs': 0
                        }
                       
                            )
        
        # show card immediately after task creation
        create_task_card(cardStorage, currentTaskNumber, 
                         entry1.get(), entry2.get(), priority.get(), entry3.get(), status.get(),assigned_to.get(), tag.get())
        
        # update to show new card
        place_card(cardStorage)
        
        # Commit changes
        connect_db.commit()
        # Close Connnection
        connect_db.close()

        # Clear input boxes
        entry1.delete(0, END)
        entry2.delete(0, END)
        entry3.delete(0, END)
        priority.set('')
        status.set('')
        assigned_to.set('')
        tag.set('')

        window.destroy()

    # Toplevel object which will
    # be treated as a new window
    newTaskWindow = Toplevel(MainWindow)
 
    # sets the title of the
    # Toplevel widget
    newTaskWindow.title("New Task")
 
    # sets the geometry of toplevel
    newTaskWindow.geometry("500x500")


    frame = Frame(newTaskWindow, width = 400, height = 400)
    frame.pack()

    task_name = Label(frame, text = "Task Name:")
    task_name.place(x = 20, y = 50)

    task_description = Label(frame, text = "Task Description:")
    task_description.place(x = 20, y = 80)

    task_story_points = Label(frame, text = "Story Points:")
    task_story_points.place(x = 20, y = 110)

    task_priority = Label(frame, text = "Priority:")
    task_priority.place(x = 20, y = 140)

    task_status = Label(frame, text = "Status:")
    task_status.place(x = 20, y = 170)

    task_assigned_to = Label(frame, text = "Assigned To:")
    task_assigned_to.place(x = 20, y = 200)

    task_tag = Label(frame, text = "Tag:")
    task_tag.place(x = 20, y = 230)


    entry1 = Entry(frame, width = 50)
    entry2 = Entry(frame, width = 50)
    entry3 = Entry(frame, width = 50)
    entry1.place(x = 140, y = 50)
    entry2.place(x = 140, y = 80)
    entry3.place(x = 140, y = 110)

    current_priority = StringVar()
    priority = Combobox(frame, textvariable = current_priority)
    priority['values'] = ('Low', 'Medium', 'High', 'Critical')
    priority['state'] = 'readonly'
    priority.current(0)
    priority.place(x = 140, y = 140)

    current_Status = StringVar()
    status = Combobox(frame, textvariable = current_Status)
    status['values'] = ('Not Started', 'In Progress', 'Complete')
    status['state'] = 'readonly'
    status.current(0)
    status.place(x = 140, y = 170)

    connect_db = sqlite3.connect("members.db")
    # create cusror
    cursor = connect_db.cursor()
    # select all data from table    
    cursor.execute("SELECT * from members")
    members = cursor.fetchall()
    # [0]: member_name
    # [1]: member_email
    # [2]: member_analytics
    member_name_list = [] # list of member names
    for member in members:
        member_name_list.append(member[0])

    current_assigned_to = StringVar()
    assigned_to = Combobox(frame, textvariable = current_assigned_to)

    if len(member_name_list) > 0:
        member_name_list.insert(0, "Everyone")
        assigned_to['values'] = tuple(member_name_list)
    else:
        assigned_to['values'] = ('Everyone')
    assigned_to['state'] = 'readonly'
    assigned_to.current(0)
    assigned_to.place(x = 140, y = 200)

    current_tag = StringVar()
    tag = Combobox(frame, textvariable = current_tag)
    tag['values'] = ('UI', 'CORE', 'TESTING')
    tag['state'] = 'readonly'
    tag.current(0)
    tag.place(x = 140, y = 230)

    createButton = Button(frame, text = "Create", bg = "#234d97", fg = "white",
                          command = lambda: createTask(newTaskWindow))
    createButton.place(x = 125, y = 350)

    discardButton = Button(frame, text = "Close", bg = "#234d97", fg = "white",
                           command = newTaskWindow.destroy)
    discardButton.place(x = 225, y = 350)
    
# initialise main window layout
def init_main_window(title, size, splitRow, splitCol):
    main = new_page(title,size)
    # breakdown window into cells in a grid (splitRow x splitCol)
    main.grid_rowconfigure(splitRow, weight = 1)
    main.grid_columnconfigure(splitCol, weight = 1)
    return main

# new page (window)
def new_page(title, size):
    newPage = Tk()
    newPage.title(title)
    newPage.geometry(size)
    return newPage
    
# add label and position it
def add_label(displayText):
    newLabel = Label(MainWindow, text = displayText, bd = 5, padx = 3, pady = 3)
    return newLabel

# create card to represent a task in display
def create_task_card(cardStorage, taskNumber, 
                     DescName, DescDesc, DescPriority, DescPoints, DescStatus, DescAssign, DescTag):
    global TaskTab
    # main frame for card
    mainFrame = Frame(TaskTab, width=280, height=200, highlightbackground="gray", highlightthickness=2, bg="white")
    # card split into 9Rx8C; cells evenly sized
    for i in range(1, 8): #R1-R8
        mainFrame.grid_rowconfigure(i, weight=1, uniform = "cardrows")
    for i in range(2, 9-1): #C2-C8
        mainFrame.grid_columnconfigure(i, weight = 1, uniform = "cardcolumns")
    mainFrame.grid_propagate(0) # stop auto resize
    
    # print fields and buttons for card
    cardNum = Label(mainFrame, text = "Task ", font=("Arial", 10, "bold"), bg="white")
    cardEditTask = Button(mainFrame, text = "Edit", font=("Courier", 8), command = lambda: editTask(taskNumber))
    cardDelete = Button(mainFrame, text = "X", font=("Arial", 8, "bold"), bg = "#FF0000", fg = "#FFFFFF", command = lambda: delete(mainFrame, taskNumber))
    cardDescName = Label(mainFrame, text = "Name: ", font=("Arial" ,8, "bold"), bg="white")
    cardDescPriority = Label(mainFrame, text = "Priority: ", font=("Arial" ,8, "bold"), bg="white")
    cardDescPoints = Label(mainFrame, text = "Story Points: ", font=("Arial" ,8, "bold"), bg="white")
    cardDescTag = Label(mainFrame, text = "Tag: ", font=("Arial" ,8, "bold"), bg="white")
    
    # print variable data from database
    variableCardNum = Label(mainFrame, text = taskNumber, font=("Arial" , 10, "bold"), bg="white")        
    variableDescName = Label(mainFrame, text = DescName, bg="white")
    variableDescPriority = Label(mainFrame, text = DescPriority, bg="white")
    if DescPriority == "Low":
        variableDescPriority.config(fg = "#18d900", font=("Arial" , 9, "bold"))
    elif DescPriority == "Medium":
        variableDescPriority.config(fg = "#ffce00", font=("Arial" , 9, "bold"))
    elif DescPriority == "High":
        variableDescPriority.config(fg = "#f36b00", font=("Arial" , 9, "bold"))
    elif DescPriority == "Critical":
        variableDescPriority.config(fg = "#f40400", font=("Arial" , 9, "bold"))
    variableDescPoints = Label(mainFrame, text = DescPoints, bg="white")
    variableDescTag = Label(mainFrame, text = DescTag, bg="white")
    
    # position of fields and buttons within card
    frontSpace = Label(mainFrame, width=200, height=1, bg = "gray") # coloured status bar
    if DescStatus == "Not Started":
        frontSpace.config(fg = "#000000", bg = "#DD8300", text = "Not started")
    elif DescStatus == "In Progress":
        frontSpace.config(fg = "#000000", bg = "#FFD800", text = "In Progress")
    elif DescStatus == "Complete":
        frontSpace.config(fg = "#000000", bg = "#3AFF00", text = "Complete")
    frontSpace.grid(row = 2, column = 1, columnspan = 8, padx = 3, pady = 1)
    
    # priority box
    if DescPriority == "Critical":
        priorityBox = Label(mainFrame, width=2, height=1, bg = "gray", highlightbackground="black", highlightthickness=1) # coloured 
        priorityBox.config(text = "!", font=("Arial" , 9, "bold"),
                           fg = "#FF0000", bg = "#FFFFFF", highlightbackground="red", highlightthickness=1)
        priorityBox.grid(row = 1, column = 6, padx = 3, pady = 3)
    
    cardNum.grid(row = 1, column = 2, columnspan = 1, padx = 2, pady = 2, sticky = "w")
    cardEditTask.grid(row = 1, column = 7, padx = 2, pady = 2, sticky = "e")
    cardDelete.grid(row = 1, column = 8, padx = 2, pady = 2, sticky = "w")
    cardDescName.grid(row = 3, column = 2, columnspan = 2, padx = 2, pady = 2, sticky = "w")
    cardDescPriority.grid(row = 4, column = 2, columnspan = 2, padx = 2, pady = 2, sticky = "w")
    cardDescPoints.grid(row = 5, column = 2, columnspan = 2, padx = 2, pady = 2, sticky = "w")
    cardDescTag.grid(row = 6, column = 2, columnspan = 2, padx = 2, pady = 2, sticky = "w")
    
    # position of variables within card
    variableCardNum.grid(row = 1, column = 3, columnspan = 1, padx = 2, pady = 2, sticky = "w")
    variableDescName.grid(row = 3, column = 4, columnspan = 4, padx = 2, pady = 2, sticky = "w")
    variableDescPriority.grid(row = 4, column = 4, columnspan = 4, padx = 2, pady = 2, sticky = "w")
    variableDescPoints.grid(row = 5, column = 4, columnspan = 4, padx = 2, pady = 2, sticky = "w")
    variableDescTag.grid(row = 6, column = 4, columnspan = 4, padx = 2, pady = 2, sticky = "w")
    
    # add card to array
    cardStorage.append(mainFrame)
    
# place cards in grid
def place_card(cardStorage):
    currentRow = 4 # first card at R4, C2
    currentCol = 2
    for card in range(0,len(cardStorage)):
        # add column-wise first, then add row if insufficient space ([arbitrary]Rx4C)
        if currentCol == 6:
            currentCol = 2
            currentRow += 1
        cardStorage[card].grid(row = currentRow, column = currentCol, padx = 5, pady = 5, sticky = "s")
        currentCol += 1
        
def display(cardArray):
    # connect to database
    connect_db = sqlite3.connect("tasks.db")
    
    # create cusror
    cursor = connect_db.cursor()
        
    # select all data from table    
    cursor.execute("SELECT * from tasks")
    rows = cursor.fetchall()
    
    # [0]: task_name
    # [1]: task description
    # [2]: story_points
    # [3]: priority
    # [4]: status
    # [5]: assigned_to
    # [6]: tag
    # [7]: id

    for row in rows:
        DescName, DescDesc, DescPriority, DescPoints, DescStatus, DescAssign, DescTag, taskNumber = row[0], row[1], row[3], row[2], row[4], row[5], row[6], row[7]
        create_task_card(cardArray, taskNumber, DescName, 
                         DescDesc, DescPriority, DescPoints, DescStatus, DescAssign, DescTag)
    
    # display if cardArray not empty
    if cardArray:
        place_card(cardArray)
        
    connect_db.commit
    connect_db.close()

def editTask(taskNumber):
    #create a new window
    newWindow = Toplevel(MainWindow)
    newWindow.geometry("300x300")
    newWindow.title("edit task")
    
    #connect to database
    sqliteConnection = sqlite3.connect('tasks.db')
    #connect to cursor
    cursor = sqliteConnection.cursor()

    #Select a single row from SQLite table
    sqlite_select_query = """SELECT * from tasks where id = ?"""
    cursor.execute(sqlite_select_query, (taskNumber,))
    record = cursor.fetchone()

    #assign all variable to StringVar()
    DescName = StringVar()
    DescDesc = StringVar()
    DescPoints = StringVar()
    DescPriority = StringVar()
    DescStatus = StringVar()
    DescAssign = StringVar()
    DescTag = StringVar()

    #put data into variable
    DescName.set(record[0])
    DescDesc.set(record[1])
    DescPoints.set(record[2])
    DescPriority.set(record[3])
    DescStatus.set(record[4])
    DescAssign.set(record[5])
    DescTag.set(record[6])

    #making label
    editName = Label(newWindow, text = "Name")
    editDesc = Label(newWindow, text = "Description")
    editPoints = Label(newWindow, text = "Story Point")
    editPriority = Label(newWindow, text = "Priority")
    editStatus = Label(newWindow, text = "Status")
    editAssign = Label(newWindow, text = "Assigned To")
    editTag = Label(newWindow, text = "Tag")

    editName.grid(row = 1, column = 0, sticky = "w", pady = 2)
    editDesc.grid(row = 2, column = 0, sticky = "w", pady = 2)
    editPoints.grid(row = 3, column = 0, sticky = "w", pady = 2)
    editPriority.grid(row = 4, column = 0, sticky = "w", pady = 2)
    editStatus.grid(row = 5, column = 0, sticky = "w", pady = 2)
    editAssign.grid(row = 6, column = 0, sticky = "w", pady = 2)
    editTag.grid(row = 7, column = 0, sticky = "w", pady = 2)

    entry1 = Entry(newWindow,  textvariable = DescName)
    entry2 = Entry(newWindow,  textvariable = DescDesc)
    entry3 = Entry(newWindow,  textvariable = DescPoints)
    entry4 = Combobox(newWindow,  textvariable = DescPriority)
    entry5 = Combobox(newWindow,  textvariable = DescStatus)
    entry6 = Combobox(newWindow,  textvariable = DescAssign)
    entry7 = Combobox(newWindow,  textvariable = DescTag)
    
    entry1.grid(row = 1, column = 1, pady=5, sticky = "w")
    entry2.grid(row = 2, column = 1, pady=5, sticky = "w")
    entry3.grid(row = 3, column = 1, pady=5, sticky = "w")
    entry4.grid(row = 4, column = 1, pady=5, sticky = "w")
    entry5.grid(row = 5, column = 1, pady=5, sticky = "w")
    entry6.grid(row = 6, column = 1, pady=5, sticky = "w")
    entry7.grid(row = 7, column = 1, pady=5, sticky = "w")
    
    # connect to database
    connect_db = sqlite3.connect("members.db")
    connect_db.row_factory = lambda cursor, row: row[0]
    cursor = connect_db.cursor()
        
    # select all data from table    
    cursor.execute("SELECT member_name FROM members")
    memberNames = cursor.fetchall()
    
    # determine team members
    memberList = tuple(memberNames)
    print(memberList)

    entry4['values'] = ('Low', 'Medium', 'High', 'Critical')
    entry5['values'] = ('Not Started', 'In Progress', 'Complete')
    entry6['values'] = memberList
    entry7['values'] = ('UI', 'CORE', 'TESTING')
    
    entry4['state'] = 'readonly'
    entry5['state'] = 'readonly'
    entry6['state'] = 'readonly'
    entry7['state'] = 'readonly'


    def update():
        #connect to database
        sqliteConnection = sqlite3.connect('tasks.db')
        #connect to cursor
        cursor = sqliteConnection.cursor()

        #update the selected row
        sql_update_query = "Update tasks set task_name = ?, task_description = ?, story_points = ?, priority = ?, status = ?, assigned_to = ?, tag = ? where id = ?"
        data = (str(entry1.get()), str(entry2.get()), int(entry3.get()), str(entry4.get()), str(entry5.get()), str(entry6.get()), str(entry7.get()), int(taskNumber))
        cursor.execute(sql_update_query, data)
        sqliteConnection.commit()
        cursor.close()
        sqliteConnection.close()

        newWindow.destroy()
        global cardStorage
        for card in cardStorage:
            card.destroy()
        cardStorage = []
        display(cardStorage)

    
    editButton = Button(newWindow, text = "Confirm", command = update)
    editButton.grid(row = 8, column = 2, pady=5, sticky = "w")

    editButton = Button(newWindow, text = "Delete", command = lambda: delete(newWindow, taskNumber))
    editButton.grid(row = 8, column = 1, pady=5, sticky = "w")

    cursor.close()
    sqliteConnection.close()


def delete(mainFrame, taskNumber):
    #delete card
    mainFrame.destroy()

    #connect database
    sqliteConnection = sqlite3.connect('tasks.db')
    #connect cursor
    cursor = sqliteConnection.cursor()

    #delete selected row
    sql_update_query = """DELETE from tasks where id = ?"""
    cursor.execute(sql_update_query, (taskNumber,))
    sqliteConnection.commit()
    cursor.close()
    sqliteConnection.close()

    global cardStorage
    for card in cardStorage:
        card.destroy()
    cardStorage = []
    display(cardStorage)

def filter(tag):
    global cardStorage
    global newCardList
    if tag == 'ALL':
        for card in cardStorage:
            card.destroy()
        for card in newCardList:
            card.destroy()
        cardStorage = []
        display(cardStorage) 
        return

    for card in cardStorage:
        card.destroy()
    for card in newCardList:
        card.destroy()
    newCardList = []
    displayFilter(newCardList, tag)

def displayFilter(cardArray, tag):
    # connect to database
    connect_db = sqlite3.connect("tasks.db")
    
    # create cusror
    cursor = connect_db.cursor()
        
    # select all data from table according to the tag
    
    sql_filter_query = """SELECT * from tasks where tag = ?"""   
    cursor.execute(sql_filter_query, (tag,))
    rows = cursor.fetchall()
    
    # [0]: task_name
    # [1]: task description
    # [2]: story_points
    # [3]: priority
    # [4]: status
    # [5]: assigned_to
    # [6]: tag
    # [7]: id

    for row in rows:
        DescName, DescDesc, DescPriority, DescPoints, DescStatus, DescAssign, DescTag, taskNumber = row[0], row[1], row[3], row[2], row[4], row[5], row[6], row[7]
        create_task_card(cardArray, taskNumber, DescName, 
                         DescDesc, DescPriority, DescPoints, DescStatus, DescAssign, DescTag)
    
    # display if cardArray not empty
    if cardArray:
        place_card(cardArray)
        
    connect_db.commit
    connect_db.close()
   #('ALL','UI', 'CORE', 'TESTING') 

def refresh_task_cards():
    """ Refresh all the task cards once changes are made to the database"""
    global cardStorage
    for card in cardStorage:
        card.destroy()
    cardStorage = []
    display(cardStorage)
        
def refresh_member_cards():
    """ Refresh all the sprint cards once changes are made to the database"""
    global memberStorage
    global memberDisplay
    
    for member in memberStorage:
        member.destroy()

    # connect to database
    connect_db = sqlite3.connect("members.db")
    
    # create cusror
    cursor = connect_db.cursor()
    
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS members
                ([member_name], [member_email], [member_analytics])
                ''')
        
    # select all data from table    
    cursor.execute("SELECT * from members")
    members = cursor.fetchall()
    
    # [0]: member_name
    # [1]: member_email
    # [2]: member_analytics
    
    row = 1
    col = 1
    
    # print each card
    for member in members:
        name = (member[0])
        email = (member[1])
        analytics = (member[2])
        end = (member[2])
    
        memberCard = create_member_card(memberDisplay, name, email)
        memberCard.grid(row = row, column = col)
        memberStorage.append(memberCard)
        
        row += 1
            
def check_analytics(root, name):
    """ Plots a graph of hours logged against time (previous 7 days) """
    # covert name to string for title
    strName = ""
    for char in name:
        strName += char
    
    # get dates (x-axis)
    duration = 7 # previous 7 days
    x = []
    for i in range(0, duration):
        x.append((datetime.today() - timedelta(days=i)).strftime('%d-%m-%Y'))
    
    # hours logged (y-axis)
    y = []
    for i in range(duration):
        y.append(random.randrange(1,12))
        
    # tkinter window that will house plot
    plotWindow = Toplevel(root)
    
    figure = Figure(figsize = (5, 5), dpi = 100) # figure that contains plot
    plot1 = figure.add_subplot(111) # occupy all subplots
    
    barChart = plot1.bar(x, y, color = "#00DDD3", width = 0.4) # plot bar chart
    plot1.bar_label(barChart, label_type='edge') # label y bars
    plot1.set_xticklabels(x, rotation=45, fontsize=8) # rotate x tick labels
    figure.tight_layout(rect=[0.04, 0.04, 0.95, 0.95]) # fit to window, [west ,south ,east ,north]
    
    # plot labels
    plot1.set_xlabel("Day")
    plot1.set_ylabel("Hours logged")
    plot1.set_title(f"{strName}'s Analytics")
    
    # place chart in canvas
    canvas = FigureCanvasTkAgg(figure, master = plotWindow)  
    canvas.draw()
    canvas.get_tk_widget().pack(side = TOP, fill = 'both', expand = True)
    
def create_log_card(root, name, hours):
    ''' Creates an entry of a member in the table '''
    # turn name into string
    memberName = ""
    
    for char in name:
        memberName += str(char)
        
    # frame storing all fields of a member
    entryFrame = Frame(root, height = 2, width = 1000)
    entryFrame.grid_rowconfigure(1, weight = 1)
    entryFrame.grid_columnconfigure(2, weight = 1)
    entryFrame.grid(columnspan = 4)
    
    # member name
    nameFrame = Label(entryFrame, text = name, font = ("Roboto", 9)
                       , width = 45, height = 2, bg = "white",
                       highlightbackground = "black", highlightthickness = 1)
    nameFrame.grid(row = 1, column = 1, sticky = W+E)
    
    # member hours
    hoursFrame = Label(entryFrame, text = hours, font = ("Roboto", 9)
                       , width = 45, height = 2, bg = "white",
                       highlightbackground = "black", highlightthickness = 1)
    hoursFrame.grid(row = 1, column = 2, sticky = W+E)
    
    return entryFrame

def get_results(root):
    tableFrame = Frame(root, bg = "red", width = 300, height = 300)
    tableFrame.grid(row = 4, column = 1)
    
    tableFrame.grid_columnconfigure(2, weight = 1)
    tableFrame.grid_rowconfigure(10, weight = 1)
    
    nameLabel = Label(tableFrame, text = "Member Name", bg = "#647687", fg = "white",
                      font = ("Roboto", 9, "bold"), width = 45, height = 2,
                      highlightbackground="black", highlightthickness=1)
    nameLabel.grid(row = 1, column = 1, sticky = W+E)
    
    hoursLabel = Label(tableFrame, text = "Average Time (Hours)", bg = "#647687", fg = "white",
                       font = ("Roboto", 9, "bold"), width = 45, height = 2,
                       highlightbackground="black", highlightthickness=1)
    hoursLabel.grid(row = 1, column = 2, sticky = W+E)
    
    # Create/Connect to a database
    connect_db = sqlite3.connect('log.db')
    # Create cusror
    cursor = connect_db.cursor()

    # create table "log" in same dir if it does not exist locally
    logs = cursor.execute('''
                SELECT * from log
                ''')
    
    hasData = False
    
    row = 2
    col = 1
    for log in logs:
        hasData = True
        # [0], [1], [2] = [member_name], [hours_logged], [times_logged]
        memberName = log[0]
        if log[1] == 0 or log[2] == 0:
            avgHours = 0
        else:
            avgHours = log[1]/log[2]
        logCard = create_log_card(tableFrame, memberName, avgHours)
        logCard.grid(row = row, column = col, columnspan = 2,
                     sticky = N)
        
        row += 1
        
    if not hasData:
        noLogs = Label(tableFrame, text = "No data to display.", width = 45, height = 2,
                    highlightbackground="black", highlightthickness=1, bg = "white")
        noLogs.grid(row = 2, column = 1, columnspan = 2, sticky=W+E)
    
main()
