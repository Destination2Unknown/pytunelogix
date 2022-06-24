def main():
    import tkinter as tk
    import numpy as np
    import matplotlib.pyplot as plt
    import random
    import threading
    import time
    from matplotlib import animation
    from scipy.integrate import odeint
    from pylogix import PLC
    from pytunelogix.common import generalclasses as g

    class data(object):
        def __init__(self):      
            self.PV = np.zeros(0)
            self.CV = np.zeros(0)
            self.SP = np.zeros(0)
            self.livetrend=0
            self.scanCount=0
        def storereads(self,CV,SP):
            self.CV=np.append(self.CV,CV)
            self.SP=np.append(self.SP,SP)
        def storepv(self,PV):
            self.PV=np.append(self.PV,PV)       
        def reset(self):
            self.PV = np.zeros(0)
            self.CV = np.zeros(0)
            self.SP = np.zeros(0)
            self.scanCount=0

    def fopdtsetup():
        process.Gain=float(modelgain.get())
        process.TimeConstant=float(modeltc.get())*10
        process.DeadTime=float(modeldt.get())*10
        process.Bias=float(ambient.get())
        process.t=0
        gData.reset()
        gData.livetrend=1
        spstatus.set("")
        pvstatus.set("")
        cvstatus.set("")
        comm.IPAddress = ip.get()
        comm.ProcessorSlot = int(slot.get()) 
        comm.SocketTimeout = 1
        button_start["state"] = "disabled"
        button_stop["state"] = "normal"
        button_trend["state"] = "normal"
        ip.configure(state="disabled")
        slot.configure(state="disabled")
        modelgain.configure(state="disabled")
        modeltc.configure(state="disabled")
        modeldt.configure(state="disabled")
        ambient.configure(state="disabled")
            
    def thread_start():    
        global looper
        looper = g.PeriodicInterval(start, 0.1)

    def start():
        try:
            ret = comm.Read([cvtag.get(),sptag.get()])
            if ret[0].Status=='Success':
                cvtext.set(round(ret[0].Value,2))         
                cvtag.configure(state="disabled")       
                actualcv=ret[0].Value
            else:
                cvstatus.set(ret[0].Status)
                if gData.CV.size>1:
                    actualcv=gData.CV[-1]
                else:
                    actualcv=0

            if ret[1].Status=='Success':
                sptext.set(round(ret[1].Value,2))         
                sptag.configure(state="disabled") 
                actualsp=ret[1].Value
            else:
                spstatus.set(ret[1].Status)
                if gData.SP.size>1:
                    actualsp=gData.SP[-1]
                else:
                    actualsp=0

            #Send CV to Process
            process.CV=gData.CV
            #Store Data when it is read
            gData.storereads(actualcv,actualsp)
            ts=[gData.scanCount,gData.scanCount+1]

            #Get new PV value
            if gData.PV.size>1:
                pv=process.update(gData.PV[-1],ts)
            else:
                pv=process.update(float(ambient.get()),ts)
            #Add Noise between -0.1 and 0.1
            noise=(random.randint(0,10)/100)-0.05
            #Store PV
            gData.storepv(pv[0]+noise)
            #Write PV to PLC   
            write = comm.Write(pvtag.get(),gData.PV[-1])
            if write.Status=='Success':
                pvtext.set(round(write.Value,2))         
                pvtag.configure(state="disabled")            
            else:
                pvstatus.set(write.Status)
            gData.scanCount+=1
            
        except Exception as e:
            pvstatus.set('An exception occurred: {}'.format(e))     
        
    def stop():
        button_start["state"] = "normal"
        button_stop["state"] = "disabled"
        ip.configure(state="normal")
        slot.configure(state="normal")
        modelgain.configure(state="normal")
        modeltc.configure(state="normal")
        modeldt.configure(state="normal")
        pvtag.configure(state="normal")
        cvtag.configure(state="normal")
        sptag.configure(state="normal")
        ambient.configure(state="normal")
        gData.livetrend=0
        if 'looper' in globals():
                looper.stop()
        comm.Close()
        
    def livetrend(): 
        #Set up the figure
        fig = plt.figure()
        ax = plt.axes(xlim=(0,100),ylim=(0, 100))
        SP, = ax.plot([], [], lw=2, color="Red", label='SP')
        CV, = ax.plot([], [], lw=2, color="Green", label='CV')
        PV, = ax.plot([], [], lw=2, color="Blue", label='PV')

        #Setup Func
        def init():
            SP.set_data([], [])
            PV.set_data([], [])
            CV.set_data([], [])        
            plt.ylabel('EU')  
            plt.xlabel("Time (min)")
            plt.suptitle("Live Data")        
            plt.legend(loc='best')
            return SP,PV,CV,

        #Loop here
        def animate(i):     
            x = np.arange(len(gData.SP),dtype=int)
            scale = int(60*1000/100) #Convert mS to Minutes
            x=x/scale
            ax.set_xlim(0,max(x)*1.1)
            max_y=max(max(gData.PV),max(gData.CV),max(gData.SP))
            min_y=min(min(gData.PV),min(gData.CV),min(gData.SP))
            ax.set_ylim(min_y-1,max_y+1)
            SP.set_data(x,gData.SP)
            CV.set_data(x,gData.CV)
            PV.set_data(x,gData.PV)
            return SP,PV,CV,

        #Live Data
        if gData.livetrend:
            anim = animation.FuncAnimation(fig, animate, init_func=init, frames=100, interval=1000) #, blit=True) # cant use blit with dynamic x-axis

        plt.show()

    #Gui
    root = tk.Tk()
    root.title('CLX PID Stand Alone Simulator')
    root.resizable(True, True)
    root.geometry('500x325')

    #Text tags setup
    pvtext = tk.StringVar()
    cvtext = tk.StringVar()
    sptext = tk.StringVar()
    pvstatus = tk.StringVar()
    cvstatus = tk.StringVar()
    spstatus = tk.StringVar()
    pvtag = tk.Entry(root,width=10)
    cvtag = tk.Entry(root,width=10)
    sptag = tk.Entry(root,width=10)
    ip = tk.Entry(root,width=15)
    slot = tk.Entry(root,width=5)
    modelgain = tk.Entry(root,width=5)
    modeltc = tk.Entry(root,width=5)
    modeldt = tk.Entry(root,width=5)
    ambient = tk.Entry(root,width=5)

    #Column 0
    #Labels
    tk.Label(root, text="Tag").grid(row=0,column=0,padx=10 ,pady=2,sticky="NESW")
    tk.Label(root, text="SP:").grid(row=1,column=0,padx=10 ,pady=2,sticky="NESW")
    tk.Label(root, text="PV:").grid(row=2,column=0,padx=10 ,pady=2,sticky="NESW")
    tk.Label(root, text="CV:").grid(row=3,column=0,padx=10 ,pady=2,sticky="NESW")
    #Row 4 = Button
    #Row 5 = Button
    tk.Label(root, text="PLC IP Address:").grid(row=6,column=0,padx=10 ,pady=2)
    tk.Label(root, text="PLC Slot:").grid(row=7,column=0,padx=10 ,pady=2)
    tk.Label(root, text="Model Gain:").grid(row=8,column=0,padx=10 ,pady=2,sticky="NESW")
    tk.Label(root, text="Model TimeConstant(s):").grid(row=9,column=0,padx=10 ,pady=2,sticky="NESW")
    tk.Label(root, text="Model DeadTime(s):").grid(row=10,column=0,padx=10 ,pady=2,sticky="NESW")
    tk.Label(root, text="Model Ambient:").grid(row=11,column=0,padx=10 ,pady=2,sticky="NESW")

    #Column 1
    #Labels
    tk.Label(root, text="Value").grid(row=0,column=1,padx=10 ,pady=2,sticky="NESW")
    tk.Label(root, textvariable=sptext).grid(row=1,column=1,padx=10 ,pady=2,sticky="NESW")
    tk.Label(root, textvariable=pvtext).grid(row=2,column=1,padx=10 ,pady=2,sticky="NESW")
    tk.Label(root, textvariable=cvtext).grid(row=3,column=1,padx=10 ,pady=2,sticky="NESW")
    #Row 4 = Button
    #Row 5 = Button
    ip.grid(row=6, column=1,padx=10 ,pady=2,sticky="NESW")
    slot.grid(row=7, column=1,padx=10 ,pady=2,sticky="NESW")
    modelgain.grid(row=8, column=1,padx=10 ,pady=2,sticky="NESW")
    modeltc.grid(row=9, column=1,padx=10 ,pady=2,sticky="NESW")
    modeldt.grid(row=10, column=1,padx=10 ,pady=2,sticky="NESW")
    ambient.grid(row=11, column=1,padx=10 ,pady=2,sticky="NESW")

    #Column 2
    #Actual PLC TagName
    tk.Label(root, text="PLC Tag").grid(row=0,column=2,padx=10 ,pady=2)
    sptag.grid(row=1, column=2,padx=10 ,pady=2,sticky="NESW")
    pvtag.grid(row=2, column=2,padx=10 ,pady=2,sticky="NESW")
    cvtag.grid(row=3, column=2,padx=10 ,pady=2,sticky="NESW")

    #Column 3
    #Status
    tk.Label(root, text="Last Error:").grid(row=0,column=3,padx=10,columnspan=2 ,pady=2,sticky="NESW")
    tk.Label(root, textvariable=spstatus).grid(row=1,column=3,padx=10,columnspan=2 ,pady=2,sticky="NESW")
    tk.Label(root, textvariable=pvstatus).grid(row=2,column=3,padx=10,columnspan=2 ,pady=2,sticky="NESW")
    tk.Label(root, textvariable=cvstatus).grid(row=3,column=3,padx=10,columnspan=2 ,pady=2,sticky="NESW")

    #Default Values
    sptag.insert(10, "SP")
    pvtag.insert(10, "PID_PV")
    cvtag.insert(10, "PID_CV")
    ip.insert(10, "192.168.123.100")
    slot.insert(5, "2")
    modelgain.insert(5, "1.75")
    modeltc.insert(5, "75.5")
    modeldt.insert(5, "17.66")
    ambient.insert(5, "13.5")

    #Buttons
    #Start Button Placement
    button_start = tk.Button(root, text="Start Simulator", command=lambda :[fopdtsetup(),thread_start()])
    button_start.grid(row=4,column=0,columnspan=1,padx=10 ,pady=2,sticky="NESW")

    #Stop Button Placement
    button_stop = tk.Button(root, text="Stop Simulator", command=lambda :[stop()])
    button_stop.grid(row=4,column=1,columnspan=1,padx=10 ,pady=2,sticky="NESW")

    #Trend Button Placement
    button_trend = tk.Button(root, text="Show Trend", command=lambda :[livetrend()])
    button_trend.grid(row=5,column=0,columnspan=2,padx=10 ,pady=2,sticky="NESW")
    button_trend["state"] = "disabled"

    #default setup 
    params=0,0
    model= (modelgain.get(),modeltc.get()*10,modeldt.get()*10,13.1)
    process=g.FOPDTModel(params, model)
    gData=data()
    comm=PLC()

    root.mainloop()

if __name__ == '__main__':
    main()