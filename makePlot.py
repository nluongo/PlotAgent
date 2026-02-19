import os
import ROOT as r
import json
from core.utils import *
from histoDict import *
from PlottingList import *
from core.Sample import *
from core.MC import *
from core.Data import *
from ROOT import gROOT, gStyle
from array import array
from core.parse_config import load_and_process_yaml

r.gROOT.LoadMacro("./AtlasStyle/AtlasStyle.C")
r.gROOT.LoadMacro("./AtlasStyle/AtlasLabels.C")
r.gROOT.LoadMacro("./AtlasStyle/AtlasUtils.C")

colors = gROOT.GetColor(1)

r.SetAtlasStyle()
r.gDebug = 0
r.EnableImplicitMT()

r.gROOT.SetBatch(1)
r.gStyle.SetPalette(56)

histoDict = PlottingDict()
sampleDicts = {
    'run2': SampleDict_run2(),
    'run3': SampleDict_run3()
    }

mc_campaigns_run2 = ['a', 'd', 'e']
mc_campaigns_run3 = ['a', 'd']
mc_campaigns_res_run2 = [campaign+'res' for campaign in mc_campaigns_run2]
mc_campaigns_res_run3 = [campaign+'res' for campaign in mc_campaigns_run3]
mc_campaigns = {
    'run2': mc_campaigns_run2,
    'run3': mc_campaigns_run3
    }

mc_campaigns_res = {
    'run2': mc_campaigns_res_run2,
    'run3': mc_campaigns_res_run3
    }

run_coms = {
    "2": "13",
    "3": "13.6",
    "23": "13,13.6"
    }

selectionDict = SelectionDict()
SignalDict = SignalDict()
cutPerSampleDict = CutPerSampleDict()
cutPerStackDict = CutPerStackDict()

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()
    if iteration == total:
        print()

#### PLOT 1D
def main1D(config={},
                   UNBLIND=False,
                   mcOnly=False,
                   include_ratio=False,
                   logOn=False,
                   dosignal=False,
                   yields=False,
                   old_yields=False,
                   noPlots=False,
                   runs="2"):
    
    if config["ttbar_reweighting_file_Run2"] or config["ttbar_reweighting_file_Run3"]:
        apply_ttbar_reweighting = True
    else:
        apply_ttbar_reweighting = False

    if config["do_ttbar_reweighting_calc"] and apply_ttbar_reweighting:
        print("ERROR: Currently the data ttbar reweighting calculation cannot be run when an data ttbar reweighting file is provided. Please remove the file from the config.")
        return 0

    if config["do_ttbar_reweighting_calc"] or apply_ttbar_reweighting:
        nJets = 15

    if config["do_ttbar_reweighting_calc"] and (mcOnly or not yields):
        print("WARNING: Data ttbar reweighting cannot run in MC only mode or with yields enabled. Forcing yields and disabling MC only mode.")
        yields = True
        mcOnly = False

    user_name = config["user_name"]

    run2_path = config["input_path_run2"]
    run3_path = config["input_path_run3"]
    input_paths = {
        'run2':config["input_path_run2"],
        'run3':config["input_path_run3"]
    }

    output_path = config["output_path"]+f"/run{runs}/"

    if runs == "2":
        samples_to_stack = {
            'run2':config["samplesToStack_run2"],
        }
    elif runs == "3":
        samples_to_stack = {
            'run3':config["samplesToStack_run3"],
        }
    elif runs == "23":
        samples_to_stack = {
            'run2':config["samplesToStack_run2"],
            'run3':config["samplesToStack_run3"],
        }

    com = run_coms[runs]

    campaign_maps = {
        'run2':campaign_map_run2,
        'run3':campaign_map_run3,
    }

    sample_maps = {
        'run2':sample_map_run2,
        'run3':sample_map_run3,
    }
    
    if config["fastframes_input"]:
        if runs == "2":
            sample_map = json.load(open(config["sampleslist_path_Run2"]))
        elif runs == "3":
            sample_map = json.load(open(config["sampleslist_path_Run3"]))
        elif runs == "23":
            sample_map = json.load(open(config["sampleslist_path_Run2"]))
            sample_map_Run3 = json.load(open(config["sampleslist_path_Run3"]))
            for key in sample_map_Run3:
                if key in sample_map:
                    sample_map[key] += sample_map_Run3[key]
                else:
                    sample_map[key] = sample_map_Run3[key]

    r.gStyle.SetPadLeftMargin(0.15)
    r.gStyle.SetPadRightMargin(0.10)
    r.gStyle.SetPadBottomMargin(0.15)
    r.gStyle.SetPadTopMargin(0.05)
    r.gStyle.SetNumberContours(999)

    if UNBLIND:
        print('WARNING: You have unblinded the analysis! Are you sure you want to do this?')
        answer = input('Type "yes" to continue: ')
        if answer != 'yes':
            return

    if "customCutPerStack" in config:
        for customCut in config["customCutPerStack"]:
            cutPerStackDict[customCut] = config["customCutPerStack"][customCut]
    for run_num in samples_to_stack.keys():
        sampleDict = sampleDicts[run_num]
        for stack_cut in cutPerStackDict:
            cutPerSampleDict[stack_cut] = {
                'samples': [],
                'cuts': cutPerStackDict[stack_cut]['cuts']
            }
            for stack in cutPerStackDict[stack_cut]['stacks']:
                cutPerSampleDict[stack_cut]['samples'] += sampleDict[stack]['samples']
        sampleDicts[run_num] = restructureSampleMap(sampleDict)

    if "customCutPerSample" in config:
        for customCut in config["customCutPerSample"]:
            cutPerSampleDict[customCut] = config["customCutPerSample"][customCut]
        

    if "customSelection" in config:
        for selection in config["customSelection"]:
            selectionDict[selection] = config["customSelection"][selection]

    if "customHists" in config:
        for hist in config["customHists"]:
            histoDict[hist] = config["customHists"][hist]
    
    MC.set_sampleDict(sampleDicts)
    selections = config["selectionToPlot"]

    # Initialize class members in Sample for yields
    if yields:
        Sample.init_yields()

    # Create the data sample
    if not mcOnly:
        run2_campaigns = ["15", "16", "17", "18"]
        run2_lumi = 140
        run3_campaigns = ["22", "23"]
        run3_lumi = 58.6

        if runs == "2":
            data_campaigns = run2_campaigns
            lumi = run2_lumi
        elif runs == "3":
            data_campaigns = run3_campaigns
            lumi = run3_lumi
        elif runs == "23":
            data_campaigns = run2_campaigns + run3_campaigns
            lumi = run2_lumi + run3_lumi

        data = {}
        if config["fastframes_input"]:
            for i, file_path in enumerate(sample_map["data"]):
                campaign = file_path.split("/")[-1].split("_")[-2]
                data[campaign] = Data("data", file_path)
                print_progress_bar(i+1, len(sample_map["data"]), prefix='Loading data files:', suffix='Complete\n', length=50)
        else:
            for i, campaign in enumerate(data_campaigns):
                if campaign.startswith("2"):
                    file_name = f"{user_name}.data{campaign}_p6269.root"
                    input_path = run3_path
                elif (campaign.startswith("15")):
                    file_name = f"{user_name}.data{campaign}_p6255.root"
                    input_path = run2_path
                else:
                    file_name = f"{user_name}.data{campaign}_p6266.root"
                    input_path = run2_path
                print(f"Loading file: {file_name}...")
                data[campaign] = Data("data", input_path+file_name)
                print_progress_bar(i+1, len(data_campaigns), prefix='Loading data files:', suffix='Complete\n', length=50)

    if "scale_factor" in config:
        MC.set_scale_formula(config["scale_factor"])
    MC.set_weight_formula(config["weight_factor"])
    MC.set_sampleStackNames(samples_to_stack)
    MC.set_sampleSignalNames(config["signalName"])
    MC.set_doSignal(dosignal)

    if apply_ttbar_reweighting:
        print("Loading data ttbar reweighting file...")
        if runs == "2":
            MC.setup_ttbar_weights(config["ttbar_reweighting_file_Run2"], nJets=nJets)
        elif runs == "3":
            MC.setup_ttbar_weights(config["ttbar_reweighting_file_Run3"], nJets=nJets)

    mc = {}

    for run_num, run_mc in samples_to_stack.items():
        sampleDict = sampleDicts[run_num]
        if config["fastframes_input"]:
            for i, mc_name in enumerate(run_mc):
                if mc_name not in sample_map:
                    print(f"Sample {mc_name} not found in the sample map")
                    continue
                for file_path in sample_map[mc_name]:
                    campaign = file_path.split("/")[-1].split("_")[-2]
                    print(f"Loading file: {file_path}")
                    mc[mc_name+f"_{campaign}"] = MC(mc_name, sampleDict[mc_name], file_path)
                print_progress_bar(i+1, len(run_mc), prefix='Loading MC files:', suffix=f'Completed: {mc_name}', length=50)
        else:
            campaign_map = campaign_maps[run_num]
            sample_map = sample_maps[run_num]
            input_path = input_paths[run_num]
            campaign_list = mc_campaigns[run_num]
            campaign_res_list = mc_campaigns_res[run_num]
            for i, mc_name in enumerate(run_mc):
                print('mc_name: ',mc_name)
                if (mc_name.startswith("bbWW") or mc_name.startswith("bbZZ") or mc_name.startswith("bbtt")) and not mc_name.endswith("SM"):
                    for campaign in campaign_res_list:
                        file_name = f"{user_name}.{sample_map[mc_name]}_{campaign_map[campaign]}.root"
                        print(f"Loading file: {file_name}")
                        mc[mc_name+f"_{campaign}"] = MC(mc_name, sampleDict[mc_name], input_path+file_name, signal=1)
                elif (mc_name.startswith("bbWW") or mc_name.startswith("bbZZ") or mc_name.startswith("bbtt")) and mc_name.endswith("SM"):
                    for campaign in ["a", "e"]:
                        file_name = f"{user_name}.{sample_map[mc_name]}_{campaign_map[campaign]}.root"
                        print(f"Loading file: {file_name}...")
                        mc[mc_name+f"_{campaign}"] = MC(mc_name, sampleDict[mc_name], input_path+file_name, signal=1)
                elif (mc_name.endswith("fix")):
                    for campaign in ["afix", "dfix"]:
                        file_name = f"{user_name}.{sample_map[mc_name]}_{campaign_map[campaign]}.root"
                        print(f"Loading file: {file_name}...")
                        mc[mc_name+f"_{campaign}"] = MC(mc_name, sampleDict[mc_name], input_path+file_name)
                else:
                    for campaign in campaign_list:
                        file_name = f"{user_name}.{sample_map[mc_name]}_{campaign_map[campaign]}.root"
                        print(f"Loading file: {file_name}...")
                        mc[mc_name+f"_{campaign}"] = MC(mc_name, sampleDict[mc_name], input_path+file_name)
                print_progress_bar(i+1, len(run_mc), prefix=f'Loading {run_num} MC files:', suffix=f'Completed: {mc_name}\n', length=50)

    # Old Yields Method
    if old_yields:
        mc_yields = get_mc_yields(mc, selections, selectionDict, cutPerSampleDict)
        if not mcOnly:
            data_yields = get_data_yields(data, selections, selectionDict)
            event_yields = {}
            for selection in selections:
                event_yields[selection] = mc_yields[selection] | data_yields[selection]
        else:
            event_yields = mc_yields
        process_names = list(set(sample.hist_name for sample_name, sample in mc.items())) + ['Data', 'Background']
        write_yields(event_yields, process_names, output_path, MC.SampleDict)

    if noPlots:
        return

    # for i, selection in enumerate(selections):
    #     # Loop over histogram required
    #     for histo_name in config["histosToPlot"]:
    #         # Create the variable name
    #         variable = histoDict.get(histo_name, {}).get('variable', histo_name)
    #         toGev = histoDict.get(histo_name, {}).get('toGeV', False)
   
    #         # Create histogram model
    #         hist_model = r.RDF.TH1DModel(f"hist_{variable}_{selection}",
    #                                  f"hist_{variable}_{selection}",
    #                                  histoDict[histo_name]['nBins'],
    #                                  histoDict[histo_name]['x-min'],
    #                                  histoDict[histo_name]['x-max'])
    
    # Loop over selection required
    for i, selection in enumerate(config["selectionToPlot"]):
        selection_cuts = selectionDict[selection]['cuts'][0]
        # Loop over histogram required
        for histo_name in config["histosToPlot"]:
            # Create the variable name
            variable = histoDict.get(histo_name, {}).get('variable', histo_name)
            toGev = histoDict.get(histo_name, {}).get('toGeV', False)

            # Create histogram model
            hist_model = r.RDF.TH1DModel(f"hist_{variable}_{selection}",
                                                             f"hist_{variable}_{selection}",
                                                             histoDict[histo_name]['nBins'],
                                                             histoDict[histo_name]['x-min'],
                                                             histoDict[histo_name]['x-max'])

            for s in mc:
                for cut in cutPerSampleDict:
                    do_cut = (s[:-(1+len(s.split("_")[-1]))] in cutPerSampleDict[cut]['samples'])
                    if do_cut:
                        mc[s].apply_cutPerSample(cutPerSampleDict[cut]['cuts'][0])
                mc[s].apply_selection(selection, selectionDict[selection]['cuts'][0])
                if mc[s].hist_name.startswith("ttbar") and apply_ttbar_reweighting:
                    mc[s].define_ttbar_weight(selection, 'weight')
                        # print the first 10 ttbar_weight values
                # Get histogram ptrs for MC samples
                mc[s].get_histogram_ptr(histo_name,
                                        variable,
                                        selection,
                                        hist_model,
                                        "weight",
                                        toGev)
                    
                # Get Yields ptrs for MC samples
                if yields:
                    if not apply_ttbar_reweighting or not mc[s].hist_name.startswith("ttbar"):
                        mc[s].set_sample_yields(selection)
                    elif apply_ttbar_reweighting and mc[s].hist_name.startswith("ttbar"):
                        mc[s].set_sample_yields(selection, weight="weight_wTTbarWeight")

            if not mcOnly:
                if config["fastframes_input"]:
                    for campaign in data:
                        data[campaign].apply_selection(selection, selectionDict[selection]['cuts'][0])
                        data[campaign].get_histogram_ptr(histo_name,
                                                                                        variable,
                                                                                        selection,
                                                                                        hist_model,
                                                                                        toGev)
                        if yields:
                            data[campaign].set_sample_yields(selection)
                else:
                    for campaign in data_campaigns:
                        data[campaign].apply_selection(selection, selectionDict[selection]['cuts'][0])
                        data[campaign].get_histogram_ptr(histo_name,
                                                                                        variable,
                                                                                        selection,
                                                                                        hist_model,
                                                                                        toGev)
                        if yields:
                            data[campaign].set_sample_yields(selection)
        print_progress_bar(i+1, len(config["selectionToPlot"]), prefix='Creating histograms:', suffix='Complete\n', length=50)

    if config["do_ttbar_reweighting_calc"] and not mcOnly:
        print("Queueing data ttbar reweighting...")
        Sample.setup_ttbar_reweighting_calc()
        # Create histogram model for each nJet bin
        # nbins = [50] * nJets  # Set the same number of bins for all nJets
        # Dict where key is number of jets and value is a list of bin edges for HT2
        if runs == "2":
            ttbar_reweighting_binEdges = {
                2 : array('d', [0, 33e3, 66e3, 100e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 440e3, 490e3, 533e3, 650e3, 1999e3]),
                3 : array('d', [0, 33e3, 66e3, 100e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 500e3, 575e3, 700e3, 1999e3]),
                4 : array('d', [0, 50e3, 100e3, 150e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 500e3, 600e3, 700e3, 850e3, 1999e3]),
                5 : array('d', [0, 70e3, 120e3, 160e3, 200e3, 250e3, 300e3, 400e3, 525e3, 650e3, 775e3, 1999e3]),
                6 : array('d', [0, 60e3, 100e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 500e3, 550e3, 600e3, 650e3, 750e3, 900e3, 1999e3]),
                7 : array('d', [0, 90e3, 150e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 500e3, 550e3, 600e3, 650e3, 700e3, 750e3, 850e3, 1999e3]),
                8 : array('d', [0, 66e3, 100e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 500e3, 550e3, 650e3, 800e3, 1999e3]),
                9 : array('d', [0, 66e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 500e3, 550e3, 650e3, 800e3, 1999e3]),
                10: array('d', [0, 150e3, 300e3, 400e3, 650e3, 1999e3]),
                11: array('d', [0, 150e3, 266e3, 400e3, 600e3, 1999e3]),
                12: array('d', [0, 200e3, 400e3, 1999e3]),
                13: array('d', [0, 200e3, 400e3, 1999e3]),
                14: array('d', [0, 200e3, 400e3, 1999e3]),
                15: array('d', [0, 200e3, 400e3, 1999e3]),
            }
        elif runs == "3":
            ttbar_reweighting_binEdges = {
                # 2 : array('d', [0, 33e3, 66e3, 100e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 433e3, 466e3, 500e3, 533e3, 566e3, 600e3, 650e3, 700e3, 750e3, 800e3, 900e3, 1999e3]),
                # 3 : array('d', [0, 33e3, 66e3, 100e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 433e3, 466e3, 500e3, 533e3, 566e3, 600e3, 650e3, 700e3, 750e3, 800e3, 850e3, 900e3, 950e3, 1000e3, 1999e3]),
                # 4 : array('d', [0, 33e3, 66e3, 100e3, 150e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 500e3, 600e3, 700e3, 800e3, 900e3, 1999e3]),
                # 5 : array('d', [0, 50e3, 100e3, 150e3, 200e3, 250e3, 300e3, 400e3, 525e3, 650e3, 775e3, 800e3, 1999e3]),
                # 6 : array('d', [0, 33e3, 66e3, 100e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 433e3, 466e3, 500e3, 533e3, 566e3, 600e3, 650e3, 700e3, 750e3, 800e3, 900e3, 1075e3, 1999e3]),
                # 7 : array('d', [0, 33e3, 66e3, 100e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 433e3, 466e3, 500e3, 533e3, 566e3, 600e3, 633e3, 666e3, 700e3, 733e3, 766e3, 800e3, 900e3, 1999e3]),
                # 8 : array('d', [0, 33e3, 66e3, 100e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 433e3, 466e3, 500e3, 533e3, 566e3, 600e3, 700e3, 800e3, 900e3, 1999e3]),
                # 9 : array('d', [0, 33e3, 66e3, 100e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 433e3, 466e3, 500e3, 533e3, 566e3, 600e3, 700e3, 800e3, 900e3, 1999e3]),
                # 10: array('d', [0, 100e3, 200e3, 300e3, 400e3, 600e3, 800e3, 1999e3]),
                # 11: array('d', [0, 100e3, 250e3, 400e3, 550e3, 700e3, 1999e3]),
                # 12: array('d', [0, 100e3, 250e3, 400e3, 550e3, 1999e3]),
                2 : array('d', [0, 33e3, 66e3, 100e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 440e3, 490e3, 600e3, 1999e3]),
                3 : array('d', [0, 33e3, 66e3, 100e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 500e3, 625e3, 1999e3]),
                4 : array('d', [0, 50e3, 100e3, 150e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 550e3, 700e3, 1999e3]),
                5 : array('d', [0, 70e3, 120e3, 160e3, 200e3, 250e3, 300e3, 400e3, 525e3, 650e3, 775e3, 1999e3]),
                6 : array('d', [0, 90e3, 133e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 500e3, 550e3, 600e3, 800e3, 1999e3]),
                7 : array('d', [0, 150e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 500e3, 550e3, 600e3, 650e3, 700e3, 850e3, 1999e3]),
                8 : array('d', [0, 125e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 500e3, 550e3, 650e3, 800e3, 1999e3]),
                9 : array('d', [0, 110e3, 166e3, 200e3, 233e3, 266e3, 300e3, 333e3, 366e3, 400e3, 450e3, 500e3, 550e3, 650e3, 800e3, 1999e3]),
                10: array('d', [0, 150e3, 300e3, 400e3, 650e3, 1999e3]),
                11: array('d', [0, 150e3, 266e3, 400e3, 600e3, 1999e3]),
                12: array('d', [0, 200e3, 400e3, 1999e3]),
                13: array('d', [0, 200e3, 400e3, 1999e3]),
                14: array('d', [0, 200e3, 400e3, 1999e3]),
                15: array('d', [0, 200e3, 400e3, 1999e3]),
            }
        hist_models = {}
        for i, njet in enumerate(range(2, nJets + 1)):
            hist_models[njet] = r.RDF.TH1DModel(f"hist_HT2_ttbar_CR_njet_{njet}",
                                                        f"hist_HT2_ttbar_CR_njet_{njet}",
                                                        len(ttbar_reweighting_binEdges[njet]) - 1,
                                                        ttbar_reweighting_binEdges[njet])
            # hist_models[njet] = r.RDF.TH1DModel(f"hist_HT2_ttbar_CR_njet_{njet}",
            #                                             f"hist_HT2_ttbar_CR_njet_{njet}",
            #                                             nbins[i],
            #                                             0,
            #                                             1999e3)
        for s in mc:
            if not mc[s].hist_name.startswith("HH"):
                mc[s].queue_ttbar_reweighting_yields(hist_models, "weight", nJets=nJets)
        if config["fastframes_input"]:
            for campaign in data:
                data[campaign].queue_ttbar_reweighting_yields(hist_models, "weight", nJets=nJets)
        else:
            for campaign in data_campaigns:
                data[campaign].queue_ttbar_reweighting_yields(hist_models, "weight", nJets=nJets)
        print("All samples queued!")
    elif mcOnly:
        print("Data ttbar reweighting cannot run in MC only mode. Skipping...")

    # Temporary to check ttbar_weight: Creating histogram ptrs for ttbar weight in ttbar samples
    if apply_ttbar_reweighting:
        ttbar_w_hists_ptrs = []
        for s in mc:
            if mc[s].hist_name.startswith("ttbar"):
                hist_model = r.RDF.TH1DModel(f"ttbar_weight_{s}",
                                             f"ttbar_weight_{s}",
                                             150,
                                             0.5,
                                             3.5)
                ttbar_w_hists_ptrs.append(mc[s].df["preselection"].Histo1D(hist_model, "ttbar_weight"))
                Sample.graphs.append(ttbar_w_hists_ptrs[-1])
    #####

    print("Running graphs...")
    Sample.runGraphs()
    print("Completed!")

    # Temporary to check ttbar_weight: evaluating and saving ttbar weight histograms
    if apply_ttbar_reweighting:
        i = 0
        for s in mc:
            if mc[s].hist_name.startswith("ttbar"):
                if i == 0:
                    ttbar_weight_hist = ttbar_w_hists_ptrs[i].GetValue().Clone("ttbar_weight_hist")
                else:
                    ttbar_weight_hist.Add(ttbar_w_hists_ptrs[i].GetValue())
                i += 1
        ttbar_weight_hist.SetName("ttbar_weight_hist")
        ttbar_weight_hist.SetTitle("ttbar weight histogram")
        ttbar_weight_hist.GetXaxis().SetTitle("ttbar weight")
        ttbar_weight_hist.GetYaxis().SetTitle("Entries")
        ttbar_weight_hist.GetXaxis().SetTitleOffset(1.2)
        ttbar_weight_hist.GetYaxis().SetTitleOffset(1.2)
        ttbar_weight_hist.GetXaxis().SetLabelFont(43)
        ttbar_weight_hist.GetXaxis().SetLabelSize(25)
        canvus = r.TCanvas("ttbar_weight_canvas", "ttbar_weight_canvas", 800, 600)
        ttbar_weight_hist.Draw("HIST")
        canvus.SaveAs(output_path + "ttbar_weight_hist.png") 
    #####

    # Create the canvas
    canv =  r.TCanvas("canvas","canvas",800,600)
    for i, selection in enumerate(config["selectionToPlot"]):
        # Evaluate histograms and save them
        for histo_name in config["histosToPlot"]:
            print("--- Plotting " + histo_name + " with selection " + selection + " ---")
            
            # Reset class members
            MC.reset()
            Data.reset()

            # Evaluate histograms
            #MC
            for sample in mc:
                mc[sample].eval_hist_value(histo_name, selection)

            #Data
            if not mcOnly:
                if config["fastframes_input"]:
                    for campaign in data:
                        data[campaign].eval_hist_value(histo_name, selection)
                else:
                    for campaign in data_campaigns:
                        data[campaign].eval_hist_value(histo_name, selection)
            else:
                Data.create_default_hist(mc[list(mc.keys())[0]].hist)

            canv.cd()

            # Create the upper pad if include_ratio leave space for ratio
            padhigh = createUpperPad(include_ratio,logOn)
            padhigh.Draw()
            padhigh.cd()

            # Create legend
            legend = initializeLegend()

            # Create the stack histogram
            MC.create_Stack(legend)
            #Temp
            # for hname in MC.histomap:
            #     if "ttbar" not in hname and "signal" not in hname:
            #         Data.data_hist.Add(-1 * MC.histomap[hname])
            ####

            # Create significance histograms
            MC.create_significance_histogram()

            # BLINDING
            if not UNBLIND:
                significance_ratios = MC.get_significance_ratios()
                Data.blind_data_hist(significance_ratios, config["BLIND_THRESHOLD"])

            if not mcOnly:
                legend.AddEntry(Data.data_hist, "Data", "PE")

            # Draw
            MC.stack.Draw("HIST")
            if not mcOnly:
                Data.data_hist.Draw("SAME E1")

            if dosignal:
                MC.draw_signal_histograms(legend)

            # Define y-asis label
            if 'y-axis title' in histoDict:
                y_title = histoDict[histo_name]['y-axis title']
            else:
                print(f"stack {MC.stack}")

                y_title = GetYtitle(MC.stack, histoDict[histo_name]['units'])

            MC.stack.GetYaxis().SetTitle(y_title)
            MC.stack.GetYaxis().SetTitleOffset(1)
            MC.stack.GetXaxis().SetNdivisions(306)

            ymax_upper = max(MC.stack.GetMaximum(), Data.data_hist.GetMaximum())
            MC.stack.SetMaximum(1.9*ymax_upper)

            # Draw x axis for top panel
            if not include_ratio:
                MC.stack.GetXaxis().SetTitle(histoDict[histo_name]['x-axis title'])
                MC.stack.GetXaxis().SetTitleOffset(1)
                MC.stack.GetXaxis().SetLabelFont(43)
                MC.stack.GetXaxis().SetLabelSize(25)
                MC.stack.GetYaxis().SetLabelFont(43)
                MC.stack.GetYaxis().SetLabelSize(25)
            else:
                MC.stack.GetXaxis().SetTitleOffset(99)
                MC.stack.GetXaxis().SetLabelSize(0)

            # Set up ATLAS label
            drawATLASLabel(selectionDict[selection], include_ratio, "Internal", lumi=lumi, com=com)

            # Draw Legend
            canv.cd()
            padside = r.TPad("padside","padside",0.5,0.52,0.85,0.96)
            padside.SetFillColorAlpha(0, 0.1)
            padside.Draw()
            padside.cd()
            legend.Draw("SAME")

            # RATIO PANEL
            if include_ratio:
                padLow = createLowerPad()
                canv.cd()
                padLow.Draw()
                padLow.cd()

                if mcOnly:
                    # if MC only -> Draw Significance
                    ratioHist = MC.significance_ratios[MC.sampleSignalNames[0]].Clone("ratioHist")
                    # ratioHist = Data.data_hist.Clone("ratioHist")
                    # ratioHist.Divide(MC.histomap["ttbar"])
                    ratioHist.GetYaxis().SetTitle("Significance")
                    ratioHist.Scale(0)
                    ratioHist.SetLineWidth(0)
                    ratioHist.Draw("SAME")
                    ymax_lower = max(MC.significance_ratios[s_name].GetMaximum() for s_name in MC.sampleSignalNames)

                    # create a pad for the significance
                    canv.cd()
                    padsig = r.TPad("padsig","padsig",0.6,0.17,0.85,0.28)
                    padsig.Draw()
                    padsig.cd()
                    ls = r.TLatex()
                    ls.SetNDC()
                    ls.SetTextColor(r.kBlack)
                    ls.SetTextFont(42)
                    ls.SetTextSize(0.2)
                    ls.DrawLatex(0.1, 1-(1)/(len(MC.sampleSignalNames)+1), "S_{i} = #sqrt{2((s+b)log(1+s/b)-s)}")
                    for k, s_name in enumerate(MC.sampleSignalNames):
                        padLow.cd()

                        MC.significance_ratios[s_name].SetLineWidth(2)
                        MC.significance_ratios[s_name].SetLineColor(colors.GetColor(*SignalDict[s_name]["color"]))

                        MC.significance_ratios[s_name].Draw("SAME HIST")

                        # print significance on the plot
                        padsig.cd()
                        ls.DrawLatex(0.1, 1-(k+2)/len(MC.sampleSignalNames), "Sig. "+s_name+": "+str(round(MC.significance_all[s_name], 2)))
                    padLow.cd()
                    ratioHist.SetMaximum(1.3*ymax_lower)
                else:
                    padLow.cd()
                    ratioHist = Data.data_hist.Clone("ratioHist")
                    ratioHist.GetYaxis().SetTitle("Data/MC")
                    ratioHist.Divide(MC.stack.GetStack().Last())
                    ratioHist.SetMarkerColor(r.kBlack)
                    ratioHist.SetMarkerStyle(r.kFullDotLarge)
                    ratioHist.SetLineColor(r.kBlack)
                    ratioHist.SetLineWidth(2)

                    # draw line at 1
                    line = r.TLine(ratioHist.GetXaxis().GetXmin(), 1, ratioHist.GetXaxis().GetXmax(), 1)
                    line.SetLineColor(r.kBlack)
                    line.SetLineWidth(2)

                    ratioHist.SetMaximum(1.2)
                    ratioHist.SetMinimum(0.8)
                    ratioHist.Draw("SAME E1")
                    line.Draw("SAME")

                ratioHist.GetYaxis().CenterTitle()
                ratioHist.GetYaxis().SetNdivisions(303)
                ratioHist.GetYaxis().SetTitleSize(0.10)
                ratioHist.GetYaxis().SetLabelSize(0.10)
                ratioHist.GetYaxis().SetTitleOffset(0.35)

                ratioHist.GetXaxis().SetTitle(histoDict[histo_name]['x-axis title'])
                ratioHist.GetXaxis().SetTitleSize(0.10)
                ratioHist.GetXaxis().SetLabelSize(20)
                ratioHist.GetXaxis().SetTitleOffset(1)
                ratioHist.GetXaxis().SetLabelFont(43)

            # Save the plot
            print("Saving the canvas name : ", output_path + histo_name + "_" + selection + ".png")
            canv.SaveAs(output_path + histo_name + "_" + selection + ".png")
            canv.SaveAs(output_path + histo_name + "_" + selection + ".pdf")
            canv.Clear()
        # Calculate global yields and write to file
        if yields:
            for sample in mc:
                mc[sample].eval_sample_yields(selection)
            MC.calc_mc_global_yields(selection)
            if config["fastframes_input"]:
                for campaign in data:
                    data[campaign].eval_sample_yields(selection)
            else:
                for campaign in data:
                    data[campaign].eval_sample_yields(selection)
        print_progress_bar(i+1,
                                           len(config["selectionToPlot"]),
                                           prefix='Creating plots:',
                                           suffix=f'Saved canvas :'+output_path + histo_name + "_" + selection + ".png\n",
                                           length=50)
    
    if config["do_ttbar_reweighting_calc"] and not mcOnly:
        print("Running data ttbar reweighting...")
        Sample.set_mc_yield_wo_ttbar(MC.mc_yield_wo_ttbar)
        Sample.calc_ttbar_reweighting_normalization()
        if config["fastframes_input"]:
            for campaign in data:
                data[campaign].eval_ttbar_reweighting_histogram(is_ttbar=False, is_mc=False)
        else:
            for campaign in data_campaigns:
                data[campaign].eval_ttbar_reweighting_histogram(is_ttbar=False, is_mc=False)
        for s in mc:
            if not mc[s].hist_name.startswith("HH"):
                if mc[s].hist_name.startswith("ttbar"):
                    mc[s].eval_ttbar_reweighting_histogram(is_ttbar=True, is_mc=True)
                else:
                    mc[s].eval_ttbar_reweighting_histogram(is_ttbar=False, is_mc=True)
        Sample.evaluate_ttbar_reweighting(runs)\
    
    if yields:
        Sample.write_yields_tex(MC.signal_map, MC.histomap, blind= not UNBLIND)
        Sample.write_yields_txt(blind= not UNBLIND)



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument("-c","--config",help="Path to the config file",default="config.yaml")
    parser.add_argument("-m","--mcOnly",help="", action="store_true",default=False)
    parser.add_argument("-r","--include_ratio",help="", action="store_true",default=False)
    parser.add_argument("-s","--dosignal",help="", action="store_true", default=False)
    parser.add_argument("-l","--logOn",help="", action="store_true", default=False)
    parser.add_argument("-t","--twoDim",help="",action="store_true",default=False)
    parser.add_argument("-y","--yields",help="",action="store_true",default=False)
    parser.add_argument("-oy","--old-yields",action="store_true",help="Uses old method to find yields", default=False)
    parser.add_argument("-np","--noPlots",help="Only works with old yields method",action="store_true",default=False)
    parser.add_argument("-rs","--runs",help="The runs to process, either 2, 3, or 23",default="2")
    #parser.add_argument("-p", "--plotDump", help="Option for making plots in different formats.", action="store_true", default=False)
    parser.add_argument("-UB","--UNBLIND",help="",action="store_true",default=False)
    return parser.parse_args()

if __name__ == "__main__":

    # Adding an argument parser, which we might want to use  a
    from argparse import ArgumentParser

    options = argument_parser()

    # Give warning if the user has selected both old and new yield methods
    if options.yields and options.old_yields:
        print("WARNING: You have selected both the old and new yield methods.")
    # Give warning if the user selects noPlots and not old_yields
    if options.noPlots and not options.old_yields:
        print("WARNING: The noPlots option only works with the old yields method.")
    # Give warning if the user selects noPlots and yields
    if options.noPlots and options.yields:
        print("WARNING: The noPlots option only works with the old yields method.")


    # Load the config file
    config = load_and_process_yaml(options.config)["makePlot"]

    output_path = config["output_path"]+f"/run{options.runs}/"
    # Input and output directories
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print("The output directory did not exist, I have just created one: ", output_path)

    # Defining dictionary to be passed to the main function
    # skip twoDim option
    option_dict = {k: v for k, v in vars(options).items() if (v is not None) and (k != "twoDim")}
    option_dict["config"] = config

    r.EnableImplicitMT()

    #print(option_dict)
    # if --twoDim true run main2D
    if options.twoDim:
        main2D(**option_dict)
    else:
        main1D(**option_dict)
