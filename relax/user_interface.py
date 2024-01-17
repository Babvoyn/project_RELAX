import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import font
import itertools
import time
import json
import sys
import os
from pathlib import Path
sys.path.insert(0,'/home/manip3/Desktop/Relax/BalloonShooter')
from balloonShooter import launch_balloonshooter , get_score_balloonshooter
from biofeedback import Biofeedback
import numpy as np

from colorama import Fore, Back, Style

os.chdir("/home/manip3/Desktop/Relax")

###################### Definition of the parameters and the saving file ######################

# Parameters for biofeedback
cond= []
subject_id= '35'
global block
block= []
egg_pos= 1
egg_freq= 0.046

# the soundscape order is semi-random, it is selected according to the subject id in a permuation list containing all possibility
list_condition = [['ecg', 'mock', 'resp', 'egg'], ['resp', 'egg', 'mock', 'ecg'], ['egg', 'ecg', 'mock', 'resp'], ['mock', 'ecg', 'egg', 'resp'], ['mock', 'ecg', 'resp', 'egg'], ['ecg', 'resp', 'mock', 'egg'], ['mock', 'egg', 'resp', 'ecg'], ['mock', 'egg', 'ecg', 'resp'], ['resp', 'egg', 'ecg', 'mock'], ['egg', 'mock', 'ecg', 'resp'], ['mock', 'resp', 'egg', 'ecg'], ['resp', 'ecg', 'egg', 'mock'], ['resp', 'mock', 'egg', 'ecg'], ['ecg', 'egg', 'mock', 'resp'], ['egg', 'ecg', 'resp', 'mock'], ['egg', 'resp', 'mock', 'ecg'], ['ecg', 'mock', 'egg', 'resp'], ['egg', 'resp', 'ecg', 'mock'], ['ecg', 'resp', 'egg', 'mock'], ['ecg', 'egg', 'resp', 'mock'], ['egg', 'mock', 'resp', 'ecg'], ['resp', 'ecg', 'mock', 'egg'], ['resp', 'mock', 'ecg', 'egg'], ['mock', 'resp', 'ecg', 'egg']]

# Change of the first electrode from 2 to 1 to match the physical change of order between the two (to be able to see them on ActiView)
ecg_poses = [1,8]
resp_pos = 0
sampling_rate = 2048
hostname = '192.168.1.1'
port = 1972

# game score
score = 0
nb_try = 0

# Font size
LARGE_FONT = ('Helvetica',25)
BUTTON_FONT = ('Helvetica',20)


# time
start_time = time.time()

# create the list that will contain registered data
saved_json = {}

# create the string that will contain the path for the jason file
FullPath = str


###################### Definition of the different class & function to be used in the main tkinter Frames ######################
class MultiChoiceParam(Frame):
    def __init__(self, frame, text,values):
        super().__init__(frame)

        label = ttk.Label(self,text=text)
        label.grid(row = 0,column=0,padx = 5, pady = 5)
        self.answer = ttk.Combobox(self)
        self.answer['values'] = values
        self.answer['state'] = 'readonly'
        self.answer.grid(row = 0,column=1,padx = 5, pady = 5)

    def get(self):
        return self.answer.get()


class StringParam(Frame):
    def __init__(self, frame, text,default_text):
        super().__init__(frame)

        label = ttk.Label(self,anchor=E,text=text)
        label.grid(row=0,column=0,padx = 5, pady = 5)
        self.answer = Entry(self)
        self.answer.insert(END,default_text)
        self.answer.grid(row=0,column=1,padx = 5, pady = 5)

    def get(self):
        return self.answer.get()


class InfoParam(Frame):
    def __init__(self, frame, text, values):
        super().__init__(frame)

        label = ttk.Label(self,anchor=E,text=text)
        label.grid(row=0,column=0,padx = 5, pady = 5)
        value = ttk.Label(self,anchor=W,text=values)
        value.grid(row=0,column=1,padx = 5, pady = 5)


class Eva(ttk.Frame):
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

# Launch the biofeedback
def launch_block(
        cond,
        subject_id,
        block,
        egg_pos,
        egg_freq,
        ecg_poses,
        resp_pos,
        sampling_rate,
        hostname,
        port,
        master_volume
        ):
    Biofeedback(
    cond,
    subject_id,
    block,
    egg_pos,
    egg_freq,
    ecg_poses,
    resp_pos,
    sampling_rate,
    hostname,
    port,
    master_volume,
    )


# Saving in the json file le saved_jason list
def save_json():
    json_object = json.dumps(saved_json, indent = 0)
    if not os.path.exists("Data/Header"):
        os.mkdir("Data/Header")
    with open(FullPath, "w") as outfile:
        outfile.write(json_object)


###################### Main Window and all frames of the app ######################

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

        for all_frame in (FirstFrame,IntermediateFrame,GameFrame,ScoreFrame,BeforeQuestionFrame,BeforeRelaxFrame,RelaxFrame,EndRelaxFrame,AfterQuestionFrame,AfterQuestion2Frame,LastFrame):
            frame = all_frame(container,self)
            self.frames[all_frame] = frame
            frame.grid(row=0,column= 0, sticky = "nsew")

        self.show_frame(FirstFrame)
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()

    def begin(self,cont):
        self.frames[cont].begin()
    

## Additional Window only displayed for the operator. Initialise the parameters
class AdminWindow():
    def __init__(self,parent):
        # init the toplevel window dimension, place it on the left screen
        self.parent = parent
        self.top = Toplevel(parent)
        self.top.geometry('500x500')
        self.top.wm_geometry("500x500-2160+0")
        self.frame = ttk.Frame(self.top)

        self.frame.pack()
        
        # All parameters

        self.subject_id_txt = StringParam(self.top,text='subject_id',default_text=subject_id)
        self.subject_id_txt.place(relx = 0.1,rely=0.2,relwidth=0.7,relheight=0.1)

        self.block_txt = StringParam(self.top,text='block',default_text='01')
        self.block_txt.place(relx=0.1,rely=0.3,relwidth=0.7,relheight=0.1)

        self.egg_pos_txt = StringParam(self.top,text='egg_pos',default_text=egg_pos)
        self.egg_pos_txt.place(relx=0.1,rely=0.4,relwidth=0.7,relheight=0.1)

        self.egg_freq_txt = StringParam(self.top,text='egg_freq',default_text=egg_freq)
        self.egg_freq_txt.place(relx=0.1,rely=0.5,relwidth=0.7,relheight=0.1)


        ecg_poses_txt= InfoParam(self.top,text='ecg_poses : ',values = str(ecg_poses))
        ecg_poses_txt.place(relx=0.1,rely=0.7,relwidth=0.7,relheight=0.1)

        resp_pos_txt= InfoParam(self.top,text='resp_pos : ',values =resp_pos)
        resp_pos_txt.place(relx=0.1,rely=0.75,relwidth=0.7,relheight=0.1)
        
        sampling_rate_txt= InfoParam(self.top,text='sampling rate : ',values =sampling_rate)
        sampling_rate_txt.place(relx=0.1,rely=0.80,relwidth=0.7,relheight=0.1)
        
        hostname_txt= InfoParam(self.top,text='hostname : ',values =str(hostname))
        hostname_txt.place(relx=0.1,rely=0.85,relwidth=0.7,relheight=0.1)
        
        port_txt= InfoParam(self.top,text='port : ',values =port)
        port_txt.place(relx=0.1,rely=0.9,relwidth=0.7,relheight=0.1)

        
        button = Button(self.top,text = 'Confirm', command =lambda : self.initialise_block())
        button.pack(anchor=SE)

    # Sub function to initialise the block
    def initialise_block(self):

        # Retrieve the parameter and modify the global variable
        global subject_id,cond,block,egg_pos,egg_freq
        subject_id= self.subject_id_txt.get()
        block= self.block_txt.get()
        egg_pos= self.egg_pos_txt.get()
        egg_freq= self.egg_freq_txt.get()

        cond = list_condition[int(subject_id)-1-24][int(block)-1]
        print("-------------------------------------------\n\n")
        print("Condition : {}".format(cond))
        print("\n\n-------------------------------------------")

        # Check if the file for mock_modulation exist
        record_folder = "/home/manip3/Desktop/Relax/Data/RestingState/"
        list_file = os.listdir(record_folder)
        expected_file= f"RELAX_sub-{self.subject_id_txt.get()}_PremodulatedSignal.json"
        if not expected_file in list_file:
            raise FileNotFoundError(f"{expected_file} was not found.")     

        # initialise the path for the json file
        global FullPath
        FullPath = "Data/Header/"+"RELAX_sub-"+str(subject_id)+"_ses-"+str(block)+"_cond-"+str(cond)+"_header"+".json"

        check_file = os.path.isfile(FullPath)
        if check_file:
            raise NameError(f"{FullPath} already exist !")

        # save all parameters
        saved_json["subject_id"] = subject_id
        saved_json["block"] = block
        saved_json["condition"] = cond
        saved_json["egg_pos"] = egg_pos
        saved_json["egg_freq"] = egg_freq
        saved_json["egg_pos"] = egg_pos
        save_json()


        # Show next frame
        app.show_frame(IntermediateFrame)
        app.begin(IntermediateFrame)

        # Close the top level window
        self.top.withdraw()

    def show_admin(self):
        self.top.deiconify()


class FirstFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        label = tk.Label(self,text = "Veuillez patienter le temps que l'opérateur initialise l'expérience", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.5, anchor=CENTER)
        # the first frame for the participant open the toplevel window to enter all information    
        self.new_wind = AdminWindow(parent)   

    def begin(self):
        self.new_wind.show_admin()


class IntermediateFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.label = tk.Label(self,text = "", font=LARGE_FONT)
        self.label.place(relx=0.5,rely = 0.5, anchor=CENTER)

        button1 = tk. Button(self,text="Jouer",font=BUTTON_FONT,command = lambda : [controller.show_frame(GameFrame), controller.begin(GameFrame)])
        button1.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)

    def begin(self):
        self.label["text"] ="Vous allez jouer à Balloon Shooter.\n\nQuand vous êtes prêt.e, appuyer sur 'Jouer'"


class GameFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
    
    def begin(self):
        global score

        launch_balloonshooter()
        score = get_score_balloonshooter()
        saved_json["score"] = score
        save_json()

        self.controller.show_frame(ScoreFrame)
        self.controller.begin(ScoreFrame)


class ScoreFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.label = tk.Label(self,text = "", font=LARGE_FONT)
        self.label.place(relx=0.5,rely=0.5, anchor=CENTER)

        button1 = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : controller.show_frame(BeforeQuestionFrame))
        button1.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)
        

    def begin(self):
        # the label goes in the begin as the score can't be initialized
        self.label["text"]="Votre score est : {}".format(score)+"\n\n Appuyez sur 'Suivant' pour continuer."
        print("-------------------------------------------\n\n")
        print("End of the game\n")
        print("Score : {}".format(score))
        print("\n\n-------------------------------------------")


class BeforeQuestionFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        label = tk.Label(self,text = "Comment vous sentez-vous maintenant ?\n\nPrenez le temps d'utiliser ces échelles de façon honnête et précise.", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.1, anchor=CENTER)

        self.relaxation = Eva(self,"Détendu.e/relaxé.e ?","Pas du tout","Completement")
        self.relaxation.place(relx=0.2,rely=0.30,relwidth=0.6)

        self.excitation = Eva(self,"Eveillé.e/agité.e/excité.e ?","Pas du tout","Completement")
        self.excitation.place(relx=0.2,rely=0.50,relwidth=0.6)

        self.restoration = Eva(self,"Ressourcé.e/apaisé.e/reposé.e?","Pas du tout","Completement")
        self.restoration.place(relx=0.2,rely=0.70,relwidth=0.6)

        self.next_button = tk.Button(self,text='Suivant',font=BUTTON_FONT,command=lambda : self.stop())
        self.next_button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE) 

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)

    def stop(self):
        if self.relaxation.get()!=50.00 and self.relaxation.get()!=50.00 and self.restoration.get()!=50.00:
            saved_json["before_excitation"]=self.excitation.get()
            saved_json["before_relaxation"]=self.relaxation.get()
            saved_json["before_restoration"]=self.restoration.get()
            save_json()
            print("-------------------------------------------\n\n")
            print(self.excitation.get(),self.relaxation.get(),self.restoration.get())
            print("End of the questions before relaxation")
            print("\n\n-------------------------------------------")
            self.controller.show_frame(BeforeRelaxFrame)
        else :
            self.label_warning["text"]='Merci de repondre à toutes les questions'
        

class BeforeRelaxFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.label = tk.Label(self,text = "Nous allons pouvoir débuter la session de relaxation.\n\nUne fois que vous aurez cliqué sur 'Débuter', il vous sera demandé de fermer les yeux et de vous relaxer.\nL'ambiance sonore commencera après plusieurs dizaines de secondes.\n\nLa session dure environ 10 minutes.\n\nUne fois le son terminé, réouvrez les yeux et suivez les instructions.", font=LARGE_FONT)
        self.label.place(relx=0.5,rely=0.5, anchor=CENTER)

        button1 = tk. Button(self,text="Débuter",font=BUTTON_FONT,command = lambda : [self.controller.show_frame(RelaxFrame) ,self.controller.begin(RelaxFrame)])
        button1.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)
        

class RelaxFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.label = tk.Label(self,text = "La session de relaxation a commencé.\n\nFermez les yeux et relaxez vous.\n\nL'ambiance sonore ne commencera qu'après quelque dizaines de seconde.\n\nLorsque le son s'arrête, vous pouvez réouvrir les yeux,\nmais ne bougez pas jusqu'à ce que la prochaine fenêtre apparaisse.", font=LARGE_FONT)
        self.label.place(relx=0.5,rely = 0.5, anchor=CENTER)

    def begin(self):
        record_folder = "/home/manip3/Desktop/Relax/Data/Header/"
        file_list = os.listdir(record_folder)
        expected_file = f"RELAX_sub-{subject_id}_header.json"

        if expected_file in file_list:
            with open(record_folder+expected_file,"r") as file:
                master_header= json.load(file)
                master_volume = master_header["volume"]
        else:
            # If the file is not found, print an error message and exit.
            raise FileNotFoundError(f"{expected_file} was not found.")

        launch_block(cond,
                    subject_id,
                    block,
                    egg_pos,
                    egg_freq,
                    ecg_poses,
                    resp_pos,
                    sampling_rate,
                    hostname,
                    port,
                    master_volume,
                    )

        self.controller.show_frame(EndRelaxFrame)
        self.controller.begin(EndRelaxFrame)


class EndRelaxFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        label = tk.Label(self,text = "La session de relaxation est terminée.\n\n Merci de ne pas bouger jusqu'à ce que la prochaine fenêtre apparaisse.", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.5, anchor=CENTER)


    def begin(self):
        print("-------------------------------------------\n\n")
        print("Begining of the waiting period")
        print("\n\n-------------------------------------------")
        time.sleep(30)
        print("-------------------------------------------\n\n")
        print(Fore.BLACK + Back.RED + "End of the wainting period, press D to stop the save.")
        print(Style.RESET_ALL)
        print("\n\n-------------------------------------------")
        self.controller.show_frame(AfterQuestionFrame)


class AfterQuestionFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        label = tk.Label(self,text = "Pendant cette écoute musicale,\ncomment vous êtes vous senti.e ?\n\nPrenez le temps d'utiliser ces échelles de façon honnête et précise.", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.1, anchor=CENTER)

        self.relaxation = Eva(self,"Détendu.e/relaxé.e ?","Pas du tout","Completement")
        self.relaxation.place(relx=0.2,rely=0.30,relwidth=0.6)

        self.excitation = Eva(self,"Eveillé.e/agité.e/excité.e ?","Pas du tout","Completement")
        self.excitation.place(relx=0.2,rely=0.50,relwidth=0.6)

        self.restoration = Eva(self,"Ressourcé.e/apaisé.e/reposé.e?","Pas du tout","Completement")
        self.restoration.place(relx=0.2,rely=0.70,relwidth=0.6)

        self.next_button = tk.Button(self,text='Suivant',font=BUTTON_FONT,command=lambda : self.stop())
        self.next_button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE) 

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)

    def stop(self):
        if self.relaxation.get()!=50.00 and self.relaxation.get()!=50.00 and self.restoration.get()!=50.00:
            saved_json["after_excitation"]=self.excitation.get()
            saved_json["after_relaxation"]=self.relaxation.get()
            saved_json["after_restoration"]=self.restoration.get()
            save_json()
            print("-------------------------------------------\n\n")
            print(self.excitation.get(),self.relaxation.get(),self.restoration.get())
            print("End of the questions after relaxation")
            print("\n\n-------------------------------------------")
            self.controller.show_frame(AfterQuestion2Frame)
        else :
            self.label_warning["text"]='Merci de repondre à toutes les questions'
       

class AfterQuestion2Frame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.influence = Eva(self,"Est-ce que vos pensées étaient influencées par l'ambiance sonore ?","A aucun moment","Tout le temps")
        self.influence.place(relx=0.2,rely=0.2,relwidth=0.6)

        self.evoke = Eva(self,"Est-ce que l'ambiance sonore évoquait un environnement dans lequel\nvous vous êtes projeté ?","A aucun moment","Tout le temps")
        self.evoke.place(relx=0.2,rely=0.4,relwidth=0.6)

        self.next_button = tk.Button(self,text='Suivant',font=BUTTON_FONT,command=lambda : self.stop())
        self.next_button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE)

        self.label_warning = Label(self,'',font=LARGE_FONT,fg="red")
        self.label_warning.place(relx=0.60,rely=0.99,relwidth=0.6,relheight=0.10,anchor=SE)

    def stop(self):

        if self.influence.get()!=50.00 and self.evoke.get()!=50.00:
            saved_json["after_influence"]=self.influence.get()
            saved_json["after_evoke"]=self.evoke.get()
            print("-------------------------------------------\n\n")
            print(self.influence.get(),self.evoke.get())
            print("End of the after questions")
            print("\n\n-------------------------------------------")
            save_json()
            self.controller.show_frame(LastFrame)
        else :
            self.label_warning["text"]='Merci de repondre à toutes les questions'


class LastFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        label = tk.Label(self,text = "Cette partie est maintenant terminé.\nCliquez sur 'Suivant'.", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.5, anchor=CENTER)

        button1 = tk. Button(self,text="Suivant",font=BUTTON_FONT,command = lambda :self.end())
        button1.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)
    
    def end(self):
        print("---------------------------\n\n"+
              "end of the bloc\n\n"+
              "---------------------------")
        sys.exit()

app = MasterWindow()
app.mainloop()
