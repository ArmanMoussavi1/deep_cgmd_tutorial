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

## Installation

Install DeepMD-kit and its dependencies:

```bash
conda create -n deepmd python=3.8
conda activate deepmd
pip install deepmd-kit
```

Verify the installation by running the following command:

```bash
dp -h


## Generate Training Data

### Prepare LAMMPS Simulation

To create training data for DeepMD-kit, run a LAMMPS simulation that outputs trajectory data, including atomic positions, forces, and energies. Add the following commands to your LAMMPS input script:

```bash
dump 1 all custom 100 dump.lammpstrj id type x y z fx fy fz
thermo_style custom step etotal


2. Generate Training Data
To train a model, you'll need trajectory data (atomic positions, forces, energies, etc.) from LAMMPS.

a. Prepare LAMMPS Simulation
Run a LAMMPS simulation with a potential (e.g., EAM, LJ) and save the trajectory in a dump file (e.g., dump.lammpstrj). Also, output the per-atom forces and total system energy.




```bash
dump 1 all custom 100 dump.lammpstrj id type x y z fx fy fz
thermo_style custom step etotal


b. Convert LAMMPS Data to DeepMD Format
Use a script (or tools like lmp2dp from DeepMD-kit) to convert the LAMMPS trajectory into DeepMD's training data format (data.json). A Python example to extract relevant data:

```python
Copy code
from deepmd import DataLoader

# Example script to parse LAMMPS dump into DeepMD format
# Use `dpdata` to simplify the process
import dpdata

data = dpdata.System('dump.lammpstrj', fmt='lammps/dump')
data.to('deepmd/npy', 'deepmd_data')
This creates the directory deepmd_data containing atomic positions (coord.npy), forces (force.npy), and energies (energy.npy).



3. Create a Training Configuration
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

  
