import numpy as np
import os
import dpdata
import lammps_logfile







def read_lammps_dump(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    timesteps = []
    box_bounds = []
    coordinates = []
    forces = []
    
    i = 0
    while i < len(lines):
        if "ITEM: TIMESTEP" in lines[i]:
            timestep = int(lines[i + 1].strip())
            timesteps.append(timestep)
            i += 2
        elif "ITEM: NUMBER OF ATOMS" in lines[i]:
            num_atoms = int(lines[i + 1].strip())
            i += 2
        elif "ITEM: BOX BOUNDS" in lines[i]:
            box = []
            for j in range(3):
                box.append([float(x) for x in lines[i + 1 + j].split()[:3]])  # Capture all 9 values for the box bounds
            box_bounds.append(box)
            i += 4
        elif "ITEM: ATOMS" in lines[i]:
            coords = []
            force = []
            for j in range(num_atoms):
                data = lines[i + 1 + j].split()
                coords.append([float(data[3]), float(data[4]), float(data[5])])
                force.append([float(data[6]), float(data[7]), float(data[8])])
            coordinates.append(np.array(coords))
            forces.append(np.array(force))
            i += num_atoms + 1
        else:
            i += 1
    
    # Convert lists to numpy arrays
    return np.array(box_bounds), np.array(coordinates), np.array(forces)



def extract_pe_and_virials_from_log(logfile):
    # Read the LAMMPS log file
    """
    Reads a LAMMPS log file and extracts potential energy (PE) values and
    pressure tensor components. These are combined into frames and returned as
    NumPy arrays. The energy is converted from kcal/mol to eV, and virial 
    is converted from kcal/mol to eV.

    Parameters
    ----------
    logfile : str
        Path to the LAMMPS log file.

    Returns
    -------
    pe_values : ndarray
        1D array of potential energy values in eV.
    pressure_tensor : ndarray
        3D array of shape (n_frames, 3, 3) of virial tensor components in eV.
    """
    
    # Open the LAMMPS log file
    log = lammps_logfile.File(logfile)
    kcal_mol_to_eV = 0.0433641
    atm_to_eV_A3 = 0.00000063247065

    # Extract potential energy (PE) values and pressure tensor components
    pe_values = log.get('PotEng', run_num=1)
    Wxx = log.get('v_Wxx', run_num=1)
    Wyy = log.get('v_Wyy', run_num=1)
    Wzz = log.get('v_Wzz', run_num=1)
    Wxy = log.get('v_Wxy', run_num=1)
    Wxz = log.get('v_Wxz', run_num=1)
    Wyz = log.get('v_Wyz', run_num=1)
    
    # Convert potential energy from kcal/mol to eV
    pe_values_eV = np.array(pe_values) * kcal_mol_to_eV  # kcal/mol to eV
    
    # Convert pressure tensor components from atm to bar
    Wxx_eV = np.array(Wxx) * atm_to_eV_A3
    Wyy_eV = np.array(Wyy) * atm_to_eV_A3
    Wzz_eV = np.array(Wzz) * atm_to_eV_A3
    Wxy_eV = np.array(Wxy) * atm_to_eV_A3
    Wxz_eV = np.array(Wxz) * atm_to_eV_A3
    Wyz_eV = np.array(Wyz) * atm_to_eV_A3
    
    # Combine pressure tensor components into frames
    virial_tensor = np.array([np.array([[Wxx_eV[i], Wxy_eV[i], Wxz_eV[i]],
                                           [Wxy_eV[i], Wyy_eV[i], Wyz_eV[i]],
                                           [Wxz_eV[i], Wyz_eV[i], Wzz_eV[i]]]) 
                               for i in range(len(Wxx_eV))])
    
    return pe_values_eV, virial_tensor






def write_raw_files(prefix, data):
    with open(f"{prefix}.raw", 'w') as f:
        for frame in data:
            flattened = frame.flatten()
            f.write(" ".join(f"{x:.18e}" for x in flattened) + "\n")


def create_directory(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print(f"Directory '{dir_name}' created successfully.")
    else:
        print(f"Directory '{dir_name}' already exists.")






def main():

    ############################
    # Add the forces and energies to data by writing to a dpmd raw file along with the lammps_dump info
    ############################
    # # Example usage:
    filename = "cg_trajectory.lammpstrj"  # Replace with your actual filename
    box_bounds, coordinates, forces = read_lammps_dump(filename)

    PE, virials = extract_pe_and_virials_from_log("../log.lammps")



    temp_data = dpdata.System(filename, fmt='lammps/dump')
    temp_data.to('deepmd/raw', 'dpmd_raw')
    
    
    write_raw_files("./dpmd_raw/force", forces)
    write_raw_files("./dpmd_raw/energy", PE)
    write_raw_files("./dpmd_raw/virial", virials)





    ############################
    # Read all data from dpmd_raw and split into training and testing data
    ############################

    data = dpdata.LabeledSystem('dpmd_raw', type_map=None, fmt='deepmd/raw')
    print('# The data contains %d frames' % len(data))

    # # Randomly choose indices for validation data
    index_validation = np.random.choice(len(data),size=int((len(data))*0.2),replace=False)

    # Other indices are for training data
    index_training = list(set(range(len(data))) - set(index_validation))

    # Create subsystems for training and validation data
    data_training = data.sub_system(index_training)
    data_validation = data.sub_system(index_validation)

    # create_directory("deepmd_data")

    # # Save training data to directory: "training_data"
    data_training.to('deepmd/npy', './deepmd_data/training_data')

    # # Save validation data to directory: "validation_data"
    data_validation.to('deepmd/npy', './deepmd_data/validation_data')






if __name__ == "__main__":
    main()
