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

        rep1 = Radiobutton(self,text = "Non" , variable=self.var,value = "Non",height=3,width=20,indicatoron=0)
        rep1.grid(row = 2,column=0,sticky = S)
        
        rep2 = Radiobutton(self,text = "Plutôt Non",variable=self.var,value = "Plutot non",height=3,width=20,indicatoron=0)
        rep2.grid(row = 2,column=1)
        
        rep3 = Radiobutton(self,text = "Plutôt oui",variable=self.var,value= "Plutot oui",height=3,width=20,indicatoron=0)
        rep3.grid(row = 2,column=2)

        rep4 = Radiobutton(self,text = "Oui",variable=self.var,value = "Oui",height=3,width=20,indicatoron=0)
        rep4.grid(row = 2,column=3)

        

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
    FullPath = "Data/Questionary/"+"RELAX"+"_sub-"+str(subj)+"_STAIt"+".json"
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

        for all_frame in (FirstFrame,STAI_trait_1_Frame,STAI_trait_2_Frame,STAI_trait_3_Frame,STAI_trait_4_Frame,STAI_trait_5_Frame,LastFrame):
            frame = all_frame(container,self)
            self.frames[all_frame] = frame
            frame.grid(row=0,column= 0, sticky = "nsew")

        self.show_frame(FirstFrame)
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()

    def begin(self,cont):
        self.frames[cont].begin()


class FirstFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        label = tk.Label(self,text = "Un certain nombre de phrases que l'on utilise pour se décrire vont vous être présentées.\n\nLisez chaque phrase, puis sélectionnez la réponse qui correspond le mieux à ce que vous ressentez GENERALEMENT.\n\nIl n'y a pas de bonnes ou mauvaises réponses.\nNe passez pas trop de temps sur l'une ou l'autre de ces propositions\net indiquez la réponse qui décrit le mieux vos sentiments HABITUELS.", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.5, anchor=CENTER)
        
        button = tk. Button(self,text="Commencer",font=BUTTON_FONT,command = lambda : self.controller.show_frame(STAI_trait_1_Frame))
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)


class STAI_trait_1_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        for i in range(4):
                    self.rowconfigure(i,weight=1)
        
        self.columnconfigure(0,weight=1)

        self.label = Label(self,text = 'généralement :',font=LARGE_FONT)
        self.label.place(relx=0.5,rely=0.15,relwidth=0.7,relheight=0.15,anchor=CENTER)
        
        self.question1 = RadiobuttonQuestion(self,text = "Je me sens de bonne humeur, aimable.")
        self.question1.place(relx=0.5,rely=0.3,relwidth=0.7,relheight=0.15,anchor=CENTER)

        self.question2 = RadiobuttonQuestion(self,text = "Je me sens nerveux (nerveuse) et agité(e).")
        self.question2.place(relx=0.5,rely=0.45,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question3 = RadiobuttonQuestion(self,text = "Je me sens content(e) de moi.")
        self.question3.place(relx=0.5,rely=0.6,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question4 = RadiobuttonQuestion(self,text = "Je voudrais être aussi heureux (heureuse) que les autres semblent l'être.")
        self.question4.place(relx=0.5,rely=0.75,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE) 

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)

    def next_frame(self):

        if self.question1.get() and self.question2.get() and self.question3.get() and self.question4.get():
            saved_json["STAIt_1"]=self.question1.get()
            saved_json["STAIt_2"]=self.question2.get()
            saved_json["STAIt_3"]=self.question3.get()
            saved_json["STAIt_4"]=self.question4.get()
            save_json()
            self.controller.show_frame(STAI_trait_2_Frame)
        else :
             self.label_warning["text"]='Merci de repondre à toutes les questions'
            


class STAI_trait_2_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        for i in range(4):
                    self.rowconfigure(i,weight=1)
        
        self.columnconfigure(0,weight=1)

        self.label = Label(self,text = 'généralement :',font=LARGE_FONT)
        self.label.place(relx=0.5,rely=0.15,relwidth=0.7,relheight=0.15,anchor=CENTER)

        self.question1 = RadiobuttonQuestion(self,text = "J'ai un sentiment d'échec.")
        self.question1.place(relx=0.5,rely=0.3,relwidth=0.7,relheight=0.15,anchor=CENTER) 
        
        self.question2 = RadiobuttonQuestion(self,text = "Je me sens reposé(e).")
        self.question2.place(relx=0.5,rely=0.45,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question3 = RadiobuttonQuestion(self,text = "J'ai tout mon sang-froid.")
        self.question3.place(relx=0.5,rely=0.6,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question4 = RadiobuttonQuestion(self,text = "J'ai l'impression que les difficultés s'accumulent à un tel point\nque je ne peux plus les surmonter.")
        self.question4.place(relx=0.5,rely=0.78,relwidth=0.7,relheight=0.20,anchor=CENTER) 

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE)

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)

    def next_frame(self):
        if self.question1.get() and self.question2.get() and self.question3.get() and self.question4.get():
            saved_json["STAIt_5"]=self.question1.get()
            saved_json["STAIt_6"]=self.question2.get()
            saved_json["STAIt_7"]=self.question3.get()
            saved_json["STAIt_8"]=self.question4.get()
            save_json()
            self.controller.show_frame(STAI_trait_3_Frame)
        else :
            self.label_warning["text"]='Merci de repondre à toutes les questions'
            


class STAI_trait_3_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        for i in range(4):
                    self.rowconfigure(i,weight=1)
        
        self.columnconfigure(0,weight=1)

        self.label = Label(self,text = 'généralement :',font=LARGE_FONT)
        self.label.place(relx=0.5,rely=0.15,relwidth=0.7,relheight=0.15,anchor=CENTER)

        self.question1 = RadiobuttonQuestion(self,text = "Je m'inquiète à propos de choses sans importance.")
        self.question1.place(relx=0.5,rely=0.3,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question2 = RadiobuttonQuestion(self,text = "Je suis heureux(se).")
        self.question2.place(relx=0.5,rely=0.45,relwidth=0.7,relheight=0.15,anchor=CENTER) 
        
        self.question3 = RadiobuttonQuestion(self,text = "J'ai des pensées qui me perturbent.")
        self.question3.place(relx=0.5,rely=0.6,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question4 = RadiobuttonQuestion(self,text = "Je manque de confiance en moi.")
        self.question4.place(relx=0.5,rely=0.75,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE)

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)
    

    def next_frame(self):
        if self.question1.get() and self.question2.get() and self.question3.get() and self.question4.get():
            saved_json["STAIt_9"]=self.question1.get()
            saved_json["STAIt_10"]=self.question2.get()
            saved_json["STAIt_11"]=self.question3.get()
            saved_json["STAIt_12"]=self.question4.get()
            save_json()
            self.controller.show_frame(STAI_trait_4_Frame)
        else :
            self.label_warning["text"]='Merci de repondre à toutes les questions'



class STAI_trait_4_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        for i in range(4):
                    self.rowconfigure(i,weight=1)
        
        self.columnconfigure(0,weight=1)

        self.label = Label(self,text = 'généralement :',font=LARGE_FONT)
        self.label.place(relx=0.5,rely=0.15,relwidth=0.7,relheight=0.15,anchor=CENTER)
        
        self.question1 = RadiobuttonQuestion(self,text = "Je me sens sans inquiétude, en sécurité, en sûreté.")
        self.question1.place(relx=0.5,rely=0.3,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question2 = RadiobuttonQuestion(self,text = "Je prends facilement des décisions.")
        self.question2.place(relx=0.5,rely=0.45,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question3 = RadiobuttonQuestion(self,text = "Je me sens incompétent(e), pas à la hauteur.")
        self.question3.place(relx=0.5,rely=0.6,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question4 = RadiobuttonQuestion(self,text = "Je suis satisfait(e).")
        self.question4.place(relx=0.5,rely=0.75,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE)

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)

    def next_frame(self):
        if self.question1.get() and self.question2.get() and self.question3.get() and self.question4.get():
            saved_json["STAIt_13"]=self.question1.get()
            saved_json["STAIt_14"]=self.question2.get()
            saved_json["STAIt_15"]=self.question3.get()
            saved_json["STAIt_16"]=self.question4.get()
            save_json()
            self.controller.show_frame(STAI_trait_5_Frame)
        else :
             self.label_warning["text"]='Merci de repondre à toutes les questions'

class STAI_trait_5_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        for i in range(4):
                    self.rowconfigure(i,weight=1)
        
        self.columnconfigure(0,weight=1)

        self.label = Label(self,text = 'généralement :',font=LARGE_FONT)
        self.label.place(relx=0.5,rely=0.15,relwidth=0.7,relheight=0.15,anchor=CENTER)

        self.question1 = RadiobuttonQuestion(self,text = "Des idées sans importance trottant dans ma tête me dérangent.")
        self.question1.place(relx=0.5,rely=0.3,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question2 = RadiobuttonQuestion(self,text = "Je prends les déceptions tellement à coeur que je les oublie difficilement.")
        self.question2.place(relx=0.5,rely=0.45,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question3 = RadiobuttonQuestion(self,text = "Je suis une personne posée, solide, stable.")
        self.question3.place(relx=0.5,rely=0.6,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        self.question4 = RadiobuttonQuestion(self,text = "Je deviens tendu(e) et agité(e) quand je réfléchis à mes soucis.")
        self.question4.place(relx=0.5,rely=0.75,relwidth=0.7,relheight=0.15,anchor=CENTER) 

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE)

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)
    

    def next_frame(self):
        if self.question1.get() and self.question2.get() and self.question3.get() and self.question4.get():
            saved_json["STAIt_17"]=self.question1.get()
            saved_json["STAIt_18"]=self.question2.get()
            saved_json["STAIt_19"]=self.question3.get()
            saved_json["STAIt_20"]=self.question4.get()
            save_json()
            self.controller.show_frame(LastFrame)
        else :
            self.label_warning["text"]='Merci de repondre à toutes les questions'



class LastFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        label = tk.Label(self,text = "Merci d'avoir répondu aux questions.\nCliquez sur Suivant pour terminer cette partie.", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.5, anchor=CENTER)

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda :self.end())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)

    def end(self):
        print("---------------------------\n\n"+
              "end of the STAI trait questionary\n\n"+
              "---------------------------")
        sys.exit()


if __name__ == "__main__":
    initialisation()        

