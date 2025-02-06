import lammps_logfile

# Load LAMMPS log file
logfile = "log.lammps"  # Replace with your actual log file name
log = lammps_logfile.File(logfile)

# Extract values from the log file
temperature = log.get("Temp", run_num=1)
pressure = log.get("Press", run_num=1)
total_energy = log.get("TotEng", run_num=1)
density = log.get("Density", run_num=1)
potential_energy = log.get("PotEng", run_num=1)
kinetic_energy = log.get("KinEng", run_num=1)

# Compute averages
avg_temp = sum(temperature) / len(temperature)
avg_press = sum(pressure) / len(pressure)
avg_toteng = sum(total_energy) / len(total_energy)
avg_density = sum(density) / len(density)
avg_poteng = sum(potential_energy) / len(potential_energy)
avg_kineng = sum(kinetic_energy) / len(kinetic_energy)

# Print results
print(f"Average Temperature: {avg_temp:.3f} K")
print(f"Average Pressure: {avg_press:.3f} atm")
print(f"Average Total Energy: {avg_toteng:.3f} kcal/mol")
print(f"Average Density: {avg_density:.3f} g/cm³")
print(f"Average Potential Energy: {avg_poteng:.3f} kcal/mol")
print(f"Average Kinetic Energy: {avg_kineng:.3f} kcal/mol")
