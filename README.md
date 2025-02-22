# deep_cgmd_tutorial
# DeePMD-kit Tutorial: Learning from a LAMMPS Simulation with an example (Deep Water)

This tutorial guides you through training and using a Deep Potential Molecular Dynamics (DeePMD) model. The example, Deep Water, uses LAMMPS to simulate the 2005 edition of the TIP4P water model. The output of the fine-grained simulation is coarse-grained (CG) during the data preparation. Finally the Deep Water model contains a single particle per molecule.

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

## Installation Guide for DeePMD-kit and LAMMPS
*in progress*




### Install Miniconda
```bash
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh
```
### Set Up Conda Environment
```bash
conda create -n deepmd python=3.9.16
conda init
source ~/.bashrc
conda activate deepmd
python3 -m pip install tensorflow==2.15.0
pip install deepmd-kit[gpu,cu12,lmp,ipi]
```
### Install OpenMPI
```bash
wget https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.5.tar.gz
tar -xvzf openmpi-4.1.5.tar.gz
cd openmpi-4.1.5
mkdir -p $HOME/local/openmpi
./configure --prefix=$HOME/local/openmpi
make -j$(nproc)
make install
```

Add these lines to your .bashrc:
```bash
export PATH=$HOME/local/openmpi/bin:$PATH
export LD_LIBRARY_PATH=$HOME/local/openmpi/lib:$LD_LIBRARY_PATH
export MPI_HOME=$HOME/local/openmpi
```
Reload bash:
```bash
source ~/.bashrc
```
Reload Environement:
```bash
conda activate deepmd
```
### Install DeePMD-kit
```bash
mkdir lammps_deepmd && cd lammps_deepmd
git clone --depth 1 --branch v3.0.1 https://github.com/deepmodeling/deepmd-kit.git
cd ./deepmd-kit/source && mkdir -p build && cd build && cmake -DENABLE_TENSORFLOW=TRUE -DUSE_TF_PYTHON_LIBS=TRUE -DCMAKE_INSTALL_PREFIX=$HOME/local .. && cmake --build . --parallel 4 && make install && make lammps
cd ../../..
```
Add DeePMD to Environment
```bash
export DeePMD_DIR=$HOME/local/lib/cmake/DeePMD
export CMAKE_PREFIX_PATH=$HOME/local:$CMAKE_PREFIX_PATH
```
Reload bash:
```bash
source ~/.bashrc
```
Reload Environement:
```bash
conda activate deepmd
```
### Install LAMMPS with DeePMD-kit
```bash
mkdir -p ./lammps-src
cd ./lammps-src
wget https://github.com/lammps/lammps/archive/stable_29Aug2024_update1.tar.gz && tar xf stable_29Aug2024_update1.tar.gz
mkdir -p ./lammps-stable_29Aug2024_update1/build/
cd ./lammps-stable_29Aug2024_update1/build/
```
Locate DeePMD-kit Path
```bash
find ~ -type d -name "deepmd-kit"
```
This will return a `<path_to_deepmd-kit>`. Add it to LAMMPS CMake:
```bash
echo "include(<path_to_deepmd-kit>/source/lmp/builtin.cmake)" >> ../cmake/CMakeLists.txt
```
Build LAMMPS
```bash
cmake \
    -D CMAKE_INSTALL_PREFIX=$python_venv_path \
    -D LAMMPS_INSTALL_RPATH=ON \
    -D BUILD_SHARED_LIBS=yes \
    -D PKG_EXTRA-FIX=ON \
    -D PKG_EXTRA-PAIR=ON \
    -D PKG_MISC=ON \
    -D PKG_PYTHON=ON \
    -D PKG_KSPACE=ON \
    -D PKG_ML-SNAP=ON \
    -D PKG_MANYBODY=ON \
    -D PKG_GPU=ON \
    -D GPU_API=CUDA \
    -D GPU_PREC=mixed \
    -D PKG_MOLECULE=yes -D PKG_RIGID=yes -D PKG_MC=yes -D PKG_USER-COLVARS=yes -D DOWNLOAD_EIGEN3=yes -D PKG_PLUGIN=ON \
    -DCMAKE_PREFIX_PATH=$python_venv_path ../cmake
```
Compile and install:
```bash
make -j4 install DESTDIR=$HOME/.local
cd ../../..
```




---
## Generate Training Data
To train a model, you'll need trajectory data (box dimensions, atomic positions, forces, energies, and virials). [Fine water](./deep_water/fine_water/fine_water.inp)

### Prepare LAMMPS Simulation for training data

To create training data for DeePMD-kit, run a LAMMPS simulation that outputs trajectory data, including atomic positions and per-atom forces. 
```bash
dump 1 all custom 100 dump.lammpstrj id type x y z fx fy fz
```

Manually compute the virial tensor (symmetric) by computing the virial pressure, excluding the kinetic energy term, and multiplying by the system volume:

```bash
compute virial all pressure NULL virial

variable Wxx equal c_virial[1]*vol
variable Wxy equal c_virial[2]*vol
variable Wxz equal c_virial[3]*vol
variable Wyy equal c_virial[4]*vol
variable Wyz equal c_virial[5]*vol
variable Wzz equal c_virial[6]*vol
```




Using the thermo_style command, output the potential energy:

```bash
thermo_style custom step pe v_Wxx v_Wyy v_Wzz v_Wxy v_Wxz v_Wyz
```

### Prepare data in a suitable format for DeePMD
Use a script (or packages like dpdata) to convert the simulation outputs into DeePMD's training data format. For simulations in LAMMPS, a convenient method is to first convert all required data to the deepmd/raw format. A sample Python script may look like this:

```python
def write_raw_files(prefix, data):
    with open(f"{prefix}.raw", 'w') as f:
        for frame in data:
            flattened = frame.flatten()
            f.write(" ".join(f"{x:.18e}" for x in flattened) + "\n")
```
[CG trajectory](./deep_water/prep_data/cg_trajectory.py)


Then use dpdata to read in the data in the deepmd/raw format, and prepare it for training. A sample Python script may look like this:

```python
import dpdata
data = dpdata.LabeledSystem('dpmd_raw', type_map=None, fmt='deepmd/raw')
print('# The data contains %d frames' % len(data))
data.to('deepmd/npy', './deepmd_data')
```
[Prep data](./deep_water/prep_data/prep_data.py)

---

## DeePMD Model

## Create a model to train
DeePMD-kit uses a JavaScript Object Notation configuration file (input.json) to define the training process. Here's a basic template:

```json
{
  "model": {
    "descriptor": {
      "type": "se_e2_a",
      "rcut": 6.0,
      "sel": "auto",
      "neuron": [150, 100, 50],
      "resnet_dt": false,
      "axis_neuron": 32,
      "seed": 1
    },
    "fitting_net": {
      "neuron": [200, 150, 75],
      "resnet_dt": true,
      "seed": 1
    }
  },
  "learning_rate": {
    "type": "exp",
    "decay_steps": 100,
    "start_lr": 0.001,
    "stop_lr": 3.51e-8
  },
  "loss": {
    "type": "ener",
    "start_pref_e": 0.02,
    "limit_pref_e": 1,
    "start_pref_f": 500,
    "limit_pref_f": 1,
    "start_pref_v": 5,
    "limit_pref_v": 1
  },
  "training": {
    "training_data": {
      "systems": ["./training_data"],
      "batch_size": "auto"
    },
    "validation_data": {
      "systems": ["./validation_data"],
      "batch_size": "auto",
      "numb_btch": 1
    },
    "numb_steps": 5000,
    "seed": 1,
    "disp_file": "lcurve.out",
    "disp_freq": 200,
    "save_freq": 10000
  }
}
```

[Deep model](./deep_water/train_model/input.json)


Modify the to match your system.


## Train the model
Run the training process:

```bash
dp train input.json
```

DeePMD-kit generates output files in the working directory, including the trained model.



## Evaluate the model
Evaluate the trained model use a Python script like [Evaluate](./deep_water/train_model/plot.py)
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
pair_coeff * *
```
Run the simulation as usual. [Deep Water](./deep_water/deep_water_sim/deep_water.inp)


---
## Analyze Results
Perform analysis on the LAMMPS output, such as structural, thermodynamic, or dynamic properties.



---
## Side note for Northwestern University Quest users
Load this module which includes LAMMPS with the DeePMD package pre-installed. The LAMMPS version is 29 Sep 2021 - Update 3.

```bash
module load deepmd-kit/2.1.1
```

---
## Deep Water (example)
This example utilizes DeePMD to coarse grain (CG) the 2005 edition of the TIP4P water model into a single particle centered at the oxygen site. In data preparation, the TIP4P trajectory is coarsen by summing the forces on each molecule and prescribing the new force to the CG particle.





