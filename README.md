# deep_cgmd_tutorial
# DeepMD-kit Tutorial: Learning from a LAMMPS Simulation with an example (Deep Water)

This tutorial guides you through training and using a Deep Potential Molecular Dynamics (DeepMD) model. The example, Deep Water, uses LAMMPS to simulate the 2005 edition of the TIP4P water model. The output of the fine-grained simulation is coarse-grained (CG) during the data preparation. Finally the Deep Water model contains a single particle located at the oxygen site.

---

## Table of Contents

1. [Installation](#installation)
2. [Generate Training Data](#generate-training-data)
    - [Prepare LAMMPS Simulation for training data](#prepare-lammps-simulation-for-training-data)
    - [Prepare data in a suitable format for DeePMD](#prepare-data-in-a-suitable-format-for-deepmd)
3. [DeePMD Model](#deepmd-model)
    - [Create a model to train](#create-a-model-to-train)
    - [Train the Model](#train-the-model)
    - [Evaluate the model](#evaluate-the-model)
4. [Use the Model in LAMMPS](#use-the-model-in-lammps)
5. [Analyze Results](#analyze-results)
6. [Side note for Northwestern University Quest users](#side-note-for-northwestern-university-quest-users)
7. [Deep Water (example)](#deep-water-example)

---

## Installation

Install DeepMD-kit and its dependencies:

```bash
module load anaconda3/2018.12
conda create -n deepmd deepmd-kit=*=*cpu libdeepmd=*=*cpu lammps -c https://conda.deepmodeling.org
source activate deepmd
```

Verify the installation by running the following command:

```bash
dp -h
```

## Generate Training Data
To train a model, you'll need trajectory data (box dimensions, atomic positions, forces, energies, and virials).

### Prepare LAMMPS Simulation for training data

To create training data for DeepMD-kit, run a LAMMPS simulation that outputs trajectory data, including atomic positions and per-atom forces. 
```bash
dump 1 all custom 100 dump.lammpstrj id type x y z fx fy fz
```

Manually compute the virial tensor (symmetric) by computing the virial pressure, excluding the kinetic energy term, and multiplying by the system volume:

```bash
compute virial_press all pressure NULL virial

variable Wxx eqal c_virial_press[1]*vol
variable Wyy eqal c_virial_press[2]*vol
variable Wzz eqal c_virial_press[3]*vol
variable Wxy eqal c_virial_press[4]*vol
variable Wxz eqal c_virial_press[5]*vol
variable Wyz eqal c_virial_press[6]*vol
```




Using the thermo_style command, output the potential energy:

```bash
thermo_style custom step pe
```

### Prepare data in a suitable format for DeePMD
Use a script (or packages like dpdata) to convert the simulation outputs into DeepMD's training data format. For simulations in LAMMPS, a convienient method is to first convert all required data to the deepmd/raw format. A sample Python script may look like this:

```python
from deepmd import DataLoader

# Example script to parse LAMMPS dump into DeepMD format
# Use `dpdata` to simplify the process
import dpdata

data = dpdata.System('dump.lammpstrj', fmt='lammps/dump')
data.to('deepmd/npy', 'deepmd_data')
```
Then use dpdata to read in the data in the deepmd/raw format, and prepare it for training. A sample Python script may look like this:

```python
```

---

## DeePMD Model

## Create a model to train
DeepMD-kit uses a JavaScript Object Notation configuration file (input.json) to define the training process. Here's a basic template:

```json
{
    "model": {
      "type_map": ["TYPE_0"],   
      "descriptor": {
        "type": "se_e2_a",
        "rcut": 2.5,
        "sel": "auto",
        "neuron": [25, 50, 100],
        "resnet_dt": false,
        "axis_neuron": 16,                  
        "seed": 1,
        "_comment": "that's all"        
      },
      "fitting_net": {
        "neuron": [240, 240, 240],
        "resnet_dt":       true,
        "seed":            1,
        "_comment":        "that's all"
    }
      },
    "learning_rate": {
      "type": "exp",
      "decay_steps":         50,
      "start_lr":            0.001,    
      "stop_lr":             3.51e-8,
      "_comment":            "that's all"
  },
  "loss" :{
    "type":                "ener",
    "start_pref_e":        0.02,
    "limit_pref_e":        1,
    "start_pref_f":        1000,
    "limit_pref_f":        1,
    "start_pref_v":        0,
    "limit_pref_v":        0,
    "_comment":            "that's all"
  },
  "training" : {
    "training_data": {
        "systems":            ["./deepmd_data"],     
        "batch_size":         "auto",                       
        "_comment":           "that's all"
    },
    "validation_data":{
        "systems":            ["./deepmd_data"],
        "batch_size":         "auto",               
        "numb_btch":          1,
        "_comment":           "that's all"
    },
    "numb_steps":             1000,                           
    "seed":                   10,
    "disp_file":              "lcurve.out",
    "disp_freq":              200,
    "save_freq":              10000
    }
  }
```

Modify the type_map to match the atom types in your system.


## Train the model
Run the training process:

```bash
dp train input.json
```

DeepMD-kit generates output files in the working directory, including the trained model (model.ckpt).



## Evaluate the model
Evaluate the trained model use a Python script like this:

```python
```
The test results will include metrics like root mean square error (RMSE) for energies, forces, and virials.

---
## Use the model in LAMMPS

First, export the trained model to a format compatible with LAMMPS:

```bash
dp freeze -o graph.pb
```

The, call the model in LAMMPS Input. An example LAMMPS input script may look like this:

```bash
pair_style    deepmd <path_to_model>/graph.pb
pair_coeff **
```
Run the simulation as usual.

---
## Analyze Results
Perform analysis on the LAMMPS output, such as structural, thermodynamic, or dynamic properties.



---
## Side note for Northwestern University Quest users
Load this module which includes LAMMPS with the DeepMD package pre-installed. The LAMMPS version is 29 Sep 2021 - Update 3.

```bash
module load deepmd-kit/2.1.1
```

---
## Deep Water (example)
This example utilizes DeePMD to coarse grain (CG) the 2005 edition of the TIP4P water model into a single particle centered at the oxygen site. In data preparation, the TIP4P trajectory is coarsen by summing the forces on each molecule and prescribing the new force to the CG particle.





