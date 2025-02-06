# Written by Arman Moussavi
import numpy as np

# Input and output filenames
input_filename = '../fine_water/tip4p_training_data.lammpstrj'
output_filename = 'cg_trajectory.lammpstrj'

def read_trajectory(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return lines



def process_trajectory(lines):
    kcal_to_ev = 0.0433641  # Conversion factor from kcal/mol to eV
    
    new_lines = []
    timestep = None
    num_atoms = None
    molecule_forces = {}
    molecule_stress = {}
    molecule_atom_count = {}  # Tracks the number of atoms per molecule
    molecule_energy = {}  # Tracks the total energy per molecule
    atom_mapping = {}  # Maps old atom IDs to new atom IDs
    current_new_id = 1  # Counter for new atom IDs

    for i, line in enumerate(lines):
        # Parse timestep
        if line.startswith('ITEM: TIMESTEP'):
            timestep = int(lines[i + 1].strip())
            new_lines.append(f"ITEM: TIMESTEP\n{timestep}\n")

        # Parse number of atoms
        elif line.startswith('ITEM: NUMBER OF ATOMS'):
            num_atoms = int(lines[i + 1].strip())
            num_coarse_atoms = num_atoms // 3  # One atom per molecule
            new_lines.append(f"ITEM: NUMBER OF ATOMS\n{num_coarse_atoms}\n")

        # Parse box bounds
        elif line.startswith('ITEM: BOX BOUNDS'):
            new_lines.append(line)
            new_lines.extend(lines[i + 1:i + 4])

        # Process atoms
        elif line.startswith('ITEM: ATOMS'):
            new_lines.append(line)  # Write header line
            atom_data = lines[i + 1:i + 1 + num_atoms]
            molecule_forces.clear()
            molecule_atom_count.clear()
            
            for atom_line in atom_data:
                # Parse atom info
                data = atom_line.split()
                atom_id = int(data[0])
                mol_id = int(data[1])
                atom_type = int(data[2])
                x, y, z = float(data[3]), float(data[4]), float(data[5])
                fx, fy, fz = float(data[6]), float(data[7]), float(data[8])


                # Convert forces to eV/Å
                fx *= kcal_to_ev
                fy *= kcal_to_ev
                fz *= kcal_to_ev

                # Sum the forces, stresses, and track total energy per molecule
                if mol_id not in molecule_forces:
                    molecule_forces[mol_id] = {'fx': 0.0, 'fy': 0.0, 'fz': 0.0, 'coords': (x, y, z), 'atom_id': atom_id}
                    molecule_atom_count[mol_id] = 0  # Initialize atom count

                molecule_forces[mol_id]['fx'] += fx
                molecule_forces[mol_id]['fy'] += fy
                molecule_forces[mol_id]['fz'] += fz
                molecule_atom_count[mol_id] += 1


                # Keep the first atom's coordinates and image flags for each molecule
                if atom_type == 1:  # Assuming atom type 1 is the oxygen atom
                    molecule_forces[mol_id]['coords'] = (x, y, z)
                    molecule_forces[mol_id]['atom_id'] = atom_id

            # Assign new IDs to molecules and compute summed forces and stresses
            for mol_id, data in molecule_forces.items():
                old_id = data['atom_id']
                if old_id not in atom_mapping:
                    atom_mapping[old_id] = current_new_id
                    current_new_id += 1

                new_id = atom_mapping[old_id]
                x, y, z = data['coords']

                # Get summed forces
                fx = data['fx']
                fy = data['fy']
                fz = data['fz']
                

                new_lines.append(f"{new_id} {mol_id} 1 {x} {y} {z} {fx} {fy} {fz}\n")

    return new_lines





def write_trajectory(lines, filename):
    with open(filename, 'w') as f:
        f.writelines(lines)

def main():
    # Read the trajectory
    lines = read_trajectory(input_filename)

    # Process the trajectory and sum the forces
    new_lines = process_trajectory(lines)

    # Write the new trajectory to output file
    write_trajectory(new_lines, output_filename)

    print(f"Coarse-grained trajectory written to {output_filename}")

if __name__ == "__main__":
    main()
