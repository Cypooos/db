import sqlite3
import tkinter as tk
import os.path
from tkinter.constants import TRUE
import tkinter.filedialog as fd
import shutil
from typing import Collection
from tkinter import simpledialog
from tkinter import messagebox


class App():
    def __init__(self):
        self.file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.db") # get absolute path to database
        self.root = tk.Tk()
        self.connexion = sqlite3.connect(self.file_path)
        self.create_menu()
        self.reload_window()
        self.root.mainloop()

    def file_open(self):
        self.file_path = fd.askopenfilename(filetypes=[("Contact database","*.db"),("All","*.*")])
        self.connexion = sqlite3.connect(self.file_path)
        print("FILE::OPEN")
        self.reload_window()
    
    def file_new_file(self):
        if messagebox.askyesno("sauvegarder","Voulez-vous sauvegarder avant ?"):self.file_save()
        file_ = fd.asksaveasfile(filetypes=[("Contact database","*.db"),("All","*.*")],defaultextension=[("Contact database","*.db"),("All","*.*")])
        self.file_path = file_.name
        file_.close()
        self.connexion = sqlite3.connect(self.file_path)
        self.connexion.execute("""CREATE TABLE "repertoire" (
	"id"	INTEGER NOT NULL UNIQUE,
	"nom"	TEXT,
	"prenom"	TEXT,
	"numero"	TEXT NOT NULL UNIQUE,
	"adresse"	TEXT UNIQUE,
	"mail"	TEXT UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
)""")
        self.connexion.commit()
        self.reload_window()
        
    def file_save(self):
        self.connexion.commit()
        print("Saved !")
        self.reload_window()
    
    def file_save_as(self):
        print("PAS ENCORE FAIS")
        self.reload_window()

    def file_quit(self):
        if messagebox.askyesno("sauvegarder","Voulez-vous sauvegarder avant ?"):self.file_save()
        self.root.destroy()

    def get_all_widgets (self):
        _list = self.root.winfo_children()
        for item in _list :
            if item.winfo_children() :_list.extend(item.winfo_children())
        return _list
    
    def reload_window(self):
        
        for x in range(30):
            self.root.grid_rowconfigure(x, weight=1)
            self.root.grid_columnconfigure(x, weight=1)

        self.root.config(bg="#C0C0C0")
        widget_list = self.get_all_widgets()
        for item in widget_list:item.pack_forget()

        res = self.connexion.execute("SELECT * FROM repertoire")
        for y,tuple in enumerate(res):
            for x,element in enumerate(tuple):
                
                color = "#C0C0C0"
                tk.Label(self.root, text=str(element),background=color,width=len(str(element))).grid(row=y, column=x,sticky='ns')
                
    def no_co(self):
        try:
            if self.connexion == None: messagebox.showwarning("Warning","Vous n'avez pas de fichier ouvert !");return True
            return False
        except:
            return messagebox.showwarning("Warning","Vous n'avez pas de fichier ouvert !");return True


    def ctc_add(self):
        if self.no_co():return
        num = simpledialog.askstring("Numero", "Le numero du contact :\n(Cancel pour annuler)",parent=self.root)
        if num == None: return
        name = simpledialog.askstring("Nom", "Le nom du contact :\n(Cancel pour rien)",parent=self.root)
        prenom = simpledialog.askstring("Prenom", "Le prenom du contact :\n(Cancel pour rien)",parent=self.root)
        adr = simpledialog.askstring("Adresse", "L'addresse du contact :\n(Cancel pour rien)",parent=self.root)
        mail = simpledialog.askstring("Mail", "Le mail du contact :\n(Cancel pour rien)",parent=self.root)

        self.connexion.execute("INSERT INTO repertoire (FirstName,LastName) VALUES()")
        
        


    def create_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=lambda: self.file_open())
        filemenu.add_command(label="new", command=lambda: self.file_new_file())
        filemenu.add_command(label="Save", command=lambda: self.file_save())
        #filemenu.add_command(label="Save as...", command=lambda: self.file_save_as())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=lambda: self.file_quit())
        menubar.add_cascade(label="Fichier",menu=filemenu)

        contactsmenu = tk.Menu(menubar, tearoff=0)
        contactsmenu.add_command(label="Add", command=lambda: self.ctc_add())
        contactsmenu.add_command(label="Modify", command=lambda: self.ctc_modify())
        contactsmenu.add_command(label="Delete", command=lambda: self.ctc_delete())
        contactsmenu.add_command(label="Search", command=lambda: self.ctc_search())
        contactsmenu.add_separator()
        contactsmenu.add_command(label="SQL", command=lambda: self.ctc_sql())
        menubar.add_cascade(label="Contacts",menu=contactsmenu)
        
        self.root.config(menu=menubar)

    def create_widgets(self):
        pass

    def say_hi(self):
        print("hi there, everyone!")


a = App()