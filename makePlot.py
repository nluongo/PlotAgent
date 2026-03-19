import os
import sys
import yaml
import ROOT as r
import hashlib
import json
from collections import OrderedDict
from core.utils import *
from core.Sample import *
from core.MC import *
from core.Data import *
from ROOT import gROOT, gStyle
from array import array
from core.parse_config import load_and_process_yaml, load_config

r.gROOT.LoadMacro("./AtlasStyle/AtlasStyle.C")
r.gROOT.LoadMacro("./AtlasStyle/AtlasLabels.C")
r.gROOT.LoadMacro("./AtlasStyle/AtlasUtils.C")

colors = gROOT.GetColor(1)

r.SetAtlasStyle()
r.gDebug = 0
r.EnableImplicitMT()

r.gROOT.SetBatch(1)
r.gStyle.SetPalette(56)

histoDict = {}
sampleDicts = {'run2': {}, 'run3': {}}

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

selectionDict = {}
cutPerSampleDict = {}
cutPerStackDict = {}

# ---------------------------------------------------------------------------
# YAML builder helpers — convert YAML config sections into the dict shapes
# that the existing pipeline expects.
# ---------------------------------------------------------------------------

def _build_sample_dict_from_yaml(stacks_config):
    """Pre-restructureSampleMap() format: {stack_name: {samples, color, legend description}}."""
    result = {}
    for stack_name, stack in stacks_config.items():
        result[stack_name] = {
            'samples': list(stack.get('samples', [])),
            'color': tuple(stack['color']),
            'legend description': stack.get('legend', stack_name),
        }
    return result


def _build_signal_dict_from_yaml(stacks_config):
    """SignalDict shape from stacks where is_signal: true."""
    result = {}
    for stack_name, stack in stacks_config.items():
        if stack.get('is_signal', False):
            result[stack_name] = {
                'legend description': stack.get('legend', stack_name),
                'color': tuple(stack['color']),
                'multiplier': stack.get('signal_multiplier', 1),
            }
    return result


def _build_histo_dict_from_yaml(variables_config):
    """Pass-through: variables.yaml variables schema matches PlottingDict()."""
    return dict(variables_config)


def _build_selection_dict_from_yaml(selections_config):
    """Pass-through: selections.yaml schema matches SelectionDict()."""
    return dict(selections_config)


def _build_cut_dicts_from_yaml(stacks_config, samples_config):
    """Return (cut_per_stack, cut_per_sample) dicts from YAML extra_cuts fields."""
    cut_per_stack = {}
    for stack_name, stack in stacks_config.items():
        if 'extra_cuts' in stack:
            key = f'yaml_stack_{stack_name}'
            cut_per_stack[key] = {
                'stacks': [stack_name],
                'cuts': list(stack['extra_cuts']),
            }
    cut_per_sample = {}
    for sample_name, sample in samples_config.items():
        if isinstance(sample, dict) and 'extra_cuts' in sample:
            key = f'yaml_sample_{sample_name}'
            cut_per_sample[key] = {
                'samples': [sample_name],
                'cuts': list(sample['extra_cuts']),
            }
    return cut_per_stack, cut_per_sample


def _build_campaign_map_from_yaml(campaigns_config, run_num):
    """campaign_map (shorthand → full suffix string) for a given run."""
    return dict(campaigns_config.get(run_num, {}))


def _build_sample_map_from_yaml(samples_config, run_num):
    """sample_map (sample_name → dataset_id) for a given run."""
    result = {}
    for sample_name, sample in samples_config.items():
        if not isinstance(sample, dict):
            continue
        run_data = sample.get(run_num, {})
        if isinstance(run_data, dict) and 'dataset_id' in run_data:
            result[sample_name] = run_data['dataset_id']
    return result


def _compute_plot_config_hash(histo_name, selection, hist_def,
                               selections_config, stacks_config, weight_formula):
    """SHA-256 hash of the config fields that determine a plot's appearance."""
    key_data = {
        'histo': histo_name,
        'selection': selection,
        'x-min': hist_def.get('x-min'),
        'x-max': hist_def.get('x-max'),
        'nBins': hist_def.get('nBins'),
        'cuts': (selections_config.get(selection) or {}).get('cuts'),
        'stacks': {k: {'color': v.get('color'), 'legend': v.get('legend')}
                   for k, v in stacks_config.items()},
        'weight': str(weight_formula),
    }
    return hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()


def _load_plot_hashes(output_path):
    """Load stored plot config hashes from <output_path>/.plot_hashes.json."""
    hash_file = os.path.join(output_path, '.plot_hashes.json')
    if os.path.exists(hash_file):
        with open(hash_file) as f:
            return json.load(f)
    return {}


def _save_plot_hashes(output_path, hashes):
    """Persist plot config hashes to <output_path>/.plot_hashes.json."""
    hash_file = os.path.join(output_path, '.plot_hashes.json')
    with open(hash_file, 'w') as f:
        json.dump(hashes, f, indent=2)


def _dump_individual_plots(config, output_file):
    """Expand selectionToPlot x histosToPlot matrix into per-plot YAML and write to output_file."""
    plots = []
    for sel in config['selectionToPlot']:
        for histo in config['histosToPlot']:
            plots.append({'selection': sel, 'histogram': histo})
    with open(output_file, 'w') as f:
        yaml.dump({'plots': plots}, f, default_flow_style=False, sort_keys=False)
    print(f"Wrote {len(plots)} plot definitions to {output_file}")


# ---------------------------------------------------------------------------

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

    if '_stacks_config' not in config:
        raise RuntimeError(
            "No YAML config found. Support for histoDict.py / PlottingList.py "
            "has been removed. Please provide a config.yaml with 'includes:' "
            "pointing to configs/samples.yaml, configs/variables.yaml, and "
            "configs/selections.yaml."
        )

    campaign_maps = {'run2': {}, 'run3': {}}
    sample_maps = {'run2': {}, 'run3': {}}

    # ---- YAML path: populate module-level dicts from split config files ----
    stacks_cfg   = config['_stacks_config']
    samples_cfg  = config['_samples_config']
    vars_cfg     = config['_variables_config']
    sels_cfg     = config['_selections_config']
    camps_cfg    = config['_campaigns_config']

    histoDict.clear()
    histoDict.update(_build_histo_dict_from_yaml(vars_cfg))

    selectionDict.clear()
    selectionDict.update(_build_selection_dict_from_yaml(sels_cfg))

    yaml_sample_dict = _build_sample_dict_from_yaml(stacks_cfg)
    sampleDicts['run2'] = yaml_sample_dict
    sampleDicts['run3'] = yaml_sample_dict

    yaml_cut_stack, yaml_cut_sample = _build_cut_dicts_from_yaml(stacks_cfg, samples_cfg)
    cutPerStackDict.clear()
    cutPerStackDict.update(yaml_cut_stack)
    cutPerSampleDict.clear()
    cutPerSampleDict.update(yaml_cut_sample)

    campaign_maps['run2'] = _build_campaign_map_from_yaml(camps_cfg, 'run2')
    campaign_maps['run3'] = _build_campaign_map_from_yaml(camps_cfg, 'run3')
    sample_maps['run2']   = _build_sample_map_from_yaml(samples_cfg, 'run2')
    sample_maps['run3']   = _build_sample_map_from_yaml(samples_cfg, 'run3')

    MC.set_SignalDict(_build_signal_dict_from_yaml(stacks_cfg))
    # ------------------------------------------------------------------------

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

    # Build unified plot list — either from explicit `plots:` YAML section or
    # by expanding the selectionToPlot x histosToPlot matrix.
    if '_plots_config' in config:
        plot_list = config['_plots_config']
    else:
        plot_list = [{'selection': s, 'histogram': h}
                     for s in config['selectionToPlot']
                     for h in config['histosToPlot']]

    plots_by_selection = OrderedDict()
    for p in plot_list:
        plots_by_selection.setdefault(p['selection'], []).append(p)

    MC.set_sampleDict(sampleDicts)
    selections = list(plots_by_selection.keys())

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
    
    # ---- Plot-skip hash logic (YAML path only) ----
    stored_hashes = {}
    new_hashes    = {}
    plots_to_skip = set()
    if '_stacks_config' in config:
        stored_hashes = _load_plot_hashes(output_path)
        for _plot_def in plot_list:
            _sel   = _plot_def['selection']
            _histo = _plot_def['histogram']
            _hist_def = histoDict.get(_histo, {}).copy()
            # Apply per-plot axis overrides when computing the hash
            if 'nBins' in _plot_def:
                _hist_def['nBins'] = _plot_def['nBins']
            if 'x_min' in _plot_def:
                _hist_def['x-min'] = _plot_def['x_min']
            if 'x_max' in _plot_def:
                _hist_def['x-max'] = _plot_def['x_max']
            _new_hash  = _compute_plot_config_hash(
                _histo, _sel, _hist_def,
                config['_selections_config'], config['_stacks_config'],
                config.get('weight_factor'))
            new_hashes[(_sel, _histo)] = _new_hash
            _out_file  = output_path + _histo + "_" + _sel + ".png"
            _hash_key  = f"{_histo}__{_sel}"
            if _new_hash == stored_hashes.get(_hash_key) and os.path.exists(_out_file):
                plots_to_skip.add((_sel, _histo))
    # ------------------------------------------------

    # Loop over selections (grouped from plot_list)
    for i, (selection, sel_plots) in enumerate(plots_by_selection.items()):
        selection_cuts = selectionDict[selection]['cuts'][0]
        # Loop over plots for this selection
        for plot_def in sel_plots:
            histo_name = plot_def['histogram']
            skip_this_plot = (selection, histo_name) in plots_to_skip
            # Create the variable name
            variable = histoDict.get(histo_name, {}).get('variable', histo_name)
            toGev = histoDict.get(histo_name, {}).get('toGeV', False)

            # Create histogram model (only needed when not skipping)
            # Per-plot overrides take precedence over histoDict defaults.
            if not skip_this_plot:
                nBins = plot_def.get('nBins', histoDict[histo_name]['nBins'])
                x_min = plot_def.get('x_min', histoDict[histo_name]['x-min'])
                x_max = plot_def.get('x_max', histoDict[histo_name]['x-max'])
                hist_model = r.RDF.TH1DModel(f"hist_{variable}_{selection}",
                                             f"hist_{variable}_{selection}",
                                             nBins, x_min, x_max)

            for s in mc:
                for cut in cutPerSampleDict:
                    do_cut = (s[:-(1+len(s.split("_")[-1]))] in cutPerSampleDict[cut]['samples'])
                    if do_cut:
                        mc[s].apply_cutPerSample(cutPerSampleDict[cut]['cuts'][0])
                mc[s].apply_selection(selection, selectionDict[selection]['cuts'][0])
                # Get histogram ptrs for MC samples
                if not skip_this_plot:
                    mc[s].get_histogram_ptr(histo_name,
                                            variable,
                                            selection,
                                            hist_model,
                                            "weight",
                                            toGev)

                # Get Yields ptrs for MC samples
                if yields:
                    mc[s].set_sample_yields(selection)

            if not mcOnly:
                if config["fastframes_input"]:
                    for campaign in data:
                        data[campaign].apply_selection(selection, selectionDict[selection]['cuts'][0])
                        if not skip_this_plot:
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
                        if not skip_this_plot:
                            data[campaign].get_histogram_ptr(histo_name,
                                                             variable,
                                                             selection,
                                                             hist_model,
                                                             toGev)
                        if yields:
                            data[campaign].set_sample_yields(selection)
        print_progress_bar(i+1, len(plots_by_selection), prefix='Creating histograms:', suffix='Complete\n', length=50)

    print("Running graphs...")
    Sample.runGraphs()
    print("Completed!")

    # Create the canvas
    canv =  r.TCanvas("canvas","canvas",800,600)
    for i, (selection, sel_plots) in enumerate(plots_by_selection.items()):
        # Evaluate histograms and save them
        for plot_def in sel_plots:
            histo_name = plot_def['histogram']
            if (selection, histo_name) in plots_to_skip:
                print(f"--- Skipping {histo_name} / {selection} (config unchanged, output exists) ---")
                continue

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
            # Per-plot log_scale override takes precedence over the -l CLI flag.
            _logOn = plot_def.get('log_scale', logOn)
            padhigh = createUpperPad(include_ratio, _logOn)
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
                        MC.significance_ratios[s_name].SetLineColor(colors.GetColor(*MC.SignalDict[s_name]["color"]))

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
            # Record hash for this plot so future runs can skip it if unchanged
            _hash_key = f"{histo_name}__{selection}"
            if (selection, histo_name) in new_hashes:
                stored_hashes[_hash_key] = new_hashes[(selection, histo_name)]
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
                                           len(plots_by_selection),
                                           prefix='Creating plots:',
                                           suffix=f'Saved canvas :'+output_path + histo_name + "_" + selection + ".png\n",
                                           length=50)

    # Persist updated hashes for the next run's skip logic
    if '_stacks_config' in config:
        _save_plot_hashes(output_path, stored_hashes)

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
    parser.add_argument('--dump-plots', '-dp', type=str, default=None, metavar='FILE',
        help='Expand the plot matrix into individual plot definitions and write to FILE, then exit')
    parser.add_argument('--plots-file', '-pf', type=str, default=None, metavar='FILE',
        help='Load per-plot definitions from FILE (YAML with top-level `plots:` key), '
             'overriding configs/plots.yaml and the selectionToPlot × histosToPlot matrix')
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
    config = load_config(options.config)["makePlot"]

    if options.dump_plots:
        _dump_individual_plots(config, options.dump_plots)
        sys.exit(0)

    if options.plots_file:
        with open(options.plots_file) as _pf:
            _plots_data = yaml.safe_load(_pf)
        if not _plots_data or 'plots' not in _plots_data:
            raise ValueError(f"--plots-file {options.plots_file!r} must contain a top-level 'plots:' key")
        config['_plots_config'] = _plots_data['plots']

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
