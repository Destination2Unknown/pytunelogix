"""
   
Updated and maintained by destination0b10unknown@gmail.com
Copyright 2022 destination2unknown

Licensed under the MIT License;
you may not use this file except in compliance with the License.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
   
"""
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy import signal
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import tkinter.filedialog
from pytunelogix.common import generalclasses as g

def main():
    # create the root window
    root = tk.Tk()
    root.title('PID Tuner Based on a FOPDT Model')
    root.resizable(True, True)
    root.geometry('550x380')

    fname = tk.StringVar()
    modelgain = tk.StringVar()
    modeltc = tk.StringVar()
    modeldt = tk.StringVar()
    ambient = tk.StringVar()
    tCHRKp = tk.StringVar()
    tCHRKi = tk.StringVar()
    tCHRKd = tk.StringVar()
    tIMCKp = tk.StringVar()
    tIMCKi = tk.StringVar()
    tIMCKd = tk.StringVar()
    tAIMCKp = tk.StringVar()
    tAIMCKi = tk.StringVar()
    tAIMCKd = tk.StringVar()
    tUnitKp = tk.StringVar()
    tUnitKi= tk.StringVar()
    tUnitKd= tk.StringVar()

    def step1():
        filetypes = (('CSV files', '*.csv'),('All files', '*.*'))
        filename= tk.filedialog.askopenfilename(
            title='Open a file',
            initialdir=os.getcwd(),
            filetypes=filetypes)
        if filename!="":
            fname.set(filename)
                
    def step2(filename):
        if bool(fname.get()) == True:
            #Calculation Variables
            deltaT=0.1 #assume 100ms interval
            twosecwindow=int(2/deltaT)
            onesecwindow=int(1/deltaT)
            hihilimit=1.05
            lololimit=0.95
            hilimit=1.02
            lowlimit=0.98
            settlingwindow=5
            window=int(settlingwindow/deltaT)

            df = pd.read_csv(filename, sep=';')
            #Find relevant columns
            CV_cols = [col for col in df.columns if 'CV' in col.upper()]
            PV_cols = [col for col in df.columns if 'PV' in col.upper()]

            #Create DataFrames
            df['CV'] = df[CV_cols[0]]
            df['PV'] = df[PV_cols[0]]

            #Direction
            if df['PV'].iloc[1] > df['PV'].iloc[-1]:
                if df['CV'].idxmin()< df['CV'].idxmax():
                    direction="Reverse"
                else:
                    direction="Direct"    
            else:
                if df['CV'].idxmin()< df['CV'].idxmax():
                    direction="Direct"
                else:
                    direction="Reverse"

            #Find basic parameters
            if df['CV'].idxmin()< df['CV'].idxmax():
                i_start=df['CV'].idxmax()
            else:
                i_start=df['CV'].idxmin()
            ambient.set(round(df['PV'].iloc[:i_start+onesecwindow].mean(axis = 0),2))
            StartPV=df['PV'].iloc[i_start]
            InitCV=df['CV'].iloc[0]
            StartCV=df['CV'].iloc[i_start]

            #DeadTime Range
            RangeU=round(float(ambient.get()),2)*hihilimit
            RangeL=round(float(ambient.get()),2)*lololimit
                    
            #Find DeadTime
            if (direction=="Reverse" and df['CV'].idxmin()< df['CV'].idxmax()) or (direction=="Direct" and df['CV'].idxmin()> df['CV'].idxmax()):
                for x in range(i_start,(len(df['PV'])-window)):
                    if(df['PV'].iloc[x:x+twosecwindow:1].mean(axis = 0)<RangeL):
                        modeldt.set(round((x-i_start)*deltaT,2))
                        break
            else:
                for x in range(i_start,(len(df['PV'])-window)):
                    if(df['PV'].iloc[x:x+twosecwindow:1].mean(axis = 0)>RangeU):
                        modeldt.set(round((x-i_start)*deltaT,2))
                        break

            #Find Gain
            if (direction=="Reverse" and df['CV'].idxmin()< df['CV'].idxmax()) or (direction=="Direct" and df['CV'].idxmin()> df['CV'].idxmax()):
                j=df['PV'].idxmin()
                min_peak=df['PV'].min()
            else:
                j=df['PV'].idxmax()
                max_peak=df['PV'].max()
                
            peak = df['PV'].iloc[j-onesecwindow:j+onesecwindow:1].mean(axis = 0)
            modelgain.set(round((peak-round(float(ambient.get()),2))/(StartCV-InitCV),2))

            #Time Constant
            tc_value=0.63*(peak-float(ambient.get()))+float(ambient.get())
            tc_upp=tc_value*1.01
            tc_low=tc_value*0.99

            #Find Time Constant
            if (direction=="Reverse" and df['CV'].idxmin()< df['CV'].idxmax()) or (direction=="Direct" and df['CV'].idxmin()> df['CV'].idxmax()):
                z=df[df['PV']<=StartPV-(peak*0.1)].first_valid_index()        
                for x in range(z,(len(df['PV'])-window)):
                    if(df['PV'].iloc[x-twosecwindow:x+twosecwindow:1].mean(axis = 0)<tc_low):
                        modeltc.set(round(((x-i_start)*deltaT)-float(modeldt.get()),2))
                        break
                    else:
                        modeltc.set(-1)
                        
            else:
                z=df[df['PV']>=(peak*0.5)].first_valid_index()        
                for x in range(z,(len(df['PV'])-window)):
                    if(df['PV'].iloc[x-twosecwindow:x+twosecwindow:1].mean(axis = 0)>tc_value):
                        modeltc.set(round(((x-i_start)*deltaT)-float(modeldt.get()),2))
                        break
                    else:
                        modeltc.set(-1)

            #Setup System Model
            num = [float(modelgain.get())]
            den = [float(modeltc.get()),1]
            sys1 = signal.TransferFunction(num,den)
            tune() 

            #Find Step Response based on Rough Model
            t1,y1 = signal.step(sys1, N=int(df['PV'].count()/10))
            t1=t1[::10]
            y1=y1[::10]

            #Rescale
            plotpv=df['PV'].iloc[::10].reset_index(drop=True)
            plotcv=df['CV'].iloc[::10].reset_index(drop=True)

            #plot 
            plt.figure()
            plt.xlim(0,df['PV'].count()*0.11)
            plt.plot(plotpv, color="blue", linewidth=3, label='PV')
            plt.plot(t1+(i_start/10+(float(modeldt.get()))),((StartCV-InitCV)*y1)+round(float(ambient.get()),2),color="red",linewidth=3,label='Model')
            plt.plot(plotcv, color="green", linewidth=3, label='CV')
            plt.hlines(round(float(ambient.get()),2), 0, i_start/10+float(modeldt.get()),colors='red', linestyles='solid',linewidth=3,label='')
            plt.ylabel('Engineering Units')
            plt.xlabel('Seconds')
            plt.suptitle("Rough Model v Actual Data")
            plt.title(f"ModelGain: {round(float(modelgain.get()),2)}   ModelTc: {round(float(modeltc.get()),2)}   ModelDT: {round(float(modeldt.get()),2)}")
            plt.legend(loc='best')
            plt.show(block=False)

    def step3(filename):
        if bool(fname.get())==True:
            #Read File 
            df = pd.read_csv(filename, sep=';')

            #Find CV and PV Columns
            CV_cols = [col for col in df.columns if 'CV' in col.upper()]
            PV_cols = [col for col in df.columns if 'PV' in col.upper()]
            df['CV'] = df[CV_cols[0]]
            df['PV'] = df[PV_cols[0]]

            #Find Step Size
            CVStep=df['CV'].max()-df['CV'].min()

            #start of step
            if df['CV'].idxmin()< df['CV'].idxmax():
                indexofstart=df['CV'].idxmax()
            else:
                indexofstart=df['CV'].idxmin()

            ambient.set(round(df['PV'].iloc[:indexofstart].mean(axis = 0),2))

            #produces a model based on the parameters
            def fopdt_func(t_fopdt, K=1, tau=1, deadtime=0):
                deadtime = max(0,deadtime)
                tau = max(0,tau)
                return np.array([K*(1-np.exp(-(t_fopdt-deadtime)/tau)) if t_fopdt >= deadtime else 0 for t_fopdt in t_fopdt])

            #Difference between model and actual
            def err(Xe,te,ye):
                Ke,tau,DeadTime = Xe
                z = CVStep*fopdt_func(te,Ke,tau,DeadTime)+float(ambient.get())
                iae = sum(abs(z-ye))*(max(te)-min(te))/len(te)
                return iae

            #Trim Timescale
            actualPV=df['PV'].iloc[max(0,indexofstart-1)::10].reset_index(drop=True)
            actualCV=df['CV'].iloc[max(0,indexofstart-1)::10].reset_index(drop=True)
            t=actualPV.index.values

            #Model Starting Point
            if modelgain.get() =="...":
                ModelValues = 1.1,60,10
            else:
                ModelValues = float(modelgain.get()),float(modeltc.get()), float(modeldt.get())
                
            #minimize difference between model and actual
            bounds = [(None, None), (0, None), (0,None)]
            Gain,Tau,DeadTime = minimize(err,ModelValues,args=(t, actualPV.values),bounds=bounds, method='Nelder-Mead').x

            #Update holder
            modelgain.set(round(Gain,2))
            modeltc.set(round(Tau,2))
            modeldt.set(round(DeadTime,2))
            tune()

            #Get data to plot new model 
            ymodel=CVStep*fopdt_func(t,float(modelgain.get()),float(modeltc.get()), float(modeldt.get()))+float(ambient.get())
            
            #Invert sign on Negative Step
            if df['CV'].idxmin()> df['CV'].idxmax():
                modelgain.set(round(-Gain,2))

            #Plot
            plt.figure()
            plt.plot(actualPV,color="blue",linewidth=3,label='PV')
            plt.plot(actualCV,color="green",linewidth=3,label='CV')
            plt.plot(ymodel,color="red",linewidth=3,label='Model')
            plt.xlabel('Seconds')
            plt.ylabel('Engineering Units')
            plt.suptitle('Refined Model v Actual Data')
            plt.title(f"ModelGain: {round(float(modelgain.get()),2)}   ModelTc: {round(float(modeltc.get()),2)}   ModelDT: {round(float(modeldt.get()),2)}")
            plt.legend(loc='best')
            plt.show(block=False)
                
    def runthesim(processmodel,tune):
        #EntryPoint
        minsize=300
        maxsize=7200

        #unpack values 
        igain,itau,ideadtime=processmodel
        ikp,iki,ikd = tune

        #Find the size of the range needed
        if ideadtime*2+itau*10 < minsize:
            rangesize = minsize
        elif ideadtime*2+itau*10 >maxsize:
            rangesize = maxsize
        else:
            rangesize = int(ideadtime*2+itau*10)

        #setup time intervals
        t = np.arange(rangesize)
        #Random Noise between -0.1 and 0.1
        noise= 0.2*np.random.rand(rangesize)
        noise-=0.1
        #noise=np.zeros(rangesize) #no noise

        #Setup data arrays
        SP = np.zeros(len(t)) 
        PV = np.zeros(len(t))
        CV = np.zeros(len(t))
        pterm = np.zeros(len(t))
        iterm = np.zeros(len(t))
        dterm = np.zeros(len(t))
        
        #defaults
        startofstep=10

        #Packup data
        PIDGains=(ikp,iki,ikd)
        ModelData=(igain,itau,ideadtime,float(ambient.get()))

        #PID Instantiation
        pid = g.PID(ikp, iki, ikd, SP[0])
        pid.output_limits = (0, 100)
        pid.tunings=(PIDGains)

        #plant Instantiation
        plant=g.FOPDTModel(CV, ModelData)

        #Start Value
        PV[0]=float(ambient.get())+noise[0]
        
        #Loop through timestamps
        for i in t:        
            if i<(len(t)-1):
                if i < startofstep:
                    SP[i] = float(ambient.get())
                elif (i > startofstep and i< rangesize/2):
                    if float(modelgain.get()) > 0:
                        SP[i]= 50 + float(ambient.get())
                    else:
                        SP[i]= float(ambient.get()) - 50
                else:
                    if float(modelgain.get()) > 0:
                        SP[i]=40 + float(ambient.get())
                    else:
                        SP[i]= float(ambient.get()) - 40
                #Find current controller output
                CV[i]=pid(PV[i], SP[i], "Direct" if float(modelgain.get()) > 0 else "Reverse")               
                ts = [i,i+1]
                #Send step data
                plant.CV=CV
                #Find calculated PV
                PV[i+1] = plant.update(PV[i],ts)
                PV[i+1]+=noise[i]
            else:
                #cleanup endpoint
                SP[i]=SP[i-1]
                CV[i]=CV[i-1]
            itae = 0 if i < startofstep else itae+(i-startofstep)*abs(SP[i]-PV[i])
                
        #Display itae value    
        itae=(round(itae/len(t),2)) #measure PID performance
        dataout=SP,PV,CV,itae
        return dataout

    def step4():
        if modelgain.get()!="..." and tCHRKp.get()!="...":
            processmodel=float(modelgain.get()),float(modeltc.get()), float(modeldt.get())
            CHRtune=tuner.CHRKp,tuner.CHRKi,tuner.CHRKd
            IMCtune= tuner.IMCKp,tuner.IMCKi,tuner.IMCKd
            AIMCtune=tuner.AIMCKp,tuner.AIMCKi,tuner.AIMCKd

            #store pid data array from simulation
            CHR=runthesim(processmodel,CHRtune)
            IMC=runthesim(processmodel,IMCtune)
            AIMC=runthesim(processmodel,AIMCtune)

            #Unpack the data returned
            CHRSP,CHRPV,CHRCV,CHRitae=CHR
            IMCSP,IMCPV,IMAIMCV,IMCitae=IMC
            AIMCSP,AIMCPV,AIMCCV,AIMCitae=AIMC

            plt.figure()    
            plt.plot(CHRSP, color="goldenrod", linewidth=3, label='SP')
            plt.plot(CHRPV,color="darkgreen",linewidth=2,label='CHR PV')
            plt.plot(IMCPV,color="blue",linewidth=2,label='IMC PV')    
            plt.plot(AIMCPV, color="red", linewidth=2, label='AIMC PV')
        
            plt.ylabel('EU')    
            plt.xlabel('Seconds')
            plt.suptitle("PID Tune Comparison")        
            plt.title("CHR ITAE:%s      IMC ITAE:%s      AIMC ITAE:%s" % (CHRitae, IMCitae, AIMCitae),fontsize=10)
            plt.legend(loc='best')
            plt.show(block=False)

    def tune(selector="C"):
        if modelgain.get()!="...":
            model=float(modelgain.get()),float(modeltc.get()), float(modeldt.get())
            if selector=="C":            
                con_button['state']='disabled'
                agg_button['state']='normal'
                tuner.calc(model)
            elif selector=='A':            
                con_button['state']='normal'
                agg_button['state']='disabled'
                tuner.calcFullFat(model)       
            if selector == "S":
                sec_button['state']='disabled'
                min_button['state']='normal'
            elif selector == "M":
                sec_button['state']='normal'
                min_button['state']='disabled'
            elif selector == "D":
                ind_button['state']='normal'
                dep_button['state']='disabled'
            elif selector == "I":
                ind_button['state']='disabled'
                dep_button['state']='normal'

            if str(dep_button['state']) =='normal' and str(sec_button['state'])=='disabled':
                tUnitKp.set("Kp")
                tUnitKi.set("      Ki (1/s)      ")
                tUnitKd.set("    Kd (s)    ")
                tCHRKp.set(round(tuner.CHRKp,4))
                tCHRKi.set(round(tuner.CHRKi,4))
                tCHRKd.set(round(tuner.CHRKd,4))
                tIMCKp.set(round(tuner.IMCKp,4))
                tIMCKi.set(round(tuner.IMCKi,4))
                tIMCKd.set(round(tuner.IMCKd,4))
                tAIMCKp.set(round(tuner.AIMCKp,4))
                tAIMCKi.set(round(tuner.AIMCKi,4))
                tAIMCKd.set(round(tuner.AIMCKd,4))

            elif str(dep_button['state']) =='normal' and str(sec_button['state'])=='normal':
                tUnitKp.set("Kp")
                tUnitKi.set("    Ki (1/min)    ")
                tUnitKd.set("   Kd (min)   ")
                tCHRKp.set(round(tuner.CHRKp,4))
                tCHRKi.set(round(tuner.CHRKi*60,4))
                tCHRKd.set(round(tuner.CHRKd/60,4))
                tIMCKp.set(round(tuner.IMCKp,4))
                tIMCKi.set(round(tuner.IMCKi*60,4))
                tIMCKd.set(round(tuner.IMCKd/60,4))
                tAIMCKp.set(round(tuner.AIMCKp,4))
                tAIMCKi.set(round(tuner.AIMCKi*60,4))
                tAIMCKd.set(round(tuner.AIMCKd/60,4))
            
            elif str(dep_button['state']) =='disabled' and str(sec_button['state'])=='disabled':
                tUnitKp.set("Kc")
                tUnitKi.set(" Ti (sec/repeat) ")
                tUnitKd.set("Td (sec)")
                tCHRKp.set(round(tuner.CHRKp,4))
                tCHRKi.set(round(tuner.CHRKp/(tuner.CHRKi),4))
                tCHRKd.set(round(tuner.CHRKd/(tuner.CHRKp),4))
                tIMCKp.set(round(tuner.IMCKp,4))
                tIMCKi.set(round(tuner.IMCKp/(tuner.IMCKi),4))
                tIMCKd.set(round(tuner.IMCKd/(tuner.IMCKp),4))
                tAIMCKp.set(round(tuner.AIMCKp,4))
                tAIMCKi.set(round(tuner.AIMCKp/(tuner.AIMCKi),4))
                tAIMCKd.set(round(tuner.AIMCKd/(tuner.AIMCKp),4))

            else: 
                tUnitKp.set("Kc")
                tUnitKi.set("Ti (min/repeat)")
                tUnitKd.set("Td (min)")
                tCHRKp.set(round(tuner.CHRKp,4))
                tCHRKi.set(round(tuner.CHRKp/(tuner.CHRKi*60),4))
                tCHRKd.set(round(tuner.CHRKd/(tuner.CHRKp*60),4))
                tIMCKp.set(round(tuner.IMCKp,4))
                tIMCKi.set(round(tuner.IMCKp/(tuner.IMCKi*60),4))
                tIMCKd.set(round(tuner.IMCKd/(tuner.IMCKp*60),4))
                tAIMCKp.set(round(tuner.AIMCKp,4))
                tAIMCKi.set(round(tuner.AIMCKp/(tuner.AIMCKi*60),4))
                tAIMCKd.set(round(tuner.AIMCKd/(tuner.AIMCKp*60),4))

    tuner=g.tunefinderFOPDT()
    modeldt.set('...')
    modeltc.set('...')
    modelgain.set('...')
    ambient.set('...')
    tCHRKp.set("...")
    tCHRKi.set("...")
    tCHRKd.set("...")
    tIMCKp.set("...")
    tIMCKi.set("...")
    tIMCKd.set("...")
    tAIMCKp.set("...")
    tAIMCKi.set("...")
    tAIMCKd.set("...")
    tUnitKp.set("     Kp     ")
    tUnitKi.set("      Ki (1/s)      ")
    tUnitKd.set("   Kd (s)   ")

    step1_button = ttk.Button(root,text='Step 1: Open CSV File    ',command=lambda :[step1()])
    step1_button.grid(row=0,column=0,padx=5,pady=4,sticky="NESW")

    step2_button = ttk.Button(root,text='Step 2: Estimate Model ',command=lambda :[step2(fname.get())])
    step2_button.grid(row=1,column=0,padx=5,pady=4,sticky="NESW")

    step3_button = ttk.Button(root,text='Step 3: Refine Model     ', command=lambda :[step3(fname.get())])
    step3_button.grid(row=2,column=0,padx=5,pady=4,sticky="NESW")

    step4_button = ttk.Button(root,text='Step 4: Run PID Sim       ',command=lambda :[step4()])
    step4_button.grid(row=3,column=0,padx=5,pady=4,sticky="NESW")

    con_button = ttk.Button(root,text='Conservative',command=lambda :[tune("C")])
    con_button.grid(row=6,column=0,padx=5,pady=4,sticky="NESW")
    con_button['state']='disabled'

    agg_button = ttk.Button(root,text='Aggressive',command=lambda :[tune("A")])
    agg_button.grid(row=7,column=0,padx=5,pady=4,sticky="NESW")

    ind_button = ttk.Button(root,text='Independant',command=lambda :[tune("I")])
    ind_button.grid(row=8,column=0,padx=5,pady=4,sticky="NESW")
    ind_button['state']='disabled'

    dep_button = ttk.Button(root,text='Dependant',command=lambda :[tune("D")])
    dep_button.grid(row=9,column=0,padx=5,pady=4,sticky="NESW")

    sec_button = ttk.Button(root,text='Seconds',command=lambda :[tune("S")])
    sec_button.grid(row=10,column=0,padx=5,pady=4,sticky="NESW")
    sec_button['state']='disabled'

    min_button = ttk.Button(root,text='Minutes',command=lambda :[tune("M")])
    min_button.grid(row=11,column=0,padx=5,pady=4,sticky="NESW")

    tk.Label(root, textvariable=fname).grid(row=0,column=1,columnspan=5,padx=1,pady=1,sticky="W")
    tk.Label(root, text="Model Gain:").grid(row=1,column=1,columnspan=2,padx=1,pady=1,sticky="W")
    tk.Label(root, text="TimeConstant (s):").grid(row=2,column=1,columnspan=1,padx=1,pady=1,sticky="W")
    tk.Label(root, text="DeadTime (s):").grid(row=3,column=1,columnspan=1,padx=1,pady=1,sticky="W")
    tk.Label(root, text="Ambient:").grid(row=4,column=1,columnspan=1,padx=1,pady=1,sticky="W")
    tk.Label(root, textvariable=modelgain).grid(row=1,column=2,padx=1,pady=1,sticky="NESW")
    tk.Label(root, textvariable=modeltc).grid(row=2,column=2,padx=1,pady=1,sticky="NESW")
    tk.Label(root, textvariable=modeldt).grid(row=3,column=2,padx=1,pady=1,sticky="NESW")
    tk.Label(root, textvariable=ambient).grid(row=4,column=2,padx=1,pady=1,sticky="NESW")
    spacer="____________________________________________________"
    tk.Label(root, text=spacer).grid(row=5,column=1,columnspan=4)
    tk.Label(root, text="PID Gains ->").grid(row=6,column=1,sticky="W")
    tk.Label(root, textvariable=tUnitKp).grid(row=6,column=2,sticky="NESW")
    tk.Label(root, textvariable=tUnitKi).grid(row=6,column=3,sticky="NESW")
    tk.Label(root, textvariable=tUnitKd).grid(row=6,column=4,sticky="NESW")
    tk.Label(root, text="CHR Method").grid(row=7,column=1,sticky="W")
    tk.Label(root, text="IMC Method").grid(row=8,column=1,sticky="W")
    tk.Label(root, text="AIMC Method").grid(row=9,column=1,sticky="W")
    tk.Label(root, textvariable=tCHRKp).grid(row=7,column=2,padx=4,pady=4,sticky="NESW")
    tk.Label(root, textvariable=tCHRKi).grid(row=7,column=3,padx=4,pady=4,sticky="NESW")
    tk.Label(root, textvariable=tCHRKd).grid(row=7,column=4,padx=4,pady=4,sticky="NESW")
    tk.Label(root, textvariable=tIMCKp).grid(row=8,column=2,padx=4,pady=4,sticky="NESW")
    tk.Label(root, textvariable=tIMCKi).grid(row=8,column=3,padx=4,pady=4,sticky="NESW")
    tk.Label(root, textvariable=tIMCKd).grid(row=8,column=4,padx=4,pady=4,sticky="NESW")
    tk.Label(root, textvariable=tAIMCKp).grid(row=9,column=2,padx=4,pady=4,sticky="NESW")
    tk.Label(root, textvariable=tAIMCKi).grid(row=9,column=3,padx=4,pady=4,sticky="NESW")
    tk.Label(root, textvariable=tAIMCKd).grid(row=9,column=4,padx=4,pady=4,sticky="NESW")

    # run the gui
    root.mainloop()

if __name__ == '__main__':
    main()