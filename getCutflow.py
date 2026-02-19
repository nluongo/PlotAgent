import os
import ROOT as r
from core.utils import *
from histoDict import *
from PlottingList import *
from core.Sample import *
from core.MC import *
from core.Data import *
from ROOT import gROOT, gStyle
from core.parse_config import load_and_process_yaml

histoDict = PlottingDict()
sampleDict = SampleDict()
selectionDict = SelectionDict()
SignalDict = SignalDict()

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()
    if iteration == total:
        print()

#### PLOT 1D
def main(config={}, 
        UNBLIND=False, 
        mcOnly=False, 
        include_ratio=False, 
        logOn=False, 
        dosignal=False):

    user_name = config["user_name"]
    sampleDict = restructureSampleMap(sampleDict)

    # Create the data sample
    if not mcOnly:
        data = {}
        for i, campaign in enumerate(["15", "16", "17", "18"]):
            if (campaign.startswith("15")):
                file_name = f"{user_name}.data{campaign}_13TeV.periodAllYear.grp{campaign}_v01_p6255.root"
            else:
                file_name = f"{user_name}.data{campaign}_13TeV.periodAllYear.grp{campaign}_v01_p6266.root"
            print(f"Loading file: {file_name}...")
            data_sample = Data("data", config["cutflow_path"]+file_name)
            data_sample.load_cutflows()
            data[campaign] = data_sample
            print_progress_bar(i+1, 4, prefix='Loading data files:', suffix='Complete', length=50)

        # Create the MC samples	
    MC.set_sampleStackNames(config["samplesToStack"])
    MC.set_sampleSignalNames(config["signalName"])
    MC.set_doSignal(dosignal)
    mc = {}
    for i, mc_name in enumerate(config["samplesToStack"]):
        if (mc_name.startswith("bbWW") or mc_name.startswith("bbZZ") or mc_name.startswith("bbtt")) and not mc_name.endswith("SM"):
            for campaign in ["ares", "dres", "eres"]:
                file_name = f"{user_name}.{sample_map[mc_name]}_{campaign_map[campaign]}.root"
                mc_sample = MC(mc_name, sampleDict[mc_name], config["cutflow_path"]+file_name)
                mc_sample.load_cutflows()
                mc[mc_name+f"_{campaign}"] = mc_sample
        elif (mc_name.startswith("bbWW") or mc_name.startswith("bbZZ") or mc_name.startswith("bbtt")) and mc_name.endswith("SM"):
            for campaign in ["a", "e"]:
                file_name = f"{user_name}.{sample_map[mc_name]}_{campaign_map[campaign]}.root"
                mc_sample = MC(mc_name, sampleDict[mc_name], config["cutflow_path"]+file_name)
                mc_sample.load_cutflows()
                mc[mc_name+f"_{campaign}"] = mc_sample
        else:
            for campaign in ["a", "d", "e"]:
                file_name = f"{user_name}.{sample_map[mc_name]}_{campaign_map[campaign]}.root"
                mc_sample = MC(mc_name, sampleDict[mc_name], config["cutflow_path"]+file_name)
                mc_sample.load_cutflows()
                mc[mc_name+f"_{campaign}"] = mc_sample
        print_progress_bar(i+1, len(config["samplesToStack"]), prefix='Loading MC files:', suffix=f'Completed: {mc_name}', length=50)

    # Cutflows
    cutflow = {}
    cutflow['StandardFlow'] = {}
    cutflow['AbsEff'] = {}
    cutflow['RelEff'] = {}
    for flow_type in cutflow:
        cutflow[flow_type]['Signal'] = {}
        cutflow[flow_type]['Background'] = {}
        cutflow[flow_type]['Data'] = {}
    for i, sample_name in enumerate(mc):
        sample = mc[sample_name]
        if i == 0:
            ncuts = sample.events_passed.GetNbinsX()
            # Get only the preselection cuts
            cut_names = [sample.events_passed.GetXaxis().GetLabels().At(i).GetName() for i in range(ncuts)][0:5]
            signal_cutflow = sample.events_passed.Clone()
            background_cutflow = sample.events_passed.Clone()
            data_cutflow = sample.events_passed.Clone()
            for i in range(ncuts):
                signal_cutflow.SetBinContent(i, 0)
                background_cutflow.SetBinContent(i, 0)
                data_cutflow.SetBinContent(i, 0)
        mc_cutflow = sample.events_passed.Clone()
        passed_histogram = sample.standard_cutflow.GetPassedHistogram()
        for i in range(ncuts):
            mc_cutflow.SetBinContent(i, passed_histogram.GetBinContent(i))
        if 'bbZZ' in sample_name or 'bbWW' in sample_name or 'bbtt' in sample_name:
            signal_cutflow.Add(mc_cutflow)
        else:
            background_cutflow.Add(mc_cutflow)
    for i, sample_name in enumerate(data):
        sample = data[sample_name]
        data_cutflow = sample.events_passed.Clone()
        passed_histogram = sample.standard_cutflow.GetPassedHistogram()
        for i in range(ncuts):
            data_cutflow.SetBinContent(i, passed_histogram.GetBinContent(i))

    for i, cut_name in enumerate(cut_names):
       cutflow['StandardFlow']['Signal'][cut_name] = signal_cutflow.GetBinContent(i+1)
       cutflow['StandardFlow']['Background'][cut_name] = background_cutflow.GetBinContent(i+1)
       cutflow['StandardFlow']['Data'][cut_name] = data_cutflow.GetBinContent(i+1)

    tex_path = config["output_path"] + 'cutflow.tex'
    tex_out = open(tex_path, 'w')

    header = tex_header(3)
    tex_out.write(header)

    top_line = 'Cut & Signal & Background & Data \\\\ \hline\n'
    tex_out.write(top_line)
    
    cut_names_tex = {
        'PASS_EVENT_CLEANING_AND_OR_OTHER_FILTERS':'Event cleaning and quality checks',
        'EXACTLY_TWO_LEPTONS':'$N_{lep}$ = 2',
        'PASS_TRIGGER':'Passed trigger',
        'TWO_OPPOSITE_CHARGE_LEPTONS':'Opposite-charge leptons',
        'EXACTLY_TWO_B_JETS':'$N_{bjet}$ = 2'
        }


    standard = cutflow['StandardFlow']
    for cut_name in cut_names:
        cut_name_tex = cut_name.replace('_', '\_')
        line = f"{cut_names_tex[cut_name]} & {standard['Signal'][cut_name]} & {standard['Background'][cut_name]} & {standard['Data'][cut_name]} \\\\\n"
        tex_out.write(line)

    footer = tex_footer()
    tex_out.write(footer)

def argument_parser():
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", help="Path to the config file", default="config.yaml")
    parser.add_argument("-m", "--mcOnly", help="", action="store_true", default=False)
    parser.add_argument("-r", "--include_ratio", help="", action="store_true", default=False)
    parser.add_argument("-s", "--dosignal", help="", action="store_true", default=False)
    parser.add_argument("-l", "--logOn", help="", action="store_true", default=False)
    parser.add_argument("-t", "--twoDim", help="",action="store_true",default=False)
    #parser.add_argument("-p", "--plotDump", help="Option for making plots in different formats.", action="store_true", default=False) 
    parser.add_argument("-UB", "--UNBLIND", help="",action="store_true",default=False) 
    return parser.parse_args()

if __name__ == "__main__":

    # Adding an argument parser, which we might want to use  a
    from argparse import ArgumentParser

    options = argument_parser()

    # Load the config file
    config = load_and_process_yaml(options.config)["makePlot"]

    # Input and output directories
    if not os.path.exists(config["output_path"]):
        os.makedirs(config["output_path"])
        print("The output directory did not exist, I have just created one: ", config["output_path"])

    # Defining dictionary to be passed to the main function
    # skip twoDim option
    option_dict = {k: v for k, v in vars(options).items() if (v is not None) and (k != "twoDim")}
    option_dict["config"] = config

    r.EnableImplicitMT()

    # if --twoDim true run main2D
    main(**option_dict)

