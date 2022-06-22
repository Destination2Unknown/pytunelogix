import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import tkinter as tk
from pytunelogix.common import generalclasses as g

#Random Noise between -0.5 and 0.5, same set used for each run. Created once at runtime.
minsize=600
maxsize=7200
noise= np.random.rand(minsize)
noise-=0.5

def main():  
    def refresh():
        #get values from tkinter 
        igain,itau,ideadtime=float(tK.get()),float(ttau.get()),float(tdt.get())
        ikp,iki,ikd = float(tKp.get()),float(tKi.get()),float(tKd.get())
            
        #Find the size of the range needed
        if (ideadtime+itau)*4 < minsize:
         rangesize = minsize
        elif (ideadtime+itau)*4 >maxsize:
         rangesize = maxsize
        else:
         rangesize = int((ideadtime+itau)*4)

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
        #noise= np.zeros(len(t)) #no noise
        
        #defaults
        ibias=15
        startofstep=10

        #Packup data
        PIDGains=(ikp,iki,ikd)
        ModelData=(igain,itau,ideadtime,ibias)

        #PID Instantiation
        pid = g.PID(ikp, iki, ikd, SP[0])
        pid.output_limits = (0, 100)
        pid.tunings=(PIDGains)

        #plant Instantiation
        plant=g.FOPDTModel(CV, ModelData)

        #Start Value
        PV[0]=ibias+noise[0]
        
        #Loop through timestamps
        for i in t:        
            if i<len(t)-1:            
                if i < startofstep:
                    SP[i] = 0
                elif i< rangesize*0.6:
                    SP[i]= 60 + ibias
                else:
                    SP[i]=40 + ibias
                #Find current controller output
                CV[i]=pid(PV[i], SP[i])               
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
        plt.title("Kp:%s   Ki:%s  Kd:%s" % (ikp, iki, ikd),fontsize=10)
        plt.legend(loc='best')

        plt.subplot(2,1,2)
        plt.plot(t,pterm, color="lime", linewidth=2, label='P Term')
        plt.plot(t,iterm,color="orange",linewidth=2,label='I Term')
        plt.plot(t,dterm,color="purple",linewidth=2,label='D Term')        
        plt.xlabel('Time [seconds]')
        plt.legend(loc='best')
        plt.show()

    #Gui
    root = tk.Tk()
    root.title('PID Simulator')
    root.resizable(True, True)
    root.geometry('450x150')

    #Labels
    tk.Label(root, text=" ").grid(row=0,column=0)
    tk.Label(root, text="FOPDT").grid(row=0,column=1)
    tk.Label(root, text="Model Gain").grid(row=1)
    tk.Label(root, text="Model TimeConstant (s) ").grid(row=2)
    tk.Label(root, text="Model DeadTime (s) ").grid(row=3)
    tk.Label(root, text="                ").grid(row=0,column=2)
    tk.Label(root, text="                ").grid(row=1,column=2)
    tk.Label(root, text="                ").grid(row=2,column=2)
    tk.Label(root, text="                ").grid(row=3,column=2)
    tk.Label(root, text="PID Gains").grid(row=0,column=4)
    tk.Label(root, text="Kp").grid(row=1,column=3)
    tk.Label(root, text="Ki").grid(row=2,column=3)
    tk.Label(root, text="Kd").grid(row=3,column=3)

    tK = tk.Entry(root,width=8)
    ttau = tk.Entry(root,width=8)
    tdt= tk.Entry(root,width=8)
    tKp = tk.Entry(root,width=8)
    tKi = tk.Entry(root,width=8)
    tKd= tk.Entry(root,width=8)

    tK.insert(10, "2.25")
    ttau.insert(10, "60.5")
    tdt.insert(10, "9.99")
    tKp.insert(10, "1.1")
    tKi.insert(10, "0.1")
    tKd.insert(10, "0.09")

    tK.grid(row=1, column=1)
    ttau.grid(row=2, column=1)
    tdt.grid(row=3, column=1)
    tKp.grid(row=1, column=4)
    tKi.grid(row=2, column=4)
    tKd.grid(row=3, column=4)

    button_calc = tk.Button(root, text="Refresh", command=refresh)
    tk.Label(root, text="itae:").grid(row=5,column=3)
    itae_text = tk.StringVar()
    tk.Label(root, textvariable=itae_text).grid(row=5,column=4)

    button_calc.grid(row=5,column=0)

    root.mainloop()
 
if __name__ == '__main__':
    main()