import numpy as np
import matplotlib.pyplot as plt

# Read data from out.txt
data = np.loadtxt('lcurve.out', skiprows=1)  # Skip header

# Extract columns
steps = data[:, 0]
rmse_val = data[:, 1]
rmse_trn = data[:, 2]
rmse_e_val = data[:, 3]
rmse_e_trn = data[:, 4]
rmse_f_val = data[:, 5]
rmse_f_trn = data[:, 6]
rmse_v_val = data[:, 7]
rmse_v_trn = data[:, 8]


# Plot RMSE values
plt.figure(figsize=(10, 6))

plt.plot(steps, rmse_val, 'o-', label="RMSE Validation")
plt.plot(steps, rmse_trn, 's-', label="RMSE Training")
plt.plot(steps, rmse_e_val, 'd-', label="Energy RMSE Validation")
plt.plot(steps, rmse_e_trn, 'p-', label="Energy RMSE Training")
plt.plot(steps, rmse_f_val, 'x-', label="Force RMSE Validation")
plt.plot(steps, rmse_f_trn, 'v-', label="Force RMSE Training")
plt.plot(steps, rmse_v_val, 'x-', label="Virial RMSE Validation")
plt.plot(steps, rmse_v_trn, 'v-', label="Virial RMSE Training")

plt.xlabel("Steps", fontsize=14)
plt.ylabel("RMSE", fontsize=14)
plt.yscale("log")  # Use log scale for better visualization
plt.legend()
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.title("RMSE Convergence Plot", fontsize=16)
plt.savefig("convergence_plot.png", dpi=300)  # Save the plot as an image()
