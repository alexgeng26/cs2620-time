import os
import pandas as pd
import re
import matplotlib.pyplot as plt

# Set the base directory for trials
BASE_DIR = "trials"  # Change if your trials are in a different folder

# Load logs into DataFrames
def parse_log(file_path):
    log_data = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(r'(\w+) \| System Time: ([\d.]+) \| Logical Clock: (\d+)', line)
            if match:
                event_type, system_time, logical_clock = match.groups()
                log_data.append({"Event": event_type, "System Time": float(system_time), "Logical Clock": int(logical_clock)})
    return pd.DataFrame(log_data)

# Function to analyze clock jumps
def analyze_clock_jumps(df, vm_id):
    df["Clock Jump"] = df["Logical Clock"].diff().fillna(0)
    return {
        "VM": vm_id,
        "Avg Clock Jump": df["Clock Jump"].mean(),
        "Max Clock Jump": df["Clock Jump"].max(),
        "Min Clock Jump": df["Clock Jump"].min()
    }

# Function to analyze logical clock gaps
def analyze_clock_gaps(df, vm_id):
    gaps = df["Logical Clock"].diff().fillna(0)
    large_gaps = (gaps > 2).sum()  # Arbitrarily defining a "large gap" as >2
    return {
        "VM": vm_id,
        "Avg Gap Size": gaps.mean(),
        "Large Gaps Count": large_gaps
    }

# Loop through each trial folder
for trial_folder in sorted(os.listdir(BASE_DIR)):
    trial_path = os.path.join(BASE_DIR, trial_folder)
    
    if os.path.isdir(trial_path):  # Ensure it's a folder
        print(f"Processing {trial_folder}...")

        # Load logs for each VM
        log_files = {f"machine_{i}.log": None for i in range(3)}
        dataframes = {}

        for file in log_files.keys():
            file_path = os.path.join(trial_path, file)
            if os.path.exists(file_path):
                dataframes[file] = parse_log(file_path)

        # Ensure all VMs have data
        if len(dataframes) == 3:
            df_vm0, df_vm1, df_vm2 = dataframes.values()
            
            # Analyze clock jumps
            clock_jump_analysis = [
                analyze_clock_jumps(df_vm0, 0),
                analyze_clock_jumps(df_vm1, 1),
                analyze_clock_jumps(df_vm2, 2)
            ]
            clock_jump_df = pd.DataFrame(clock_jump_analysis)

            # Analyze logical clock gaps
            clock_gap_analysis = [
                analyze_clock_gaps(df_vm0, 0),
                analyze_clock_gaps(df_vm1, 1),
                analyze_clock_gaps(df_vm2, 2)
            ]
            clock_gap_df = pd.DataFrame(clock_gap_analysis)

            # Save analysis to CSV
            clock_jump_df.to_csv(os.path.join(trial_path, "logical_clock_jump_analysis.csv"), index=False)
            clock_gap_df.to_csv(os.path.join(trial_path, "logical_clock_gap_analysis.csv"), index=False)

            print(f"Saved analysis for {trial_folder}.")

            # Plot logical clock drift
            plt.figure(figsize=(10, 6))
            plt.plot(df_vm0["System Time"], df_vm0["Logical Clock"], label="VM 0")
            plt.plot(df_vm1["System Time"], df_vm1["Logical Clock"], label="VM 1")
            plt.plot(df_vm2["System Time"], df_vm2["Logical Clock"], label="VM 2")
            plt.xlabel("System Time (s)")
            plt.ylabel("Logical Clock")
            plt.title(f"Logical Clock Drift - {trial_folder}")
            plt.legend()
            plt.grid()
            plt.savefig(os.path.join(trial_path, "logical_clock_drift.png"))  # Save figure
            plt.close()  # Close figure to prevent memory leaks

            print(f"Saved clock drift plot for {trial_folder}.")

print("All trials processed successfully.")
