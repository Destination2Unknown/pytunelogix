# pytunelogix
**Python PID Tuner for ControlLogix**

To install use:

```
pip install pytunelogix
```



_________________________________________________________________________________________________________________________
**Stage 1 - Tune based on a CSV file of a PRC**

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



![image](https://user-images.githubusercontent.com/92536730/174582410-7f11dac4-94ca-46d1-a641-4e0bc3da6fe2.png)



```

WIP

```



_________________________________________________________________________________________________________________________
**Stage 3 - Closed loop tune**


![image](https://user-images.githubusercontent.com/92536730/174582629-f4673405-de55-44a0-8156-1efb9d2d4cfc.png)


```

WIP

```



_________________________________________________________________________________________________________________________
**Stage 4 - Adaptive tuner**


![image](https://user-images.githubusercontent.com/92536730/174582749-9b514d13-463b-42ca-8aec-b48bfe07c386.png)


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
