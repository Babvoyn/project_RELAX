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

        rep4 = Radiobutton(self,text = "Oui",variable=self.var,value = "Oui",height=3,width=20,indicatoron=0)
        rep4.grid(row = 2,column=3)
       

    def get(self):
        return self.var.get()

class Eva(Frame):
    def __init__(self, frame, top_text, left_text, right_text,command_ = None,from_ =0 , to_ =100, resolution=0.005, set_ = 50):
        super().__init__(frame)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=1)

        top_label = ttk.Label(self,font=LARGE_FONT,text=top_text,anchor=tk.CENTER)
        top_label.grid(row=0,column=0,sticky=tk.EW,columnspan=3)

        left_label = ttk.Label(self,font=BUTTON_FONT,anchor=tk.W,text=left_text)
        left_label.grid(row=1,column=0,sticky=tk.W)

        right_label = ttk.Label(self,font=BUTTON_FONT,anchor=tk.E,text=right_text)
        right_label.grid(row=1,column=2,sticky=tk.E)

        self.slider = ttk.Scale(self,from_=from_,to=to_,orient='horizontal',command=command_)
        self.slider.set(set_)
        self.slider.grid(row=2,column=0,sticky=tk.EW,columnspan=3)

    def get(self):
        return self.slider.get()
   
class StringParam(Frame):
    def __init__(self, frame, text):
        super().__init__(frame)

        label = Label(self,anchor=E,text=text,font=LARGE_FONT)
        label.pack()
        self.answer = Text(self,font=LARGE_FONT,height=4)
        self.answer.pack()

    def get(self):
        return self.answer.get('1.0','end')


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
    FullPath = "Data/Questionary/"+"RELAX"+"_sub-"+str(subj)+"_EndQuestions"+".json"
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

        for all_frame in (End_1_Frame,End_1bis_Frame,End_2_Frame,End_2bis_Frame,End_3_Frame,End_3bis_Frame,LastFrame):
            frame = all_frame(container,self)
            self.frames[all_frame] = frame
            frame.grid(row=0,column= 0, sticky = "nsew")

        self.show_frame(End_1_Frame)
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()

    def begin(self,cont):
        self.frames[cont].begin()


class End_1_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.question1 = RadiobuttonQuestion(self,text = "Nous vous avons proposé 4 sessions de relaxation,\nvous ont-elles semblées similaires ?")
        self.question1.place(relx=0.5,rely=0.5,relwidth=0.7,relheight=0.30,anchor=CENTER)

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE) 

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)

    def next_frame(self):

        if self.question1.get():
            saved_json["question_1"]=self.question1.get()
            save_json()
            if self.question1.get() == "Oui":
                self.controller.show_frame(End_2_Frame)
            if self.question1.get() == "Non":
                self.controller.show_frame(End_1bis_Frame)
        else :
             self.label_warning["text"]='Merci de repondre à la question'
            


class End_1bis_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.question1ans = StringParam(self,text="Qu'est ce qui vous a semblé différent ?\n")
        self.question1ans.place(relx=0.5,rely=0.5,relwidth=0.7,relheight=0.30,anchor=CENTER)

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE)


    def next_frame(self):
        saved_json["question_1_ans"]=self.question1ans.get()
        save_json()
        self.controller.show_frame(End_2_Frame)

            
class End_2_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.question2 = RadiobuttonQuestion(self,text = "Avez-vous noté un état corporel particulier ?")
        self.question2.place(relx=0.5,rely=0.5,relwidth=0.7,relheight=0.30,anchor=CENTER)

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE) 

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)

    def next_frame(self):

        if self.question2.get():
            saved_json["question_2"]=self.question2.get()
            save_json()
            if self.question2.get() == "Oui":
                self.controller.show_frame(End_2bis_Frame)
            if self.question2.get() == "Non":
                self.controller.show_frame(End_3_Frame)
        else :
             self.label_warning["text"]='Merci de repondre à la question'



class End_2bis_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.question2ans = StringParam(self,text="Pouvez vous le décrire ?\n")
        self.question2ans.place(relx=0.5,rely=0.5,relwidth=0.7,relheight=0.30,anchor=CENTER)

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE)


    def next_frame(self):
        saved_json["question_2_ans"]=self.question2ans.get()
        save_json()
        self.controller.show_frame(End_3_Frame)


class End_3_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.question3 = RadiobuttonQuestion(self,text = "A certain moment, les paysages sonores étaient calés sur vos signaux corporels.\n\nL'avez vous remarqué ?")
        self.question3.place(relx=0.5,rely=0.5,relwidth=0.7,relheight=0.30,anchor=CENTER)

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE) 

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)

    def next_frame(self):

        if self.question3.get():
            saved_json["question_3"]=self.question3.get()
            save_json()
            if self.question3.get() == "Oui":
                self.controller.show_frame(End_3bis_Frame)
            if self.question3.get() == "Non":
                self.controller.show_frame(LastFrame)
        else :
             self.label_warning["text"]='Merci de repondre à la question'



class End_3bis_Frame(Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.question3ans = StringParam(self,text="Qu'avez vous remarqué ?\n")
        self.question3ans.place(relx=0.5,rely=0.5,relwidth=0.7,relheight=0.30,anchor=CENTER)

        button = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.next_frame())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE)


    def next_frame(self):
        saved_json["question_3_ans"]=self.question3ans.get()
        save_json()
        self.controller.show_frame(LastFrame)


class LastFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        label = tk.Label(self,text = "Merci d'avoir répondu aux questions.\nCliquez sur Terminer pour terminer cette partie.", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.5, anchor=CENTER)

        button = tk. Button(self,text="Terminer",font=BUTTON_FONT,command = lambda :self.end())
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)

    def end(self):
        print("---------------------------\n\n"+
              "end of the END questionary\n\n"+
              "---------------------------")
        sys.exit()

        
if __name__ == "__main__":
    initialisation()        

