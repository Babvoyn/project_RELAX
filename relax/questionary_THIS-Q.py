import tkinter as tk
from tkinter import *
from tkinter import ttk
from time import time
import json
import sys
import os
import click
from datetime import date


os.chdir("/home/manip3/Desktop/Relax")

###################### Definition of the parameters and the saving file ######################

# Font size
LARGE_FONT = ('Helvetica',25)
BUTTON_FONT = ('Helvetica',20)


# time
start_time = time()

# create the list that will contain registered data
saved_json = {}

# create the string that will contain the path for the jason file
FullPath = str


###################### Definition of the different class & function to be used in the main tkinter Frames ######################

class RadiobuttonQuestion(Frame):
    def __init__(self, frame,text):
        super().__init__(frame)

        for i in range(4):
                    self.columnconfigure(i,weight=1)
        

        label = Label(self,text=text,font=LARGE_FONT,pady=25)
        label.grid(row=0,column=0,columnspan=4)

        self.var= StringVar()

        rep1 = Radiobutton(self,text = "Jamais",variable=self.var,value = "Jamais",height=3,width=20,indicatoron=0)
        rep1.grid(row = 3,column=0,sticky = S)
        
        rep2 = Radiobutton(self,text = "Occasionnellement",variable=self.var,value = "Occasionnellement",height=3,width=20,indicatoron=0)
        rep2.grid(row = 3,column=1)
        
        rep3 = Radiobutton(self,text = "Parfois",variable=self.var,value= "Parfois",height=3,width=20,indicatoron=0)
        rep3.grid(row = 3,column=2)
        
        rep4 = Radiobutton(self,text = "Souvent",variable=self.var,value = "Souvent",height=3,width=20,indicatoron=0)
        rep4.grid(row = 3,column=3)

        rep5 = Radiobutton(self,text = "Toujours",variable=self.var,value = "Toujours",height=3,width=20,indicatoron=0)
        rep5.grid(row = 3,column=3)    

    def get(self):
        return self.var.get()

# Saving in the json file le saved_jason list
def save_json():
    json_object = json.dumps(saved_json, indent = 0)
    if not os.path.exists("Data/Questionary"):
        os.mkdir("Data/Questionary")
    with open(FullPath, "w") as outfile:
        outfile.write(json_object)


###################### Main Window and all frames of the app ######################

# Initialisation

@click.command()
@click.option("--subj", prompt="Subject id")
def initialisation(subj):

    global FullPath
    FullPath = "Data/Questionary/"+"RELAX"+"_sub-"+str(subj)+"_THISQ"+".json"
    check_file = os.path.isfile(FullPath)
    if check_file:
        raise NameError(f"{FullPath} already exist !")
    saved_json["subject_id"]=subj
    saved_json["date"]=str(date.today())
    save_json()

    global app
    app = MasterWindow()
    app.mainloop()


## Main Window
class MasterWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        #display the window full screen on the second screen
        self.wm_geometry("1080x920+2160+0")
        self.attributes('-fullscreen',True)
        self.title("RELAX")
    
        # create the frame that will fill the window and be used by all frame class
        container = tk.Frame(self)
        container.pack(fill='both',expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        # container for all the frames
        self.frames={}

        for all_frame in (FirstFrame,THISQ_1_Frame,THISQ_2_Frame,THISQ_3_Frame,THISQ_4_Frame,LastFrame):
            frame = all_frame(container,self)
            self.frames[all_frame] = frame
            frame.grid(row=0,column= 0, sticky = "nsew")

        self.show_frame(FirstFrame)
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()

    def beging(self,cont):
        self.frames[cont].beging()


class FirstFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        label = tk.Label(self,text = "Le questionnaire que nous allons vous proposer consiste en une série d'affirmations\nconcernant la perception des sensations corporelles.\n\nVeuillez indiquer, pour chacune de ces informations,\nla fréquence à laquelle l'affirmation s'applique à votre vie quotidienne.", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.5, anchor=CENTER)
        
        button = tk. Button(self,text="Commencer",font=BUTTON_FONT,command = lambda : self.controller.show_frame(THISQ_1_Frame))
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)


class THISQ_1_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        for i in range(4):
                    self.rowconfigure(i,weight=1)
        
        self.columnconfigure(0,weight=1)
        
        self.question1 = RadiobuttonQuestion(self,text = "Quand je me sens bien reposé(e), je remarque que je respire lentement.")
        self.question1.place(relx=0.5,rely=0.2,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question2 = RadiobuttonQuestion(self,text = "Avant de m'endormir, je sens que ma respiration est lente et profonde.")
        self.question2.place(relx=0.5,rely=0.35,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question3 = RadiobuttonQuestion(self,text = "Quand je me détends, je sens que ma respiration ralentit.")
        self.question3.place(relx=0.5,rely=0.49,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question4 = RadiobuttonQuestion(self,text = "Lorsque je fais un léger effort physique,\nje remarque que ma respiration est plus rapide qu'à l'habitude.")
        self.question4.place(relx=0.5,rely=0.65,relwidth=0.7,relheight=0.20,anchor=CENTER) 

        self.question5 = RadiobuttonQuestion(self,text = "Lors d'un effort physique d'intensité modérée, je sens que je respire vite et profondément.")
        self.question5.place(relx=0.5,rely=0.8,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE)

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)

    def next_frame(self):
        if self.question1.get() and self.question2.get() and self.question3.get() and self.question4.get():
            saved_json["THISQ_1"]=self.question1.get()
            saved_json["THISQ_2"]=self.question2.get()
            saved_json["THISQ_3"]=self.question3.get()
            saved_json["THISQ_4"]=self.question4.get()
            saved_json["THISQ_5"]=self.question5.get()
            save_json()
            self.controller.show_frame(THISQ_2_Frame)
        else :
             self.label_warning["text"]='Merci de repondre à toutes les questions'


class THISQ_2_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        for i in range(4):
                    self.rowconfigure(i,weight=1)
        
        self.columnconfigure(0,weight=1)
        
        self.question1 = RadiobuttonQuestion(self,text = "Je remarque quand je suis haletant(e).")
        self.question1.place(relx=0.5,rely=0.2,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question2 = RadiobuttonQuestion(self,text = "Je sens quand mon estomac se contracte.")
        self.question2.place(relx=0.5,rely=0.35,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question3 = RadiobuttonQuestion(self,text = "Je sens quand mes intestins se contractent.")
        self.question3.place(relx=0.5,rely=0.5,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question4 = RadiobuttonQuestion(self,text = "Je remarque quand les aliments se déplacent dans mes intestins.")
        self.question4.place(relx=0.5,rely=0.65,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question5 = RadiobuttonQuestion(self,text = "Lorsque j'avale de la nourriture, je sens qu'elle se déplace dans mon œsophage.")
        self.question5.place(relx=0.5,rely=0.80,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE)

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)

    def next_frame(self):
        if self.question1.get() and self.question2.get() and self.question3.get() and self.question4.get():
            saved_json["THISQ_6"]=self.question1.get()
            saved_json["THISQ_7"]=self.question2.get()
            saved_json["THISQ_8"]=self.question3.get()
            saved_json["THISQ_9"]=self.question4.get()
            saved_json["THISQ_10"]=self.question5.get()
            save_json()
            self.controller.show_frame(THISQ_3_Frame)
        else :
             self.label_warning["text"]='Merci de repondre à toutes les questions'


class THISQ_3_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        for i in range(4):
                    self.rowconfigure(i,weight=1)
        
        self.columnconfigure(0,weight=1)
        
        self.question1 = RadiobuttonQuestion(self,text = "Quand je mange ou bois quelque chose de froid,\nje sens le froid dans mon œsophage après l'avoir avalé.")
        self.question1.place(relx=0.5,rely=0.18,relwidth=0.7,relheight=0.20,anchor=CENTER) 

        self.question2 = RadiobuttonQuestion(self,text = "Quand je mange ou bois quelque chose de chaud,\nje sens la chaleur dans mon œsophage après l'avoir avalé.")
        self.question2.place(relx=0.5,rely=0.35,relwidth=0.7,relheight=0.20,anchor=CENTER) 

        self.question3 = RadiobuttonQuestion(self,text = "Lorsque je suis détendu(e), je remarque que mon rythme cardiaque est lent.")
        self.question3.place(relx=0.5,rely=0.5,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question4 = RadiobuttonQuestion(self,text = "Quand je me repose, je sens mon rythme cardiaque ralentir.")
        self.question4.place(relx=0.5,rely=0.65,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question5 = RadiobuttonQuestion(self,text = "Quand je me repose après un effort physique, je sens ma fréquence cardiaque diminuer.")
        self.question5.place(relx=0.5,rely=0.8,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE)

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)
    

    def next_frame(self):
        if self.question1.get() and self.question2.get() and self.question3.get() and self.question4.get():
            saved_json["THISQ_11"]=self.question1.get()
            saved_json["THISQ_12"]=self.question2.get()
            saved_json["THISQ_13"]=self.question3.get()
            saved_json["THISQ_14"]=self.question4.get()
            saved_json["THISQ_15"]=self.question5.get()
            save_json()
            self.controller.show_frame(THISQ_4_Frame)
        else :
             self.label_warning["text"]='Merci de repondre à toutes les questions'


class THISQ_4_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        for i in range(4):
                    self.rowconfigure(i,weight=1)
        
        self.columnconfigure(0,weight=1)
        
        self.question1 = RadiobuttonQuestion(self,text = "Lors d'un léger effort physique, je sens mon cœur battre. ")
        self.question1.place(relx=0.5,rely=0.2,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question2 = RadiobuttonQuestion(self,text = "Quand je suis actif (ve) physiquement de façon modérée,\nje sens mon cœur battre rapidement.")
        self.question2.place(relx=0.5,rely=0.38,relwidth=0.7,relheight=0.20,anchor=CENTER) 

        self.question3 = RadiobuttonQuestion(self,text = "Je remarque quand mon cœur s'emballe. ")
        self.question3.place(relx=0.5,rely=0.53,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE) 

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)

    def next_frame(self):
         
        if self.question1.get() and self.question2.get() and self.question3.get():
            saved_json["THISQ_16"]=self.question1.get()
            saved_json["THISQ_17"]=self.question2.get()
            saved_json["THISQ_18"]=self.question3.get()
            save_json()
            self.controller.show_frame(LastFrame)
        else :
            self.label_warning["text"]='Merci de repondre à toutes les questions'


class LastFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        label = tk.Label(self,text = "Merci d'avoir répondu aux questions.\nCeci signe la fin de l'expérience.\nMerci d'avoir participé.", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.5, anchor=CENTER)

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda :self.end())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)

    def end(self):
        print("---------------------------\n\n"+
              "end of the THIS Q questionary\n\n"+
              "---------------------------")
        sys.exit()

if __name__ == "__main__":
    initialisation()        

