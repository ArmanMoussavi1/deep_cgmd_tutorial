# deep_md_tutorial
# DeepMD-kit Tutorial: Learning from a LAMMPS Simulation

This tutorial guides you through training a Deep Potential Molecular Dynamics (DeepMD) model using data from a LAMMPS simulation.

---

## Table of Contents

1. [Installation](#installation)
2. [Generate Training Data](#generate-training-data)
    - [Prepare LAMMPS Simulation](#prepare-lammps-simulation)
    - [Convert LAMMPS Data to DeepMD Format](#convert-lammps-data-to-deepmd-format)
3. [Create a Training Configuration](#create-a-training-configuration)
4. [Train the Model](#train-the-model)
5. [Test the Model](#test-the-model)
6. [Use the Model in LAMMPS](#use-the-model-in-lammps)
7. [Analyze Results](#analyze-results)
8. [Additional Tips](#additional-tips)

---

## 1. Installation

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

## 2. Generate Training Data
To train a model, you'll need trajectory data (atomic positions, forces, energies, etc.) from LAMMPS.

### Prepare LAMMPS Simulation

To create training data for DeepMD-kit, run a LAMMPS simulation that outputs trajectory data, including atomic positions, forces, and energies. Add the following commands to your LAMMPS input script:

```bash
dump 1 all custom 100 dump.lammpstrj id type x y z fx fy fz
thermo_style custom step etotal
```

### Convert LAMMPS Data to DeepMD Format
Use a script (or tools like lmp2dp from DeepMD-kit) to convert the LAMMPS trajectory into DeepMD's training data format (data.json). A Python example to extract relevant data:

```python
from deepmd import DataLoader

# Example script to parse LAMMPS dump into DeepMD format
# Use `dpdata` to simplify the process
import dpdata

data = dpdata.System('dump.lammpstrj', fmt='lammps/dump')
data.to('deepmd/npy', 'deepmd_data')
```
This creates the directory deepmd_data containing atomic positions (coord.npy), forces (force.npy), and energies (energy.npy).

---

## 3. Create a Training Configuration
DeepMD-kit uses a YAML configuration file (input.json) to define the training process. Here's a basic template:

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

---
## 4. Train the Model
Run the training process:

```bash
dp train input.json
```

DeepMD-kit generates output files in the working directory, including the trained model (model.ckpt).

---

## 5. Test the Model
Evaluate the trained model against a test dataset:

```bash
dp test -m ./model.ckpt -s ./test_data
```
The test results will include metrics like root mean square error (RMSE) for energies and forces.

---
## 6. Use the Model in LAMMPS
Integrate the trained model with LAMMPS for production simulations:

### a. Convert the Model for LAMMPS
Export the trained model to a format compatible with LAMMPS:

```bash
dp freeze -o graph.pb
```

### b. Use the Model in LAMMPS Input
In the LAMMPS input file, use pair_style deepmd:

```bash
pair_style    deepmd graph.pb
pair_coeff
```
Run the simulation as usual.

---
## 7. Analyze Results
Perform analysis on the LAMMPS output, such as structural, thermodynamic, or dynamic properties.


module load deepmd-kit/2.1.1

Once loaded, this module includes LAMMPS with the DeepMD package pre-installed. The LAMMPS version is 29 Sep 2021 - Update 3.

