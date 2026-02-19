import os
import sys
import json
import argparse

def get_root_files(directory, run="2"):
    root_files = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".root"):
                file_split = file.split("_")
                isSample = file_split[-1].split(".")[0] in ["fullsim", "fastsim", "data"]
                isSample *= file_split[-2] in ["mc20a", "mc20d", "mc20e", "mc23a", "mc23b", "mc23c", "mc23d", "mc23e", "mcknown", "data15", "data16", "data17", "data18", "data22", "data23"]
                try:
                    int(file_split[-3])
                    isSample *= True
                except:
                    isSample *= False
                if isSample:
                    sample_name = "_".join(file_split[:-3])
                    if run == "3":
                        fix_samples = [
                            "ttbar_dilep",
                            "ttbar_singlelep",
                            "Zee+jet_CVetoBVeto",
                            "Zmumu+jet_CVetoBVeto",
                            "Zee+jet_CVetoBVeto_light",
                            "Zmumu+jet_CVetoBVeto_light",
                            "VH_ZH_WWlvlv",
                            "VH_ZH_WWlvqq",
                            "VH_WH_mWlep_lvlv",
                            "VH_WH_mWlep_lvqq",
                            "VH_WH_pWlep_lvlv",
                            "VH_WH_pWlep_lvqq",
                            "VH_ZH_WW_lvlv",
                            "VH_ZH_WW_lvqq",
                            "VH_ZH_Zinc_WWlvlv",
                            "VH_ZH_Zinc_WWlvqq",
                            "VH_WH_mWinc_WWlvlv",
                            "VH_WH_mWinc_WWlvqq",
                            "VH_WH_pWinc_WWlvlv",
                            "VH_WH_pWinc_WWlvqq",
                            "VH_ZH_qqZinc_WWlvlv",
                            "VH_ZH_qqZinc_WWlvqq",
                            "ggH_WW_lvlv",
                            "ggH_ZZ_llvv",
                        ]
                        if sample_name in fix_samples:
                            sample_name += "_fix"
                    if sample_name not in root_files:
                        root_files[sample_name] = []
                    root_files[sample_name].append(os.path.join(root, file))
    return root_files

def save_to_json(file_names, output_file):
    with open(output_file, 'w') as f:
        json.dump(file_names, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get root files in a directory and save to JSON.')
    parser.add_argument('--input_dir', help='Input directory containing root files', required=True)
    parser.add_argument('-r', '--run', help='Runs to consider (options "2" or "3")', required=True)
    parser.add_argument('--output_file', help='Output file to save the list of root files', default='sampleslist.json')

    args = parser.parse_args()
    
    if not os.path.isdir(args.input_dir):
        print(f"Directory {args.input_dir} does not exist.")
        sys.exit(1)
    args.input_dir = args.input_dir.rstrip("/")
    root_files = get_root_files(args.input_dir, args.run)
    save_to_json(root_files, args.output_file)
