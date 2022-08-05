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
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import tkinter as tk
from pytunelogix.common import generalclasses as g

#Random Noise between -0.25 and 0.25, same set used for each run. Created once at runtime.
minsize=600
maxsize=25200
noise= np.random.rand(maxsize)/2
noise-=0.25

def main():  
    def refresh():
        #get values from tkinter 
        if str(ind_button['state']) =='disabled' and str(sec_button['state'])=='disabled':
            calcKp.set(tKp.get())
            calcKi.set(tKi.get())
            calcKd.set(tKd.get())
        elif str(ind_button['state']) =='disabled' and str(sec_button['state'])=='normal': 
            calcKp.set(tKp.get())
            calcKi.set(float(tKi.get())/60)
            calcKd.set(float(tKd.get())*60)	
        elif str(ind_button['state']) =='normal' and str(sec_button['state'])=='disabled':
            calcKp.set(tKp.get())
            calcKi.set(float(tKp.get())/(float(tKi.get())))
            calcKd.set(float(tKp.get())*float(tKd.get()))
        elif str(ind_button['state']) =='normal' and str(sec_button['state'])=='normal':              
            calcKp.set(tKp.get())
            calcKi.set(float(tKp.get())/(float(tKi.get())*60))
            calcKd.set(float(tKp.get())*float(tKd.get())*60)
        igain,itau,ideadtime=float(tK.get()),float(ttau.get()),float(tdt.get())
        ikp,iki,ikd = float(calcKp.get()),float(calcKi.get()),float(calcKd.get())
            
        #Find the size of the range needed
        if (ideadtime+itau)*7 < minsize:
         rangesize = minsize
        elif (ideadtime+itau)*7 >maxsize:
         rangesize = maxsize
        else:
         rangesize = int((ideadtime+itau)*7)

        #setup time intervals
        t = np.arange(start=0, stop=rangesize, step=1)

        #Setup data arrays
        SP = np.zeros(len(t)) 
        PV = np.zeros(len(t))
        CV = np.zeros(len(t))
        pterm = np.zeros(len(t))
        iterm = np.zeros(len(t))
        dterm = np.zeros(len(t))
        global noise
        noise=np.resize(noise, len(t))
        
        #defaults
        ibias=float(tAmb.get())
        startofstep=10

        #Packup data
        PIDGains=(ikp,iki,ikd)
        ModelData=(igain,itau,ideadtime,ibias)
        #Filter for D term
        if radioFilter.get()=='Filter':
            tc=max(0.1*itau,0.8,ideadtime)
            num=tc*(itau+0.5*ideadtime)
            den=itau*(tc+ideadtime)
            dFilter=num/den
        else:
            dFilter=1
        direction=radioDirection.get()
        
        #Process Variable Tracking
        if radioPvT.get()=='PvT':
            PvT=1
        else:
            PvT=0

        #PID Instantiation
        pid = g.PID(ikp, iki, ikd, SP[0])
        pid.output_limits = (0, 100)
        pid.tunings=(PIDGains)

        #plant Instantiation
        plant=g.FOPDTModel(CV, ModelData)

        #Start Value
        PV[0]=ibias+noise[0]
        
        #Loop through to find PID output and Process value
        for i in t:        
            if i<len(t)-1:            
                if i < startofstep-1:
                    SP[i] = ibias
                elif i< rangesize*0.6:
                    if direction=="Direct":
                        SP[i]= 60 + ibias
                    else:
                        SP[i] = ibias - 60
                else:
                    if direction=="Direct":
                        SP[i]= 40 + ibias
                    else:
                        SP[i]= ibias - 40
                #Find current controller output                
                CV[i]=pid(PV[i], SP[i],direction,dFilter,0 if (i < startofstep and PvT==0) else 1)
                ts = [t[i],t[i+1]]
                #Send step data
                plant.CV=CV
                #Find calculated PV
                PV[i+1] = plant.update(PV[i],ts)
                PV[i+1]+=noise[i]
                #Store indiv. terms
                pterm[i],iterm[i],dterm[i]=pid.components
            else:
                #cleanup endpoint
                SP[i]=SP[i-1]
                CV[i]=CV[i-1]
                pterm[i]=pterm[i-1]
                iterm[i]=iterm[i-1]
                dterm[i]=dterm[i-1]
            itae = 0 if i < startofstep else itae+(i-startofstep)*abs(SP[i]-PV[i])
                
        #Display itae value    
        itae_text.set(round(itae/len(t),2)) #measure PID performance
        
        #Plots
        plt.figure()    
        plt.subplot(2, 1, 1) 
        plt.plot(t,SP, color="blue", linewidth=2, label='SP')
        plt.plot(t,CV,color="darkgreen",linewidth=2,label='CV')
        plt.plot(t,PV,color="red",linewidth=2,label='PV')    
        plt.ylabel('EU')    
        plt.suptitle("ITAE: %s" % round(itae/len(t),2))        
        plt.title(tUnitP.get()+": "+tKp.get() + "      " + tUnitI.get()+ ": " + tKi.get()+"      " + tUnitD.get() +": "   + tKd.get() ,fontsize=10)
        plt.legend(loc='best')

        plt.subplot(2,1,2)
        plt.plot(t,pterm, color="lime", linewidth=2, label='P Term')
        plt.plot(t,iterm,color="orange",linewidth=2,label='I Term')
        plt.plot(t,dterm,color="purple",linewidth=2,label='D Term')        
        plt.xlabel('Time [seconds]')
        plt.legend(loc='best')
        plt.show(block=False)

    def convert(selector):   
        if selector == "S":
            sec_button['state']='disabled'
            min_button['state']='normal'
            if str(dep_button['state']) =='normal' and str(ind_button['state'])=='disabled':
                tUnitP.set("Kp")
                tUnitI.set("Ki (1/s)")
                tUnitD.set("Kd (s)")
                thisp=str(round(float(tKp.get()),6))
                thisi=str(round(float(tKi.get())/60,6))
                thisd=str(round(float(tKd.get())*60,6))
                tKp.delete(0,'end')
                tKi.delete(0,'end')
                tKd.delete(0,'end')
                tKp.insert(0,thisp)
                tKi.insert(0,thisi)
                tKd.insert(0,thisd)

            elif str(dep_button['state']) =='disabled' and str(ind_button['state'])=='normal':
                tUnitP.set("Kc")
                tUnitI.set("Ti (sec/repeat)")
                tUnitD.set("Td (sec)")
                thisp=str(round(float(tKp.get()),6))
                thisi=str(round(float(tKi.get())*60,6))
                thisd=str(round(float(tKd.get())*60,6))
                tKp.delete(0,'end')
                tKi.delete(0,'end')
                tKd.delete(0,'end')
                tKp.insert(0,thisp)
                tKi.insert(0,thisi)
                tKd.insert(0,thisd)

        elif selector == "M":
            sec_button['state']='normal'
            min_button['state']='disabled'
            if str(dep_button['state']) =='normal' and str(ind_button['state'])=='disabled':
                tUnitP.set("Kp")
                tUnitI.set("Ki (1/min)")
                tUnitD.set("Kd (min)")
                thisp=str(round(float(tKp.get()),6))
                thisi=str(round(float(tKi.get())*60,6))
                thisd=str(round(float(tKd.get())/60,6))
                tKp.delete(0,'end')
                tKi.delete(0,'end')
                tKd.delete(0,'end')
                tKp.insert(0,thisp)
                tKi.insert(0,thisi)
                tKd.insert(0,thisd)

            elif str(dep_button['state']) =='disabled' and str(ind_button['state'])=='normal':
                tUnitP.set("Kc")
                tUnitI.set("Ti (min/repeat)")
                tUnitD.set("Td (min)")
                thisp=str(round(float(tKp.get()),6))
                thisi=str(round(float(tKi.get())/60,6))
                thisd=str(round(float(tKd.get())/60,6))
                tKp.delete(0,'end')
                tKi.delete(0,'end')
                tKd.delete(0,'end')
                tKp.insert(0,thisp)
                tKi.insert(0,thisi)
                tKd.insert(0,thisd)

        elif selector == "D":
            ind_button['state']='normal'
            dep_button['state']='disabled'
            if str(sec_button['state']) =='disabled' and str(min_button['state'])=='normal':              
                tUnitP.set("Kc")
                tUnitI.set("Ti (sec/repeat)")
                tUnitD.set("Td (sec)")
                thisp=str(round(float(tKp.get()),6))
                thisi=str(round(float(tKp.get())/float(tKi.get()),6))
                thisd=str(round(float(tKd.get())/float(tKp.get()),6))
                tKp.delete(0,'end')
                tKi.delete(0,'end')
                tKd.delete(0,'end')
                tKp.insert(0,thisp)
                tKi.insert(0,thisi)
                tKd.insert(0,thisd)

            elif str(sec_button['state']) =='normal' and str(min_button['state'])=='disabled':              
                tUnitP.set("Kc")
                tUnitI.set("Ti (min/repeat)")
                tUnitD.set("Td (min)")
                thisp=str(round(float(tKp.get()),6))
                thisi=str(round(float(tKp.get())/(float(tKi.get())),6))
                thisd=str(round(float(tKd.get())/float(tKp.get()),6))
                tKp.delete(0,'end')
                tKi.delete(0,'end')
                tKd.delete(0,'end')
                tKp.insert(0,thisp)
                tKi.insert(0,thisi)
                tKd.insert(0,thisd)

        elif selector == "I":
            ind_button['state']='disabled'
            dep_button['state']='normal'
            if str(sec_button['state']) =='disabled' and str(min_button['state'])=='normal':                    
                tUnitP.set("Kp")
                tUnitI.set("Ki (1/s)")
                tUnitD.set("Kd (s)")
                thisp=str(round(float(tKp.get()),6))
                thisi=str(round(float(tKp.get())/float(tKi.get()),6))
                thisd=str(round(float(tKd.get())*float(tKp.get()),6))
                tKp.delete(0,'end')
                tKi.delete(0,'end')
                tKd.delete(0,'end')
                tKp.insert(0,thisp)
                tKi.insert(0,thisi)
                tKd.insert(0,thisd)

            elif str(sec_button['state']) =='normal' and str(min_button['state'])=='disabled': 
                tUnitP.set("Kp")
                tUnitI.set("Ki (1/min)")
                tUnitD.set("Kd (min)")
                thisp=str(round(float(tKp.get()),6))
                thisi=str(round(float(tKp.get())/float(tKi.get()),6))
                thisd=str(round(float(tKd.get())*float(tKp.get()),6))
                tKp.delete(0,'end')
                tKi.delete(0,'end')
                tKd.delete(0,'end')
                tKp.insert(0,thisp)
                tKi.insert(0,thisi)
                tKd.insert(0,thisd)
        
    #Gui
    root = tk.Tk()
    root.title('PID Simulator with a FOPDT Process Model')
    root.resizable(True, True)
    root.geometry('500x180')

    #Labels
    tK = tk.Entry(root,width=8)
    ttau = tk.Entry(root,width=8)
    tdt= tk.Entry(root,width=8)
    tKp = tk.Entry(root,width=8)
    tKi = tk.Entry(root,width=8)
    tKd= tk.Entry(root,width=8)
    tAmb = tk.Entry(root,width=8)
    radioFilter = tk.StringVar()
    radioDirection = tk.StringVar()
    radioPvT = tk.StringVar()
    itae_text = tk.StringVar()
    tUnitP = tk.StringVar()
    tUnitI = tk.StringVar()
    tUnitD = tk.StringVar()
    tUnits = tk.StringVar()
    calcKp = tk.StringVar()
    calcKi = tk.StringVar()
    calcKd = tk.StringVar()

    tk.Label(root, text=" ").grid(row=0,column=0)
    tk.Label(root, text="FOPDT").grid(row=0,column=1)
    tk.Label(root, text="Model Gain: ").grid(row=1,sticky="E")
    tk.Label(root, text="TimeConstant: ").grid(row=2,sticky="E")
    tk.Label(root, text="DeadTime: ").grid(row=3,sticky="E")
    tk.Label(root, text="Ambient: ").grid(row=4,sticky="E")
    tk.Label(root, text="                 ").grid(row=0,column=2,sticky="W")
    tk.Label(root, text="                 ").grid(row=0,column=3,sticky="W")
    tk.Label(root, text="PID Gains").grid(row=0,column=4)
    tk.Label(root, textvariable=tUnitP).grid(row=1,column=2,columnspan=2,sticky="E")
    tk.Label(root, textvariable=tUnitI).grid(row=2,column=2,columnspan=2,sticky="E")
    tk.Label(root, textvariable=tUnitD).grid(row=3,column=2,columnspan=2,sticky="E")

    tK.insert(0, "2.25")
    ttau.insert(0, "60.5")
    tdt.insert(0, "9.99")
    tKp.insert(0, "3")
    tKi.insert(0, "0.1")
    tKd.insert(0, "3")
    calcKp.set("3")
    calcKi.set("0.1")
    calcKd.set("3")
    tAmb.insert(0, "13.5")
    radioFilter.set("Filter")
    radioDirection.set("Direct")
    radioPvT.set("PvT")
    itae_text.set("...")
    tUnitP.set("Kp")
    tUnitI.set("Ki (1/s)")
    tUnitD.set("Kd (s)")

    tK.grid(row=1, column=1)
    ttau.grid(row=2, column=1)
    tdt.grid(row=3, column=1)
    tKp.grid(row=1, column=4)
    tKi.grid(row=2, column=4)
    tKd.grid(row=3, column=4)
    tAmb.grid(row=4, column=1)

    button_refresh = tk.Button(root, text="Refresh", command=refresh)
    button_refresh.grid(row=5,column=1)
    tk.Label(root, text="itae:").grid(row=4,column=3)
    tk.Label(root, textvariable=itae_text).grid(row=4,column=4,padx=5,sticky="NESW")
    
    tk.Radiobutton(root, text = "Filter", variable=radioFilter, value = "Filter").grid(row=3,column=7,padx=5,pady=0, sticky="NESW")
    tk.Radiobutton(root, text = "UnFiltered", variable=radioFilter, value = "UnFilter").grid(row=3,column=8,padx=5,pady=0,columnspan=2, sticky="NESW")
    tk.Radiobutton(root, text = "Direct", variable=radioDirection, value = "Direct").grid(row=4,column=7,padx=5,pady=0, sticky="NESW")
    tk.Radiobutton(root, text = "Reverse", variable=radioDirection, value = "Reverse").grid(row=4,column=8,padx=5,pady=0,columnspan=2, sticky="NESW")
    tk.Radiobutton(root, text = "PV Tracking", variable=radioPvT, value = "PvT").grid(row=5,column=7,padx=5,pady=0, sticky="NESW")
    tk.Radiobutton(root, text = "No PvT", variable=radioPvT, value = "NoPvT").grid(row=5,column=8,padx=5,pady=0,columnspan=2, sticky="NESW")

    ind_button = tk.Button(root,text='Independant',command=lambda :[convert("I")])
    ind_button.grid(row=1,column=7,padx=5,pady=0,sticky="NESW")
    ind_button['state']='disabled'

    dep_button = tk.Button(root,text='Dependant',command=lambda :[convert("D")])
    dep_button.grid(row=1,column=8,padx=5,pady=0,sticky="NESW")

    sec_button = tk.Button(root,text='Seconds',command=lambda :[convert("S")])
    sec_button.grid(row=2,column=7,padx=5,pady=0,sticky="NESW")
    sec_button['state']='disabled'

    min_button = tk.Button(root,text='Minutes',command=lambda :[convert("M")])
    min_button.grid(row=2,column=8,padx=5,pady=0,sticky="NESW")

    root.mainloop()
 
if __name__ == '__main__':
    main()