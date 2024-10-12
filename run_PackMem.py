import os
import subprocess
import argparse
from datetime import datetime

# Function to parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Run PackMem analysis on multiple PDB files.")
    parser.add_argument("-p", "--pdb_dir", type=str, required=True,
                        help="Directory where the PDB files are stored.")
    parser.add_argument("-t", "--total_frames", type=int, required=True,
                        help="Total number of frames to analyze.")
    parser.add_argument("-P", "--packmem_path", type=str, required=True,
                        help="Directory where PackMem.py and related files are located.")
    parser.add_argument("-prefix", "--prefix", type=str, default="membrane",
                        help="Prefix of the PDB files (default: 'membrane').")
    
    return parser.parse_args()

# Function to run PackMem.py and accumulate results
def run_packmem_analysis(pdbnum, defect_type, pdb_dir, prefix, packmem_path):
    input_pdb = os.path.join(pdb_dir, f"{prefix}{pdbnum}.pdb")
    output_prefix = f"{prefix}{pdbnum}"
    
    vdw_radii_file = os.path.join(packmem_path, "vdw_radii_Charmm.txt")
    param_file = os.path.join(packmem_path, "param_Charmm.txt")
    
    # Define the command to run PackMem.py for a specific defect type
    command = [
        f"{packmem_path}/PackMem.py",
        "-i", input_pdb,
        "-r", vdw_radii_file,
        "-p", param_file,
        "-o", output_prefix,
        "-d", "1.0",  # Distance cutoff
        "-t", defect_type  # Defect type: deep, shallow, or all
    ]
    
    # Run the PackMem.py script for the current frame
    subprocess.run(command)
    
    # Append the results to the corresponding total file for the upper and lower leaflets
    with open(f"{output_prefix}_Up_{defect_type.capitalize()}_result.txt", "r") as up_file:
        with open(f"Total_Up_{prefix}_{defect_type}.txt", "a") as total_up_file:
            total_up_file.write(up_file.read())
    
    with open(f"{output_prefix}_Lo_{defect_type.capitalize()}_result.txt", "r") as lo_file:
        with open(f"Total_Lo_{prefix}_{defect_type}.txt", "a") as total_lo_file:
            total_lo_file.write(lo_file.read())
    
    # Remove the individual result files to save space
    os.remove(f"{output_prefix}_Up_{defect_type.capitalize()}_result.txt")
    os.remove(f"{output_prefix}_Lo_{defect_type.capitalize()}_result.txt")

# Main script
def main():
    args = parse_args()

    # Remove old result files if they exist
    result_files = [
        f"Total_Up_{args.prefix}_deep.txt",
        f"Total_Lo_{args.prefix}_deep.txt",
        f"Total_Up_{args.prefix}_shallow.txt",
        f"Total_Lo_{args.prefix}_shallow.txt",
        f"Total_Up_{args.prefix}_all.txt",
        f"Total_Lo_{args.prefix}_all.txt"
    ]

    for result_file in result_files:
        if os.path.exists(result_file):
            os.remove(result_file)

    # Loop over all frames
    for pdbnum in range(args.total_frames + 1):
        print(f"{datetime.now()}: Running PackMem analysis on {os.path.join(args.pdb_dir, f'{args.prefix}{pdbnum}.pdb')}")
        
        # Run analysis for deep, shallow, and all defect types
        for defect_type in ['deep', 'shallow', 'all']:
            run_packmem_analysis(pdbnum, defect_type, args.pdb_dir, args.prefix, args.packmem_path)

    # After looping through all frames, concatenate results for upper and lower leaflets
    with open(f"Total_{args.prefix}_deep.txt", "w") as total_deep_file:
        for file_part in [f"Total_Up_{args.prefix}_deep.txt", f"Total_Lo_{args.prefix}_deep.txt"]:
            with open(file_part, "r") as part_file:
                total_deep_file.write(part_file.read())

    with open(f"Total_{args.prefix}_shallow.txt", "w") as total_shallow_file:
        for file_part in [f"Total_Up_{args.prefix}_shallow.txt", f"Total_Lo_{args.prefix}_shallow.txt"]:
            with open(file_part, "r") as part_file:
                total_shallow_file.write(part_file.read())

    with open(f"Total_{args.prefix}_all.txt", "w") as total_all_file:
        for file_part in [f"Total_Up_{args.prefix}_all.txt", f"Total_Lo_{args.prefix}_all.txt"]:
            with open(file_part, "r") as part_file:
                total_all_file.write(part_file.read())

    # Clean up individual total files for upper and lower leaflets
    for result_file in result_files:
        os.remove(result_file)

    print("Analysis complete and total files generated.")

if __name__ == "__main__":
    main()
