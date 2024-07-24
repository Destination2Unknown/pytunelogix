# Note: Project Archived
For a new and improved version, see [https://github.com/PIDTuningIreland/pyPIDTune](https://github.com/PIDTuningIreland/pyPIDTune)


---


### pytunelogix
**Python PID Tuner for ControlLogix**

![PyPI](https://img.shields.io/pypi/v/pytunelogix?label=pypi%20package)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pytunelogix)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytunelogix)
![GitHub repo size](https://img.shields.io/github/repo-size/destination2unknown/pytunelogix)
![PyPI - License](https://img.shields.io/pypi/l/pytunelogix)

Windows Exe (no install required) -> https://github.com/Destination2Unknown/pytunelogix/releases

To install use:

```
pip install pytunelogix
```


PID tuning in 4 Steps:
```
A-> Record PRC using Logger
B-> Tune using PID Tuner
C-> Refine tune using PID Simulator
D-> Test tune with FOPDT Simulator for Logix PLC
```


To use, create a launch file:

```
examplelaunch.pyw #use pyw for no console
```

_________________________________________________________________________________________________________________________
**PID Logger**



![image](https://user-images.githubusercontent.com/92536730/175526532-df3cdb2c-1b42-4380-8b6f-d4f060a3194b.png)




To launch, use:
```
from pytunelogix.pidlogger import clxlogger

clxlogger.main()
    
```


_________________________________________________________________________________________________________________________
**Stage 1 - PID Tuner based on a CSV file of a Process Reaction Curve (PRC)**

> ***Notes and Limitations:***
>
> - _Assumes CV and PV data stored at 100ms intervals._
>
> - _Assumes there is a single step in CV._
>
> - _Ambient is calculated as an average of the PV prior to the step change._
>
> - _Doesn't work correctly with a ramp in CV or with multiple CV steps._
>  
>  
>  
> ***N.B.***  
> The PID tuning values are calculated for a PV with a standard range span of 100 in engineering units (e.g. 0-100 deg C or 50-150 deg F).              
> If the range of the PV has a different span the PID tuning values **may** need to be rescaled:
> 
>       Example 1: PV range of 200-400 deg C -> PID Gains x2
> 
>       Example 2: PV range of 75-100 deg C -> PID Gains x0.25
>  
>  



To launch, use:
```
from pytunelogix.stage1 import csvtuner

csvtuner.main()

```

Direct Acting:

![U_Tune](https://user-images.githubusercontent.com/92536730/179394923-8757a7b9-d1d6-482b-8bd3-8b4769937206.PNG)



Reverse Acting:

![U_TuneR](https://user-images.githubusercontent.com/92536730/179394927-d35f3e2f-943c-41cc-bfff-cfee028a821f.PNG)




_________________________________________________________________________________________________________________________
**Stage 2 - Open loop tune**





https://user-images.githubusercontent.com/92536730/175918442-017d18a0-0bac-434d-aa44-b8cd3aebe231.mp4




```

Premium Feature - https://github.com/sponsors/Destination2Unknown

```



_________________________________________________________________________________________________________________________
**Stage 3 - Closed loop tune**



https://user-images.githubusercontent.com/92536730/175920990-3fc2cb66-9d08-4c67-aff7-ff410345f9a5.mp4




```

Premium Feature - https://github.com/sponsors/Destination2Unknown

```



_________________________________________________________________________________________________________________________
**Stage 4 - Adaptive tuner**




https://user-images.githubusercontent.com/92536730/175921177-86389b8f-2d3c-4dc7-8949-db4cdd782d84.mp4




```

Premium Feature - https://github.com/sponsors/Destination2Unknown

```

_________________________________________________________________________________________________________________________
**PID Simulator**


Direct Acting:


![pidDirect_DEP](https://user-images.githubusercontent.com/92536730/179607882-859fc354-03c9-4c69-ab1f-6a47c6e74943.PNG)




Reverse Acting:


![pidReverse_DEP](https://user-images.githubusercontent.com/92536730/179607844-f2728155-9c8a-43e7-8710-8e27b0bacc47.PNG)




To launch, use:
```
from pytunelogix.simulate import simulator

simulator.main()
    
```


_________________________________________________________________________________________________________________________
**ControlLogix FOPDT Process Simulator (PID Simulator)**


Simulates a Process:


![UCLX_Sim](https://user-images.githubusercontent.com/92536730/179607984-aaea90ac-85dc-491c-8842-8aad5e23370a.png)



Direct Acting:

![C](https://user-images.githubusercontent.com/92536730/179394941-54fdb56b-a777-4f8d-bde2-d7c2dd7c5a5f.PNG)



Reverse Acting:


![C_R](https://user-images.githubusercontent.com/92536730/179394946-eb06bedd-3006-422f-91c2-66463b97bd0c.PNG)




To launch, use:
```
from pytunelogix.clxpidsim import clxsim

clxsim.main()
    
```

_________________________________________________________________________________________________________________________


**Windows Standalone Exe:**


![Pytunelogix](https://user-images.githubusercontent.com/92536730/183046630-5fb861b3-9824-4276-b7f5-1afa51b1236c.PNG)
