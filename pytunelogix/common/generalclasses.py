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
import threading
import time 
from scipy.integrate import odeint
import numpy as np

class sthread(threading.Thread):
   def __init__(self,func):
      threading.Thread.__init__(self)
      self.func=func
      
   def run(self):      
      self.func()

class PeriodicInterval(threading.Thread):
    def __init__(self, task_function, period):
        super().__init__()
        self.daemon = True
        self.task_function = task_function
        self.period = period
        self.i = 0
        self.t0 = time.time()
        self.stopper=0
        self.start()
        
    def sleep(self):
        self.i += 1
        delta = self.t0 + self.period * self.i - time.time()
        if delta > 0:
            time.sleep(delta)
    
    def run(self):
        while self.stopper==0:
            self.task_function()
            self.sleep()

    def stop(self):
        self.stopper=1

    def starter(self):
        self.stopper=0  
        self.i = 0
        self.t0 = time.time()

class tunefinderFOPDT(object):
    def __init__(self):
        self.Gain, self.TimeConstant, self.DeadTime = 1.5,60.0,15.0
        self.CHRKp,self.CHRKi, self.CHRKd=0.1,0.01,0.001
        self.IMCKp,self.IMCKi,self.IMCKd=0.2,0.02,0.002
        self.AIMCKp,self.AIMCKi, self.AIMCKd=0.3,0.03,0.003
            
    def calc(self,ModelData):
        self.Gain, self.TimeConstant, self.DeadTime = ModelData
        if (self.TimeConstant<=0):
            self.TimeConstant=1
        if (self.DeadTime<=0):
            self.DeadTime=1
        #CHRKp
        num=0.35*self.TimeConstant 
        den=abs(self.Gain)*self.DeadTime
        self.CHRKp=num/den
        #CHRKi
        ti=1.2*self.TimeConstant
        self.CHRKi=self.CHRKp/ti
        #CHRKd
        td=0.5*self.DeadTime
        self.CHRKd=(self.CHRKp*td)/60
                
        #IMC_Kp
        lmda=2.1*self.DeadTime
        num= self.TimeConstant+0.5*self.DeadTime
        den=abs(self.Gain)*(lmda)
        self.IMCKp = num/den
        #IMC_Ki
        ti=self.TimeConstant+0.5*self.DeadTime
        self.IMCKi = self.IMCKp / ti    
        #IMC_Kd
        num=self.TimeConstant*self.DeadTime
        den=2*self.TimeConstant+self.DeadTime
        td=num/den
        self.IMCKd = (td*self.IMCKp)/60
         
        #AIMC Kp
        L=max(0.1*self.TimeConstant,0.8*self.DeadTime)
        self.AIMCKp=self.TimeConstant/(abs(self.Gain)*(self.DeadTime+L))        
        #AIMC Ki
        ti=self.TimeConstant/(1.03-0.165*(self.DeadTime/self.TimeConstant))
        self.AIMCKi =self.AIMCKp/self.TimeConstant
        #AIMC Kd
        self.AIMCKd=(self.DeadTime/2)/60

    def calcFullFat(self,ModelData):
        self.Gain, self.TimeConstant, self.DeadTime = ModelData
        if (self.TimeConstant<=0):
            self.TimeConstant=1
        if (self.DeadTime<=0):
            self.DeadTime=1  
        #CHRKp
        num=0.6*self.TimeConstant 
        den=abs(self.Gain)*self.DeadTime
        self.CHRKp=num/den
        #CHRKi
        ti=1*self.TimeConstant
        self.CHRKi=self.CHRKp/ti
        #CHRKd
        td=0.5*self.DeadTime
        self.CHRKd=(self.CHRKp*td)
               
        #IMC_Kp
        lmda=2.1*self.DeadTime
        num= self.TimeConstant+0.5*self.DeadTime
        den=abs(self.Gain)*(lmda)
        self.IMCKp = 1.1*(num/den)
        #IMC_Ki
        ti=self.TimeConstant+0.5*self.DeadTime
        self.IMCKi = self.IMCKp / ti    
        #IMC_Kd
        num=self.TimeConstant*self.DeadTime
        den=2*self.TimeConstant+self.DeadTime
        td=num/den
        self.IMCKd = 1.1*(td*self.IMCKp)         

        #AIMC Kp
        L=max(0.1*self.TimeConstant,0.8*self.DeadTime)
        num=self.TimeConstant + 0.5*self.DeadTime
        den=abs(self.Gain)*(L+0.5*self.DeadTime)
        self.AIMCKp=num/den
        #AIMC Ki
        ti=self.TimeConstant+0.5*self.DeadTime
        self.AIMCKi=self.AIMCKp/ti
        #AIMC Kd
        num=self.TimeConstant*self.DeadTime
        den=2*self.TimeConstant+self.DeadTime
        td=num/den
        self.AIMCKd = td*self.AIMCKp

class PID(object):    
    def __init__(self,Kp=1.0,Ki=0.1,Kd=0.01,setpoint=50,output_limits=(0, 100)):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.setpoint = setpoint
        self._min_output, self._max_output = 0, 100
        self._proportional = 0
        self._integral = 0
        self._derivative = 0
        self.output_limits = output_limits
        self._last_eD =0
        self._lastCV=0
        self._d_init=0      
        self.reset()

    def _clamp(self, value, limits):
        lower, upper = limits
        if value is None:
            return None
        elif (upper is not None) and (value > upper):
            return upper
        elif (lower is not None) and (value < lower):
            return lower
        return value

    def __call__(self,PV=0,SP=0,action="Direct",dFilter=1,pvt=1):
            #PID calculations            
            #P term
            if action=="Direct":
                e = SP - PV 
            else:
                e = PV - SP      
            self._proportional = self.Kp * e

            #I Term
            if self._lastCV<100 and self._lastCV >0:        
                self._integral += self.Ki * e
            #Allow I Term to change when Kp is set to Zero
            if self.Kp==0 and self._lastCV==100 and self.Ki * e<0:
                self._integral += self.Ki * e
            if self.Kp==0 and self._lastCV==0 and self.Ki * e>0:
                self._integral += self.Ki * e

            #D term
            if action=="Direct":
                eD=-PV 
            else:
                eD=PV            
            self._derivative = dFilter*self.Kd*(eD - self._last_eD)
            #init D term 
            if self._d_init==0:
                self._derivative=0
                self._d_init=1
            
            #pv tracking
            if pvt==0:
                self._integral=-(self.Kp*e)+0.00001
                
            #Controller Output
            CV = self._proportional + self._integral + self._derivative
            CV = self._clamp(CV, self.output_limits)

            # update stored data for next iteration
            self._last_eD = eD
            self._lastCV=CV
            return CV
        
    @property
    def components(self):
        return self._proportional, self._integral, self._derivative

    @property
    def tunings(self):
        return self.Kp, self.Ki, self.Kd

    @tunings.setter
    def tunings(self, tunings):        
        self.Kp, self.Ki, self.Kd = tunings
    
    @property
    def output_limits(self): 
        return self._min_output, self._max_output

    @output_limits.setter
    def output_limits(self, limits):        
        if limits is None:
            self._min_output, self._max_output = 0, 100
            return

        min_output, max_output = limits
        self._min_output = min_output
        self._max_output = max_output
        self._integral = self._clamp(self._integral, self.output_limits)    
    
    def reset(self):
        #Reset
        self._proportional = 0
        self._integral = 0
        self._derivative = 0
        self._integral = self._clamp(self._integral, self.output_limits)
        self._last_eD = 0
        self._lastCV = 0
        self._last_eD = 0
        self._d_init = 0

class FOPDTModel(object):   
    def __init__(self, CV, ModelData):                
        self.CV= CV
        self.Gain, self.TimeConstant, self.DeadTime, self.Bias = ModelData
        
    def calc(self,PV,ts):                      
        if (ts-self.DeadTime) <= 0:
            um=0
        elif int(ts-self.DeadTime)>=len(self.CV):
            um=self.CV[-1]
        else:
            um=self.CV[int(ts-self.DeadTime)]
        dydt = (-(PV-self.Bias) + self.Gain * um)/(self.TimeConstant)
        return dydt

    def update(self,PV,ts):
        y=odeint(self.calc,PV,ts)           
        return y[-1]