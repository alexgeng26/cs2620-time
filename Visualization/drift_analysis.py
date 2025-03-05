# Reload logs into DataFrames for fresh analysis
df_vm0 = parse_log('/mnt/data/machine_0.log')
df_vm1 = parse_log('/mnt/data/machine_1.log')
df_vm2 = parse_log('/mnt/data/machine_2.log')

# Interpolating logical clocks to align with VM0 system time for drift analysis
def interpolate_logical_clocks_with_vm0(ref_df, compare_df, label):
    """Interpolates logical clock values for a VM to match VM0 system times."""
    merged_df = pd.DataFrame({"System Time": ref_df["System Time"]})
    merged_df = pd.merge_asof(merged_df, compare_df[["System Time", "Logical Clock"]],
                              on="System Time", direction="nearest")
    merged_df.rename(columns={"Logical Clock": f"Logical Clock_{label}"}, inplace=True)
    return merged_df

# Interpolate logical clocks for VM 1 and VM 2 against VM 0
drift_vm1 = interpolate_logical_clocks_with_vm0(df_vm0, df_vm1, "VM1")
drift_vm2 = interpolate_logical_clocks_with_vm0(df_vm0, df_vm2, "VM2")

# Merge all drift data into a single DataFrame
drift_comparison_df = df_vm0[["System Time", "Logical Clock"]].rename(columns={"Logical Clock": "Logical Clock_VM0"})
drift_comparison_df = pd.merge(drift_comparison_df, drift_vm1, on="System Time", how="left")
drift_comparison_df = pd.merge(drift_comparison_df, drift_vm2, on="System Time", how="left")

# Compute drift values
drift_comparison_df["Drift_VM0_VM1"] = abs(drift_comparison_df["Logical Clock_VM0"] - drift_comparison_df["Logical Clock_VM1"])
drift_comparison_df["Drift_VM0_VM2"] = abs(drift_comparison_df["Logical Clock_VM0"] - drift_comparison_df["Logical Clock_VM2"])

# Plot drift over time
plt.figure(figsize=(10, 6))
plt.plot(drift_comparison_df["System Time"], drift_comparison_df["Drift_VM0_VM1"], label="Drift VM0 - VM1")
plt.plot(drift_comparison_df["System Time"], drift_comparison_df["Drift_VM0_VM2"], label="Drift VM0 - VM2")
plt.xlabel("System Time (s)")
plt.ylabel("Logical Clock Drift")
plt.title("Logical Clock Drift Compared to VM0 (Fresh Analysis)")
plt.legend()
plt.grid()
plt.show()

# Compute summary statistics for logical clock drift
drift_summary = pd.DataFrame({
    "VM Pair": ["VM0 vs VM1", "VM0 vs VM2"],
    "Avg Drift": [drift_comparison_df["Drift_VM0_VM1"].mean(), drift_comparison_df["Drift_VM0_VM2"].mean()],
    "Max Drift": [drift_comparison_df["Drift_VM0_VM1"].max(), drift_comparison_df["Drift_VM0_VM2"].max()],
    "Min Drift": [drift_comparison_df["Drift_VM0_VM1"].min(), drift_comparison_df["Drift_VM0_VM2"].min()]
})

# Display drift data
tools.display_dataframe_to_user(name="Updated Logical Clock Drift Compared to VM0", dataframe=drift_summary)
