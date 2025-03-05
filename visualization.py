import pandas as pd
import matplotlib.pyplot as plt
import re

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

# Parse logs
df_vm0 = parse_log('/Users/carlma/cs2620-time/Visualization/Trial1/machine_0.log')
df_vm1 = parse_log('/Users/carlma/cs2620-time/Visualization/Trial1/machine_1.log')
df_vm2 = parse_log('/Users/carlma/cs2620-time/Visualization/Trial1/machine_2.log')

# Plot logical clock progress over system time for all VMs
plt.figure(figsize=(10, 6))
plt.plot(df_vm0["System Time"], df_vm0["Logical Clock"], label="VM 0")
plt.plot(df_vm1["System Time"], df_vm1["Logical Clock"], label="VM 1")
plt.plot(df_vm2["System Time"], df_vm2["Logical Clock"], label="VM 2")
plt.xlabel("System Time (s)")
plt.ylabel("Logical Clock")
plt.title("Logical Clock Progress Over Time")
plt.legend()
plt.grid()
plt.show()


# Function to analyze logical clock jumps
def analyze_clock_jumps(df, vm_id):
    df["Clock Jump"] = df["Logical Clock"].diff().fillna(0)
    avg_jump = df["Clock Jump"].mean()
    max_jump = df["Clock Jump"].max()
    min_jump = df["Clock Jump"].min()
    
    return {
        "VM": vm_id,
        "Avg Clock Jump": avg_jump,
        "Max Clock Jump": max_jump,
        "Min Clock Jump": min_jump
    }

# Analyze all VMs
clock_jump_analysis = [
    analyze_clock_jumps(df_vm0, 0),
    analyze_clock_jumps(df_vm1, 1),
    analyze_clock_jumps(df_vm2, 2)
]

# Convert to DataFrame for better readability
clock_jump_df = pd.DataFrame(clock_jump_analysis)

# Save results to CSV for local viewing
clock_jump_df.to_csv("logical_clock_jump_analysis.csv", index=False)
print("Logical Clock Jump Analysis saved as 'logical_clock_jump_analysis.csv'.")

# Function to analyze logical clock gaps
def analyze_clock_gaps(df, vm_id):
    gaps = df["Logical Clock"].diff().fillna(0)
    large_gaps = (gaps > 2).sum()  # Define a "large gap" as >2
    avg_gap = gaps.mean()
    return {
        "VM": vm_id,
        "Avg Gap Size": avg_gap,
        "Large Gaps Count": large_gaps
    }

# Analyze clock gaps
clock_gap_analysis = [
    analyze_clock_gaps(df_vm0, 0),
    analyze_clock_gaps(df_vm1, 1),
    analyze_clock_gaps(df_vm2, 2)
]

# Convert to DataFrame for better readability
clock_gap_df = pd.DataFrame(clock_gap_analysis)

# Save results to CSV for local viewing
clock_gap_df.to_csv("logical_clock_gap_analysis.csv", index=False)
print("Logical Clock Gap Analysis saved as 'logical_clock_gap_analysis.csv'.")

# Plot clock drift
plt.figure(figsize=(10, 6))
plt.plot(df_vm0["System Time"], df_vm0["Logical Clock"], label="VM 0")
plt.plot(df_vm1["System Time"], df_vm1["Logical Clock"], label="VM 1")
plt.plot(df_vm2["System Time"], df_vm2["Logical Clock"], label="VM 2")
plt.xlabel("System Time (s)")
plt.ylabel("Logical Clock")
plt.title("Logical Clock Drift Over Time")
plt.legend()
plt.grid()
plt.savefig("logical_clock_drift.png")  # Save figure
plt.show()
