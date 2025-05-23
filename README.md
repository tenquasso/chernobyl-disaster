# chernobyl nuclear reactor simulation

![chernobyl nuclear power plant](https://raw.githubusercontent.com/tenquasso/chernobyl-disaster/main/lab.jpg)

## the chernobyl disaster

on april 26, 1986, the worst nuclear accident in history occurred at the chernobyl nuclear power plant in ukraine (then part of the soviet union). the accident happened during a routine safety test on reactor number 4. a combination of operator errors, unsafe reactor design, and safety system failures led to an explosion that released large amounts of radioactive material into the atmosphere.

### main factors of the accident:
1. rbmk reactor design with positive void coefficient
2. improper safety test procedures
3. excessive control rod withdrawal
4. emergency cooling system failure
5. lack of adequate containment structure

## reactor simulation

this simulation models the behavior of the rbmk-1000 reactor, focusing on:
- heat transfer and coolant phase changes
- positive void reactivity effects
- nuclear poison accumulation (xenon-135)
- safety and cooling systems
- radiation levels and radioactive material release

## usage

run the simulation:
```bash
python reactor_simulation.py
```

### controls:
- space: pause/resume simulation
- up/down: adjust simulation speed (0.1x - 2.0x)
- esc: exit simulation

### monitored parameters:
- reactor temperature
- system pressure
- thermal power
- steam fraction
- radiation levels
- safety system status
- nuclear poison levels

 
