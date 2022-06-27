# pytunelogix
**Python PID Tuner for ControlLogix**

To install use:

```
pip install pytunelogix
```



_________________________________________________________________________________________________________________________
**Stage 1 - PID Tuner based on a CSV file of a Process Reaction Curve (PRC)**

_Assumes CV and PV data stored at 100ms intervals._

To use create a launch file:

```
examplelaunch.pyw
```

```
from pytunelogix.stage1 import csvtuner

if __name__ == '__main__':
    csvtuner.main()
```



![image](https://user-images.githubusercontent.com/92536730/174779654-c4ea6e3f-98e6-478e-98d3-52790d817323.png)



_________________________________________________________________________________________________________________________
**Stage 2 - Open loop tune**





https://user-images.githubusercontent.com/92536730/175918442-017d18a0-0bac-434d-aa44-b8cd3aebe231.mp4




```

WIP

```



_________________________________________________________________________________________________________________________
**Stage 3 - Closed loop tune**



https://user-images.githubusercontent.com/92536730/175920990-3fc2cb66-9d08-4c67-aff7-ff410345f9a5.mp4




```

WIP

```



_________________________________________________________________________________________________________________________
**Stage 4 - Adaptive tuner**




https://user-images.githubusercontent.com/92536730/175921177-86389b8f-2d3c-4dc7-8949-db4cdd782d84.mp4




```

WIP

```

_________________________________________________________________________________________________________________________
**PID Simulator**



![image](https://user-images.githubusercontent.com/92536730/175026471-dab7f7c1-eef5-47aa-a822-6193e83cd369.png)



To launch use:
```
from pytunelogix.simulate import simulator

if __name__ == '__main__': 
    simulator.main()
    
```


_________________________________________________________________________________________________________________________
**PID Logger**



![image](https://user-images.githubusercontent.com/92536730/175526532-df3cdb2c-1b42-4380-8b6f-d4f060a3194b.png)




To launch use:
```
from pytunelogix.pidlogger import clxlogger

if __name__ == '__main__': 
    clxlogger.main()
    
```


_________________________________________________________________________________________________________________________
**ControlLogix FOPDT Process Simulator (PID Simulator)**



![image](https://user-images.githubusercontent.com/92536730/175526821-58908595-a959-4f4c-860c-b74479d37300.png)




To launch use:
```
from pytunelogix.clxpidsim import clxsim

if __name__ == '__main__': 
    clxsim.main()
    
```

