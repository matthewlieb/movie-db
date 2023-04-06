from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import sys
import os
import data

#Absolute path to resource
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#Create table function
def createTables(tableName):
    c.execute("CREATE TABLE if not exists " + str(tableName) + """ (
        id text,
        movie_title text, 
        movie_director text,
        movie_year text
        )
    """)

#Check if database tables are empty function
def emptyTable(table):
    count = c.execute("SELECT count(*) FROM " + str(table))
    count = c.fetchone()
    intCount = count[0]
    if intCount > 0:
        return False
    return True

def fillTables(dataset, table):
    # Use the executemany() method to insert multiple records into the database at once
    c.executemany("INSERT INTO " + str(table) + " VALUES (?, ?, ?, ?)", dataset)

#Function to fill tree with records
def fillTree(records, tree):
    count = 0
    for record in records:
        if count % 2 == 0:
            tree.insert(parent='', index='end', iid=count, text='', values=(record[0], record[2], record[3], record[4]), tags=('evenrow', ))
        else:
            tree.insert(parent='', index='end', iid=count, text='', values=(record[0], record[2], record[3], record[4]), tags=('oddrow', ))
        count += 1

#Function to query the database
def query_database():
    # Delete data in treeviews
    my_tree2.delete(*my_tree2.get_children())

    # Perform a query using the with statement to manage the connection and cursor
    with sqlite3.connect(resource_path(target_dir + "\\movie.db")) as conn:
        c = conn.cursor()

        c.execute("SELECT rowid, * FROM movies ORDER BY movie_title")
        
        # Fetch and process the result set one row at a time
        records2 = []
        record = c.fetchone()
        while record is not None:
            records2.append(record)
            record = c.fetchone()

        # Fill trees with records
        fillTree(records2, my_tree2)

#Create a search function
def search():
    # Store search variables
    movie_title_search = movie_title.get()
    abbr_search = abbr.get()

    # Clear the treeviews
    my_tree2.delete(*my_tree2.get_children())

    # Perform a query using the with statement to manage the connection and cursor
    with sqlite3.connect(resource_path(target_dir + "\\movie.db")) as conn:  
        c = conn.cursor()
        
        # Perform a movie_title search
        if abbr_search == "":
            movie_title.select_range(0, END)
            # Perform an exact search
            if status.get() == "Exact Search":
                # Use a parameterized query with a tuple
                params = (movie_title_search,)
                c.execute("SELECT rowid, * FROM movies WHERE movie_title LIKE ?", params)
                records2 = []
                record2 = c.fetchone()
                while record2 is not None:
                    records2.append(record2)
                    record2 = c.fetchone()
            # Perform a partial search
            else:
                # Use a parameterized query with a tuple
                params = (f"%{movie_title_search}%",)

                c.execute("SELECT rowid, * FROM movies WHERE movie_title LIKE ?", params)
                records2 = []
                record2 = c.fetchone()
                while record2 is not None:
                    records2.append(record2)
                    record2 = c.fetchone()

        # Perform an abbreviation search
        elif movie_title_search == "":
            abbr.select_range(0, END)
            # Perform an exact search
            if status.get() == "Exact Search":
                # Use a parameterized query with a tuple
                params = (abbr_search,)

                c.execute("SELECT rowid, * FROM movies WHERE movie_director LIKE ? OR movie_year LIKE ?", params * 2)
                records2 = []
                record2 = c.fetchone()
                while record2 is not None:
                    records2.append(record2)
                    record2 = c.fetchone()
            # Perform a partial search
            else:
                # Use a parameterized query with a tuple
                params = (f"%{abbr_search}%",)
                c.execute("SELECT rowid, * FROM movies WHERE movie_director LIKE ? OR movie_year LIKE ?", params * 2)
                records2 = []
                record2 = c.fetchone()
                while record2 is not None:
                    records2.append(record2)
                    record2 = c.fetchone()

        # Fill the treeviews with the records

        fillTree(records2, my_tree2)

#Focus in on movie_title
def movie_title_focus(event):
   abbr.delete(0, END)
   
#Focus in on abbr
def abbr_focus(event):
    movie_title.delete(0, END)
   
#Clear entry boxes
def clear_entry():
    id_entry.delete(0, END)
    text_entry.delete(0, END)
    abbr_entry.delete(0, END)
    txtabbr_entry.delete(0, END)

""" #Select record
def select_record(e):
    clear_entry()
    #Grab record number
    selected = my_tree.focus()
    for item in my_tree2.selection():
        my_tree2.selection_remove(item)

    #Grab record values
    values = my_tree.item(selected, 'values')

    #output to entry boxes
    id_entry.insert(0, values[0])
    text_entry.insert(0, values[1])
    abbr_entry.insert(0, values[2])
    txtabbr_entry.insert(0, values[3])

    """

def select_record2(e):
    clear_entry()

    #Grab record number
    selected = my_tree2.focus()

    #Grab record values
    values = my_tree2.item(selected, 'values')

    #output to entry boxes
    id_entry.insert(0, values[0])
    text_entry.insert(0, values[1])
    abbr_entry.insert(0, values[2])
    txtabbr_entry.insert(0, values[3]) 

#Delete a record from the database
def remove_record():
    x = my_tree2.selection()[0]

    #yes/no message box
    res=messagebox.askquestion('Delete', 'Are you sure you want to delete the selected record from the Movies table?')
    if res == 'yes' :
        pass
    else :
        return
    
    my_tree2.delete(x)
    
    # Perform a query using the with statement to manage the connection and cursor
    with sqlite3.connect(resource_path(target_dir + "\\movie.db")) as conn:
        c = conn.cursor()
   
        c.execute("DELETE from movies WHERE oid=" + id_entry.get())

    clear_entry()

    query_database()

# Update the database
def update_record():
    # Demovie_titleine which table to update based on the treeview that has focus
    if my_tree2.focus():
        table = "movies"
        treeview = my_tree2
        result = messagebox.askyesno("Confirm", "Are you sure you want to update the Movies table?")
        if not result:
            return

    # Grab the selected record
    selected = treeview.focus()
    
    # Update the record in the treeview
    treeview.item(selected,  text='', values=(id_entry.get(), text_entry.get(), abbr_entry.get(), txtabbr_entry.get()))

    # Perform a query using the with statement to manage the connection and cursor
    with sqlite3.connect(resource_path(target_dir + "\\movie.db")) as conn:
        c = conn.cursor()
        
        # Update the record in the appropriate table
        c.execute(f"UPDATE {table} SET movie_title = :movie_title, movie_director = :movie_director, movie_year = :movie_year WHERE oid = :oid",
            {
                'movie_title' : text_entry.get(),
                'movie_director' : abbr_entry.get(),
                'movie_year' : txtabbr_entry.get(),
                'oid' : id_entry.get(),
            })

#Add new record to database
def add_record():
    # Grab record number
    selected = my_tree2.focus()

    # Update the record in the treeview
    my_tree2.item(selected,  text='', values=(id_entry.get(), text_entry.get(), abbr_entry.get(), txtabbr_entry.get()))

    # Perform a query using the with statement to manage the connection and cursor
    with sqlite3.connect(resource_path(target_dir + "\\movie.db")) as conn:
        c = conn.cursor()

        # Insert multiple records using the executemany() method
        records = [(id_entry.get(), text_entry.get(), abbr_entry.get(), txtabbr_entry.get())]
        c.executemany("INSERT INTO movies VALUES (?, ?, ?, ?)", records)

    #Clear entry boxes
    clear_entry()

    #Clear and refresh data
    query_database()

#On enter
def hitEnter(event):
    search()

#Create popup menu with instructions for tool
popup = None
def open_about():
    global popup
    if not popup:
        popup = Toplevel()
        popup.title("About Menu")
        instructions = """
        -------------------------
        MoviesDB Tool:
        -------------------------
        *This movie lookup tool is for any movies you've enjoyed. 
        *The tool allows for searching, adding, deleting, and updating movies. 
        *The tool contains three sections, the Search section, the Treeviews, and the Record section.
        *The Search section of the tool is where movies can be searched using an exact search in which the movie title or movie director must match exactly 
         (not case sensitive), or a similar search which will show partial matches. 
        *The Treeviews display the Movies table and any search results. 
        *The Record section contains the controls to add, delete, and update the Movies table. 
        *Entries in the Movies table can be updated by selecting an entry in the Treeview, modifying it in the bottom text entry, and pressing the update button. 
        *Entries in the Movies table can be added, updated, or deleted.
        -------------------------
        Controls:
        -------------------------
        Title -- Use this text entry to enter a movie title to search for
        Director -- Use this text entry to enter a director to search for
        Exact Search -- Use this radio button to choose an exact search to perform for a movie title or director
        Similar Search -- Use this radio button to choose a partial search to peform for a movie title or director 
        Search -- Press 'enter' or press this button to perform a search
        Reset -- Use this button to reset the Movies tables, displaying all results
        Add -- Use this button to add entries to the Movies table
        Update -- Use this button to update selected entries in the Movies table
        Clear -- Use this button to clear the bottom movie title, direcotor, and year entry boxes
        Delete -- Use this button to delete selected entries in the Movies table"""
        instructions = '\n'.join([line.lstrip() for line in instructions.splitlines()])
        instructions_widget = Text(popup, height=30, width=60, wrap='word')
        instructions_widget.insert('1.0', instructions)
        instructions_widget.config(state='disabled')
        scrollbar = Scrollbar(popup, orient='vertical', command=instructions_widget.yview)
        instructions_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        instructions_widget.pack(side='left', fill='both', expand=True)
        popup.protocol("WM_DELETE_WINDOW", close_about)

#Close the about menu
def close_about():
    global popup
    popup.destroy()
    popup = None
    root.focus_set()
    root.grab_set()

#Set the path to sharepoint
drive_path = "C:\\Users\\" + os.getlogin() + "\\AppData\\Local\\MovieLookup"
#drive_path = resource_path("V:\DEPT24\Abbreviation Lookup")
#drive_path = "C:\\Users\\" + "liebmd" + "\\Leidos-LeidosCorpUS\\Engineering Group - Shared Documents\\Abbreviation Tool"

# Set the target directory to the desktop
target_dir = drive_path

# Create the directory if it doesn't exist
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

#Setup icon file
datafile = "logo.ico"
if not hasattr(sys, "frozen"):
    datafile = os.path.join(os.path.dirname(__file__), datafile)
else:
    datafile = os.path.join(sys.prefix, datafile)

# Perform a query using the with statement to manage the connection and cursor
with sqlite3.connect(resource_path(target_dir + "\\movie.db")) as conn:
    c = conn.cursor()
    #Create tables
    createTables("movies")

    #Fill tables with data if they are empty
    if emptyTable("movies"):
        fillTables(data.data2, "movies")

#Setup window
root = Tk()
root.title('MovieDB Version 1.0')
root.iconbitmap(default=resource_path(datafile))
root.geometry("620x630") #Width x height

my_menu = Menu(root)
root.config(menu=my_menu)

#Create a menu item
help_menu = Menu(my_menu, tearoff=0)
my_menu.add_command(label = "About", command=open_about)

#Add a frame for search functions
search_frame = LabelFrame(root, text="Search", padx=5, pady=5)
search_frame.pack(fill="x", expand="yes", padx=20)

#Create radioboxes to select the search mode
MODES = [
    ("Exact Search", "Exact Search"),
    ("Similar Search", "Similar Search")
]

status = StringVar()
status.set("Exact Search")

i = 2
j = 0
for text, mode in MODES:
    Radiobutton(search_frame, text=text, variable=status, value=mode).grid(row=i, column=j)
    j += 1

#Create text boxes for movie_title search and abbreviation search
movie_title = Entry(search_frame, width=30)
movie_title.grid(row=0, column=1, padx=30, pady=5)
abbr = Entry(search_frame, width=30)
abbr.grid(row=1, column=1, padx=30, pady=5)

#Create labels for text box search
movie_title_label = Label(search_frame, text="Movie Title:")
movie_title_label.grid(row=0, column=0)
abbr_label = Label(search_frame, text="Director:")
abbr_label.grid(row=1, column=0)

movie_title.bind("<FocusIn>", movie_title_focus)
abbr.bind("<FocusIn>", abbr_focus)

#Create a search button to query for records
submit_btn = Button (search_frame, text="Search", command=search)
submit_btn.grid(row=2, column=3, columnspan=2, pady=5, padx=10, ipadx=10)

#Create a search button to query for records
reset_btn = Button (search_frame, text="Reset", command=query_database)
reset_btn.grid(row=2, column=5, columnspan=2, pady=5, padx=10, ipadx=15)

#Add treeview style
style = ttk.Style()

#Pick a theme
style.theme_use('default')

#Configure treeview colors
style.configure("Treeview",
background="#D3D3D3",
foreground="black",
rowheight=25,
fieldbackground="#D3D3D3")

#Change selected color
style.map('Treeview', 
background=[('selected', "#347083")])

#Create a treeview frame
tree_frame2 = Frame(root)
tree_frame2.pack(pady=10)

#Create a treeview scrollbar
tree_scroll2 = Scrollbar(tree_frame2)
tree_scroll2.pack(side=RIGHT, fill=Y)

#Create the treeview
my_tree2 = ttk.Treeview(tree_frame2, yscrollcommand=tree_scroll2.set, selectmode=EXTENDED, height=10)
my_tree2.pack()

#Configure the scrollbar
tree_scroll2.config(command=my_tree2.yview)

#Define our treeview columns
my_tree2['columns'] = ("ID", "Movie Title", "Director", "Year")

#Format treeview columns
my_tree2.column('#0', width=0, stretch=NO)
my_tree2.column('ID', width=0, stretch=NO)
my_tree2.column('Movie Title', width=300, anchor=W)
my_tree2.column('Director', width=120, anchor=CENTER)
my_tree2.column('Year', width=120, anchor=CENTER)

#Define treeview headings
my_tree2.heading('#0', text="", anchor=W)
my_tree2.heading('ID', text="", anchor=W)
my_tree2.heading('Movie Title', text="Movie Title", anchor=W)
my_tree2.heading('Director', text="Director", anchor=CENTER)
my_tree2.heading('Year', text="Year", anchor=CENTER)

#Create striped rows
my_tree2.tag_configure('oddrow', background='white')
my_tree2.tag_configure('evenrow', background='lightblue')

#Add record entry boxes
data_frame = LabelFrame(root, text="Record")
data_frame.pack(fill="x", expand="yes", padx=20)

#id_label = Label(data_frame, text="ID:")
#id_label.grid(row=0, column=0, padx=10, pady=5)
id_entry = Entry(data_frame)
#id_entry.grid(row=0, column=1, padx=10, pady=5)

#Add labels above treeview
text_label = Label(data_frame, text="Movie Title:")
text_label.grid(row=0, column=0, pady=5)
text_entry = Entry(data_frame)
text_entry.grid(row=0, column=1, pady=5)

abbr_label = Label(data_frame, text="Director:")
abbr_label.grid(row=1, column=0, pady=5)
abbr_entry = Entry(data_frame)
abbr_entry.grid(row=1, column=1, pady=5)

txtabbr_label = Label(data_frame, text="Year:")
txtabbr_label.grid(row=1, column=2, pady=5)
txtabbr_entry = Entry(data_frame)
txtabbr_entry.grid(row=1, column=3, pady=5)

#Add buttons
add_button = Button(data_frame, text="Add", command=add_record)
add_button.grid(row=2, column=0, padx=25, pady=10, ipadx=25)

remove_button = Button(data_frame, text="Delete", command=remove_record)
remove_button.grid(row=2, column=1, padx=25, pady=10, ipadx=15)

clear_button = Button(data_frame, text="Clear", command=clear_entry)
clear_button.grid(row=2, column=2, padx=25, pady=10, ipadx=20)

update_button = Button(data_frame, text="Update", command=update_record)
update_button.grid(row=2, column=3, padx=25, pady=10, ipadx=15)

# Bind the treeview to a button release
my_tree2.bind("<ButtonRelease-1>", select_record2)

if abbr_focus or movie_title_focus:
    root.bind("<Return>", hitEnter)

#Run to pull data from database on start
query_database()

root.mainloop()

# To turn code into an exe run the folliwng in a shell:
#  pyinstaller --onefile --clean --icon=logo.ico --add-data "data.py;." --add-data "logo.ico;." -w ‘Abbreviation Lookup.py’