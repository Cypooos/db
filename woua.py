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
        self.file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.db") # le chemin absolu vers la database de base
        self.root = tk.Tk()
        self.connexion = sqlite3.connect(self.file_path) # on ce connecte
        self.frame = tk.Frame(self.root)
        self.frame.pack(side="top", expand=True, fill="both")
        self.frame.config(bg="#C0C0C0") # couleur de fond
        self.root.config(bg="#C0C0C0") # couleur de fond
        self.create_menu() 
        self.reload_window()
        self.root.minsize(300, 100) # taille minimum


        # lance la mainloop
        self.root.mainloop()

    def file_open(self):

        fl = fd.askopenfilename(filetypes=[("Contact database","*.db"),("All","*.*")]) # on demande des fichier .db
        if fl == "":return # si "cancel"

        self.file_path = fl
        self.connexion = sqlite3.connect(self.file_path) # on ce connecte
        print("FILE::OPEN")
        self.reload_window() # on re-fresh la fenetre
    
    def file_new_file(self):
        
        file_ = fd.asksaveasfilename(title="Nouveau",filetypes=[("Contact database","*.db"),("All","*.*")],defaultextension=[("Contact database","*.db"),("All","*.*")]) # on demande des fichier .db
        if file_ == "":return # si "cancel"

        self.file_path = file_
        self.connexion = sqlite3.connect(self.file_path) # on ce connecte
        self.connexion.execute("""CREATE TABLE "repertoire" (
	"id"	INTEGER NOT NULL UNIQUE,
	"nom"	TEXT,
	"prenom"	TEXT,
	"numero"	TEXT NOT NULL UNIQUE,
	"adresse"	TEXT,
	"mail"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)""") # création de la table
        self.connexion.commit()
        self.reload_window()# on re-fresh la fenetre
        
    def file_save(self): # tout action comme ajouter un contact appelle cette fonction
        self.connexion.commit()
        print("Saved !")
        self.reload_window()# on re-fresh la fenetre

    def file_quit(self):
        self.root.destroy() # fin du programme

    def get_all_widgets(self):
        _list = self.root.winfo_children() # code de stackOverFlow : on récupère les enfant, et pour chaque enfant on rajoute à la liste ces enfants etc...
        for item in _list :
            if item.winfo_children() :_list.extend(item.winfo_children())
        return _list
    
    def reload_window(self):
        

        
        # destroy all widgets from frame
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        self.frame.pack_forget()
        self.frame.destroy()
        self.frame = None
        self.frame = tk.Frame(self.root)
        self.frame.config(bg="#C0C0C0") # couleur de fond

        
        # layout de grille
        for x in range(6):self.frame.grid_columnconfigure(x, weight=1)
        for y in range(30):self.frame.grid_rowconfigure(x, weight=1)
        
        color = "#C0C0C0"

        for x, label in enumerate(["ID","Nom","Prenom","Numéro","Adresse","Mail"]):
            tk.Label(self.frame, text=str(label),background=color,fg="#f542c5",width=len(str(label))).grid(row=0, column=x,sticky='ns')

        try:

            res = self.connexion.execute("SELECT * FROM repertoire")
            for y,tuple in enumerate(res):
                for x,element in enumerate(tuple):
                    
                    tk.Label(self.frame, text=str(element),background=color,width=len(str(element))).grid(row=y+1, column=x,sticky='ns')
            self.frame.pack(side="top", expand=True, fill="both")
            self.root.minsize(300, 100) # taille minimum
        except sqlite3.OperationalError: # si il y a une erreur. Je ne considère que l'erreur de "base sans table 'répertoire'"", mais on peut rajouetr d'autres handler ici
            messagebox.showwarning("Warning","La base n'as pas de table répertoire.\nOn vas la créé !")
            self.connexion = sqlite3.connect(self.file_path)
            self.connexion.execute("""CREATE TABLE "repertoire" (
	"id"	INTEGER NOT NULL UNIQUE,
	"nom"	TEXT,
	"prenom"	TEXT,
	"numero"	TEXT NOT NULL UNIQUE,
	"adresse"	TEXT,
	"mail"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)""")
            self.file_save()
            self.reload_window() # Woua fonction recursive owo
        
            
                
    def no_co(self):
        # vérifie si il y a une connexion à un fichier
        try:
            if self.connexion == None: messagebox.showwarning("Warning","Vous n'avez pas de fichier ouvert !");return True
            return False
        except:
            messagebox.showwarning("Warning","Vous n'avez pas de fichier ouvert !");return True


    def ctc_add(self):
        if self.no_co():return # si pas de fichier, return 
        num = simpledialog.askstring("Numero", "Le numero du contact :\n(Cancel pour annuler)",parent=self.root) # on demande le numéro
        if num == None: return
        nom = simpledialog.askstring("Nom", "Le nom du contact :\n(Cancel pour rien)",parent=self.root)
        prenom = simpledialog.askstring("Prenom", "Le prenom du contact :\n(Cancel pour rien)",parent=self.root)
        adr = simpledialog.askstring("Adresse", "L'addresse du contact :\n(Cancel pour rien)",parent=self.root)
        mail = simpledialog.askstring("Mail", "Le mail du contact :\n(Cancel pour rien)",parent=self.root)
        for x in [num,nom,prenom,adr,mail]:
            if self.check_sqlinject(x):return
        req = "INSERT INTO repertoire (numero,nom,prenom,adresse,mail) VALUES('{numero}','{name}','{prenom}','{adresse}','{mail}')".format(
            numero=str(num),
            name=str(nom),
            prenom=str(prenom),
            adresse=str(adr),
            mail=str(mail)
            ) # on format tout 

        self.connexion.execute(req) # on ajoute et sauvegarde
        self.file_save()
    
    
    def ctc_change_by_num(self):
        if self.no_co():return # si pas de fichier, return 
        numero = simpledialog.askstring("Numero", "Le numero du contact à modifier :\n(Cancel pour annuler)",parent=self.root) # on demande le numéro
        
        if numero == None or numero == "": return # si "cancel"
        if self.check_sqlinject(numero): return
        
        # check qu'il existe
        data = self.connexion.execute("select numero from repertoire where numero='{numero}'".format(numero=numero)).fetchall()
        print(data,str(data))
        if len(data) == 0:messagebox.showwarning("Warning","Numero inconnu");return

        ch = self.ask_champ("à modifier")
        if ch == False:return
        if ch == None:messagebox.showwarning("Warning","Champ inconnu");return
        if self.check_sqlinject(ch): return
        val = simpledialog.askstring("Valeur", "la nouvelle valeure :\n(Cancel pour annuler)",parent=self.root) # on demande la valeure
        if val == None or val == "": return # si "cancel"
        if self.check_sqlinject(val): return

        try:
            self.connexion.execute("UPDATE repertoire SET {ch} = '{val}' WHERE numero='{numero}'".format(ch=ch,val=val,numero=numero))
            self.connexion.commit()
        except Exception as e:
            messagebox.showerror("Erreur dans votre requete","ERREUR:\n"+str(e))
        self.file_save()
    
    
    def ctc_change_by_id(self):
        if self.no_co():return # si pas de fichier, return 
        ID = simpledialog.askstring("ID", "L'ID du contact à modifier :\n(Cancel pour annuler)",parent=self.root) # on demande le numéro
        
        if ID == None or ID == "": return # si "cancel"
        if self.check_sqlinject(ID): return
        
        # check qu'il existe
        data = self.connexion.execute("select id from repertoire where id='{ID}'".format(ID=ID)).fetchall()
        if len(data) == 0:messagebox.showwarning("Warning","Numero inconnu");return

        ch = self.ask_champ("à modifier")
        if ch == False:return
        if ch == None:messagebox.showwarning("Warning","Champ inconnu");return
        if self.check_sqlinject(ch): return
        val = simpledialog.askstring("Valeur", "la nouvelle valeure :\n(Cancel pour annuler)",parent=self.root) # on demande la valeure
        if val == None or val == "": return # si "cancel"
        if self.check_sqlinject(val): return

        try:
            self.connexion.execute("UPDATE repertoire SET {ch} = '{val}' WHERE id='{ID}'".format(ch=ch,val=val,ID=ID))
            self.connexion.commit()
        except Exception as e:
            messagebox.showerror("Erreur dans votre requete","ERREUR:\n"+str(e))
        self.file_save()

        

    def ctc_search(self):
        if self.no_co():return # si pas de fichier, return 
        ch = self.ask_champ("sur lequel rechercher")
        if ch == False:return
        if ch == None:messagebox.showwarning("Warning","Champ inconnu");return

        
        val = simpledialog.askstring("Valeur", "La valeur (rechercher via LIKE) :\n(Cancel pour annuler)",parent=self.root) # on demande la valeure
        if val == None or val == "": return # si "cancel"
        if self.check_sqlinject(val): return

        try:
            ret = self.connexion.execute("SELECT * FROM repertoire WHERE {ch} LIKE '{val}'".format(ch=ch,val=val))
            messagebox.showinfo("Résultat","Retour de la recherche :\n"+"\n".join(",".join([str(x) for x in line]) for line in ret))
            self.connexion.commit()
        except Exception as e:
            messagebox.showerror("Erreur dans votre requete","ERREUR:\n"+str(e))



    
    def ask_champ(self,action):
        champ = simpledialog.askstring("Champ", "Le champs "+action+":\n(Parmis: 'numero,nom,id,prenom,mail,adresse')\n(Cancel pour annuler)",parent=self.root)
        if champ == None or champ == "":return False
        if champ.lower() in ["numero","nom","id","prenom","mail","adresse"]:
            return champ.lower()
        return None



    
    def ctc_sql(self):
        if self.no_co():return # si pas de fichier, return 
        str_ = simpledialog.askstring("SQL", "Le string SQL à executer:\n(Cancel pour annuler)",parent=self.root) # on demande le numéro
        if str_ == None or str_ == "": return
        try:
            ret = self.connexion.execute(str_)
            messagebox.showinfo("Résultat","Retour de la commande :\n"+"\n".join(",".join([str(x) for x in line]) for line in ret))
        except Exception as e:
            messagebox.showerror("Erreur SQL",str(e))


    def ctc_remove_num(self):
        if self.no_co():return # si pas de fichier, return 
        numero = simpledialog.askstring("Numero", "Le numero du contact à suprimmer :\n(Cancel pour annuler)",parent=self.root) # on demande le numéro
        
        if numero == None or numero == "": return # si "cancel"
        
        # check qu'il existe
        data = self.connexion.execute("select numero from repertoire where numero='{numero}'".format(numero=numero)).fetchall()
        if len(data) == 0:messagebox.showwarning("Warning","Numero inconnu");return

        # execution, car on sais qu'il existe
        self.connexion.execute("DELETE FROM repertoire WHERE numero = '{num}' ".format(num=numero))
        self.connexion.commit()
        self.file_save()

    def ctc_remove_id(self):
        if self.no_co():return # si pas de fichier, return 
        ID = simpledialog.askstring("ID", "L'ID du contact à suprimmer :\n(Cancel pour annuler)",parent=self.root) # on demande le numéro
        
        if ID == None or ID == "": return # si "cancel"
        
        # check qu'il existe
        data = self.connexion.execute("select id from repertoire where id='{id}'".format(id=ID)).fetchall()
        if len(data) == 0:messagebox.showwarning("Warning","ID inconnu");return

        # execution, car on sais qu'il existe
        self.connexion.execute("DELETE FROM repertoire WHERE id = '{id}' ".format(id=ID))
        self.connexion.commit()
        self.file_save()

    def check_sqlinject(self,str_):
        # J'AIME PAS LES SQL INJECTIONS
        banned = "'\\\",;:/=" # la liste des charactère interdits
        for x in banned:
            if x in str(str_):messagebox.showwarning("Warning","Un charactère illégal à été détécté !");return True
        return False

    def create_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Ouvrir", command=lambda: self.file_open())
        filemenu.add_command(label="Nouveau", command=lambda: self.file_new_file())
        filemenu.add_command(label="Sauvegarder", command=lambda: self.file_save())
        #filemenu.add_command(label="Save as...", command=lambda: self.file_save_as())
        filemenu.add_separator()
        filemenu.add_command(label="Quitter", command=lambda: self.file_quit())
        menubar.add_cascade(label="Fichier",menu=filemenu)

        contactsmenu = tk.Menu(menubar, tearoff=0)
        contactsmenu.add_command(label="Ajouter", command=lambda: self.ctc_add())
        contactsmenu.add_command(label="Changer par Num", command=lambda: self.ctc_change_by_num())
        contactsmenu.add_command(label="Changer par ID", command=lambda: self.ctc_change_by_id())
        contactsmenu.add_command(label="Supprimmer par Num", command=lambda: self.ctc_remove_num())
        contactsmenu.add_command(label="Supprimmer par ID", command=lambda: self.ctc_remove_id())
        contactsmenu.add_command(label="Recherche", command=lambda: self.ctc_search())
        contactsmenu.add_separator()
        contactsmenu.add_command(label="SQL", command=lambda: self.ctc_sql())
        menubar.add_cascade(label="Contacts",menu=contactsmenu)
        
        self.root.config(menu=menubar)


    def say_hi(self):
        print("hi there, everyone!")


a = App()