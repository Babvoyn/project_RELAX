import tkinter as tk
from tkinter import *
from tkinter import ttk
from threading import Thread
from pathlib import Path
import time
import numpy
import wave
import pyaudio
import json
import sys
import os
import click
from datetime import date
from relax.biofeedback import Biofeedback

sys.path.insert(0,'/home/manip3/Desktop/Relax/BalloonShooter')
from balloonShooter import launch_balloonshooter, get_score_balloonshooter

os.chdir("/home/manip3/Desktop/Relax")

###################### Definition of the parameters and the saving file ######################

# Parameters for the general
subject_id= []
age= []
gender= []
height= []
weight = []

score = []


cond= 'mock'
subject_id_training= 'TRAINING'
block= 1
egg_pos= 1
egg_freq= 0.05

ecg_poses = [2,8]
resp_pos = 0
sampling_rate = 2048
hostname = '192.168.1.1'
port = 1972

master_volume = float

example_factor = ["forest/", 0.2, 0.3, 0.5]

# Font size
LARGE_FONT = ('Helvetica',25)
BUTTON_FONT = ('Helvetica',20)


# create the list that will contain registered data
saved_json = {}

# create the string that will contain the path for the jason file
FullPath = str


###################### Definition of the different class & function to be used in the main tkinter Frames ######################
class MultiChoiceParam(Frame):
    def __init__(self, frame, text,values):
        super().__init__(frame)

        label = Label(self,text=text,font=LARGE_FONT)
        label.pack()
        self.answer = ttk.Combobox(self,font=LARGE_FONT)
        self.answer['values'] = values
        self.answer['state'] = 'readonly'
        self.answer.pack()

    def get(self):
        return self.answer.get()


class StringParam(Frame):
    def __init__(self, frame, text,default_text):
        super().__init__(frame)

        label = Label(self,anchor=E,text=text,font=LARGE_FONT)
        label.grid(row=0,column=0,padx = 5, pady = 5)
        self.answer = Entry(self,font=LARGE_FONT)
        self.answer.insert(END,default_text)
        self.answer.grid(row=0,column=1,padx = 5, pady = 5)

    def get(self):
        return self.answer.get()


class IntQuestion(Frame):
    def __init__(self, frame, text,from_,to,set_ = 18):
        super().__init__(frame)

        label = Label(self,text=text,font=LARGE_FONT)
        label.pack()
        self.answer = Spinbox(self,from_=from_,to=to,wrap=True,font=LARGE_FONT)
        self.answer.delete(0,"end")
        self.answer.insert(0,max(from_,set_))
        self.answer.pack()

    def get(self):
        return self.answer.get()


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
        master_volume,
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

# Initialisation

@click.command()
@click.option("--subj", prompt="Subject id")
def initialisation(subj):
    global FullPath
    FullPath = "Data/Header/"+"RELAX"+"_sub-"+str(subj)+"_header"+".json"
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
class MasterWindow(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        #display the window full screen on the second screen
        self.wm_geometry("1080x920+2160+0")
        self.attributes('-fullscreen',True)
        self.title("RELAX")
    
        # create the frame that will fill the window and be used by all frame class
        container = Frame(self)
        container.pack(fill='both',expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        # container for all the frames
        self.frames={}

        for all_frame in (FirstFrame,PersonalQuestion,Game_InstructionFrame,Game_TrainingFrame,ScoreFrame,VolumeFrame,BeforeQuestionFrame,BeforeRelaxFrame,RelaxFrame,EndRelaxFrame,AfterQuestionFrame,AfterQuestion2Frame,RetrainingFrame,LastFrame):
            frame = all_frame(container,self)
            self.frames[all_frame] = frame
            frame.grid(row=0,column= 0, sticky = "nsew")

        self.show_frame(FirstFrame)
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()

    def begin(self,cont):
        self.frames[cont].begin()
    

class FirstFrame(Frame): 
    def __init__(self,parent,controller):
        Frame.__init__(self,parent)
        self.controller = controller

        label = Label(self,text = "Merci de votre participation.\n\nDurant cette expérience, il vous sera demandé de vous relaxer en écoutant différentes ambiances sonores.\n\nToutes les instructions seront présentées à l'écran.\nSi vous avez la moindre question, n'hésitez pas à demander à l'expérimentateur.\n\n\nAppuyez sur 'Suivant' pour passer à la suite.", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.5, anchor=CENTER)
        
        button =  Button(self,text="Suivant",font=BUTTON_FONT,command = lambda : self.controller.show_frame(PersonalQuestion))
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)


class PersonalQuestion(Frame):
    def __init__(self,parent,controller):
        Frame.__init__(self,parent)
        self.controller = controller

        label = Label(self,anchor=CENTER,text="Veuillez répondre à ces quelques questions.\n\nElles ne sont associées qu'avec votre numéro de participant, pas à votre nom.",font=LARGE_FONT)
        label.place(relx = 0.2,rely=0.2,relwidth=0.6,relheight=0.1)

        self.age = IntQuestion(self,"Quel est votre âge ?",18,99,18)
        self.age.place(relx = 0.2,rely=0.4,relwidth=0.6,relheight=0.1)

        self.gender= MultiChoiceParam(self,"Quel est votre genre ?",("Masculin","Féminin","Non binaire"))
        self.gender.place(relx = 0.2,rely=0.5,relwidth=0.6,relheight=0.1) 

        self.height = IntQuestion(self,"Quelle est votre taille (en cm) ?",140,210,160)
        self.height.place(relx = 0.2,rely=0.6,relwidth=0.6,relheight=0.1)

        self.weight = IntQuestion(self,"Quel est votre poids (en kg) ?",40,120,50)
        self.weight.place(relx = 0.2,rely=0.7,relwidth=0.6,relheight=0.1)

        self.next_button = tk.Button(self,text='Suivant',font=BUTTON_FONT,command=lambda : self.stop())
        self.next_button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE) 
        

    def stop(self):
        saved_json["age"]=self.age.get()
        saved_json["gender"]=self.gender.get()
        saved_json["height"]=self.height.get()
        saved_json["weight"]=self.weight.get()
        save_json()
        self.controller.show_frame(VolumeFrame)
        self.controller.begin(VolumeFrame)
        print("-------------------------------------------\n\n")
        print(["Personal Information : "+str(self.age.get()),";"+str(self.gender.get()),";"+str(self.height.get()),";"+str(self.weight.get())])
        print("\n\n-------------------------------------------")

CHUNK = 1024

class VolumeFrame(ttk.Frame):

    def __init__(self,parent,controller):
        Frame.__init__(self,parent)
        self.controller=controller
        self.file = str(Path(__file__).parent / '../volume_scale_sound')
        self.thread = Thread(target=self.play_wav)
        self.stop_thread = False
        self.volume = 0.005
        self.pred_factor_ecg = example_factor[1]
        self.pred_factor_resp = example_factor[2]
        self.pred_factor_egg = example_factor[3]

        # Normalise the factor if their sum isnt egal to 1
        if self.pred_factor_ecg+self.pred_factor_resp+self.pred_factor_egg != 1:
            norm_factor = 1/(self.pred_factor_ecg+self.pred_factor_resp+self.pred_factor_egg)
            self.pred_factor_ecg *= norm_factor
            self.pred_factor_resp *= norm_factor
            self.pred_factor_egg *= norm_factor

        self.volume_slider = Eva(
            self,
            "Veuillez faire glisser le slider pour régler le volume du son.\n\nLes différents sons doit être net, bien audibles, tout en restant confortables.\nUne fois que le volume du son vous convient, cliquer sur 'Suivant'",
            "Low",
            "High",
            from_ = 0.005,
            to_= 0.1,
            set_= 0.005,
            resolution=0.0001)
        self.volume_slider.place(relx=0.15,rely=0.25,relwidth=0.7)

        self.volume_slider.slider["command_"]=self.update_volume

        self.stop_button = tk.Button(self,text="Suivant",font=BUTTON_FONT,command=self.stop)
        self.stop_button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05,anchor=SE)

    def update_volume(self,event):
        self.volume = self.volume_slider.get()

    def play_wav(self):

        def get_data(wf,volume):
            data_ecg = wf[0].readframes(CHUNK)
            if len(data_ecg) < 2*CHUNK:
                wf[0] =  wave.open(self.file+"/ecg.wav", 'rb')
                data_ecg = wf[0].readframes(CHUNK)
            data_resp = wf[1].readframes(CHUNK)
            if len(data_resp) < 2*CHUNK:
                wf[1] =  wave.open(self.file+"/resp.wav", 'rb')
                data_resp = wf[1].readframes(CHUNK)
            data_egg = wf[2].readframes(CHUNK)
            if len(data_egg) < 2*CHUNK:
                wf[2] =  wave.open(self.file+"/egg.wav", 'rb')
                data_egg = wf[2].readframes(CHUNK)
            decodeddata_ecg = numpy.fromstring(data_ecg, numpy.int16)
            decodeddata_resp = numpy.fromstring(data_resp, numpy.int16)
            decodeddata_egg = numpy.fromstring(data_egg, numpy.int16)
            newdata = ((
                (decodeddata_ecg*self.pred_factor_ecg)+(decodeddata_resp*self.pred_factor_resp)+(decodeddata_egg*self.pred_factor_egg)
                )*volume).astype(numpy.int16)
            return newdata.tostring()

        wf_ecg = wave.open(self.file+"/ecg.wav", 'rb')
        wf_resp = wave.open(self.file+"/resp.wav", 'rb')
        wf_egg = wave.open(self.file+"/egg.wav", 'rb')

        print('opening sounds')

        wf = [wf_ecg,wf_resp,wf_egg]

        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf_ecg.getsampwidth()),
                    channels=wf_ecg.getnchannels(),
                    rate=wf_ecg.getframerate(),
                    output=True)

        data = get_data(wf,self.volume)

        while data != b'' and not self.stop_thread:
            stream.write(data)
            data = get_data(wf,self.volume)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def begin(self):
        self.place(x=0,rely=0,relwidth=1.0,relheight=1.0)
        self.thread.start()

    def stop(self):
        if self.thread.is_alive():
            self.stop_thread = True
            self.thread.join()
        saved_json["volume"]=self.volume
        global master_volume
        master_volume = self.volume
        save_json()
        print("-------------------------------------------\n\n")
        print(["Master Volume : "+str(self.volume)])
        print("\n\n-------------------------------------------")
        self.pack_forget()
        self.controller.show_frame(Game_InstructionFrame)

class Game_InstructionFrame(Frame):
    def __init__(self,parent,controller):
        self.controller = controller
        Frame.__init__(self,parent)
        label = Label(self,text = "Nous allons maintenant vous présenter un jeu, qui sera utilisé dans la suite de l'éxperience.\nIl n'y a pas de son dans ce jeu.\n\nVous devrez cliquer sur des ballons apparaissant à l'écran.\n\nPointez avec la souris et utilisez le bouton gauche pour éclater le ballon.\nTentez d'éclater un maximum de ballon dans le temps imparti (1 minute).\n\nVous pouvez maintenant vous entrainer.\n\nCliquez sur 'Jouer' pour commencer.", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.5, anchor=CENTER)

        button = Button(self,text="Jouer",font=BUTTON_FONT,command = lambda : self.controller.begin(Game_TrainingFrame))
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)


class Game_TrainingFrame(Frame):
    def __init__(self,parent,controller):
        Frame.__init__(self,parent)
        self.controller = controller

    def begin(self):
        launch_balloonshooter()
        global score
        score = get_score_balloonshooter()
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
        self.label["text"]="Votre score est : {}".format(score)+"\n\nLe score vous sera affichée à chaque fin de jeu.\n\nAppuyer sur suivant pour continuer."
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

        self.label = tk.Label(self,text = "La session de relaxation va commencer dans quelques instant. Elle est composées d'ambiances sonores successives.\n\nL'ambiance sonore commencera après plusieurs dizaines de secondes, c'est normal.\n\nLa session dure environ 4 minutes.\n\nIl vous sera demandé de fermer les yeux et de vous relaxer, même lors de la période du silence.\n\nUne fois le son terminé, réouvrez les yeux et suivez les instructions.", font=LARGE_FONT)
        self.label.place(relx=0.5,rely=0.5, anchor=CENTER)

        button1 = tk. Button(self,text="Débuter",font=BUTTON_FONT,command = lambda : [self.controller.show_frame(RelaxFrame), print("-------------------------------------------\n\nEnd of the questions before relaxation\n\n-------------------------------------------") ,self.controller.begin(RelaxFrame)])
        button1.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)
        

class RelaxFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.label = tk.Label(self,text = "La session de relaxation a commencé.\n\nFermez les yeux et relaxez vous.\n\nL'ambiance sonore ne commencera qu'après quelque dizaines de seconde.\n\nLorsque le son s'arrête, vous pouvez réouvrir les yeux,\nmais ne bougez pas jusqu'à ce que la prochaine fenêtre apparaisse.", font=LARGE_FONT)
        self.label.place(relx=0.5,rely = 0.5, anchor=CENTER)

    def begin(self):
        launch_block(cond,
                    subject_id_training,
                    block,
                    egg_pos,
                    egg_freq,
                    ecg_poses,
                    resp_pos,
                    sampling_rate,
                    hostname,
                    port,
                    master_volume)
        
        self.controller.show_frame(EndRelaxFrame)
        self.controller.begin(EndRelaxFrame)


class EndRelaxFrame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.label = tk.Label(self,text = "La session de relaxation est terminée.\n\n Merci de ne pas bouger jusqu'à ce que la prochaine fenêtre apparaisse.", font=LARGE_FONT)
        self.label.place(relx=0.5,rely = 0.5, anchor=CENTER)


    def begin(self):
        print("-------------------------------------------\n\n")
        print("Begining of the waiting period")
        print("\n\n-------------------------------------------")
        time.sleep(30)
        print("-------------------------------------------\n\n")
        print("End of the wainting period")
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
            self.controller.show_frame(RetrainingFrame)
        else :
            self.label_warning["text"]='Merci de repondre à toutes les questions'

class RetrainingFrame(Frame):
    def __init__(self,parent,controller):
        Frame.__init__(self,parent)
        self.controller = controller
        label = Label(self,text = "Cette partie est maintenant terminée.\n\nAvant de passer à la prochaine partie,\nsouhaitez vous plus d'explication sur les termes ?", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.5, anchor=CENTER)

        button = Button(self,text="Non",font=BUTTON_FONT,command = lambda : self.answer("besoin d'explication : NON"))
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)

        button = Button(self,text="Oui",font=BUTTON_FONT,command = lambda : self.answer("besoin d'explication : OUI"))
        button.place(relx=0.05,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SW)

    def answer(self,ans):
        print("---------------------------\n\n"+
              ans+" \n\n"+
              "---------------------------")
        self.controller.show_frame(LastFrame)


class LastFrame(Frame):
    def __init__(self,parent,controller):
        Frame.__init__(self,parent)
        self.controller = controller
        label = Label(self,text = "Cette partie est maintenant terminée.\n\nAvant de passer à la prochaine partie,\nsouhaitez vous vous entraîner de nouveaux sur les jeux ?", font=LARGE_FONT)
        label.place(relx=0.5,rely = 0.5, anchor=CENTER)

        button = Button(self,text="Non",font=BUTTON_FONT,command = lambda : self.answer("besoin d'un entrainement : NON"))
        button.place(relx=0.95,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SE)

        button = Button(self,text="Oui",font=BUTTON_FONT,command = lambda : self.answer("besoin d'un entrainement : OUI"))
        button.place(relx=0.05,rely=0.95,relwidth=0.25,relheight=0.05, anchor=SW)

    def answer(self,ans):
        print("---------------------------\n\n"+
              ans+" \n\n"+
              "---------------------------")
        sys.exit()

if __name__ == "__main__":
    initialisation()        

