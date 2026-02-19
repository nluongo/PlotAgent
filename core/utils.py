'''
  A collection of functions for making publication-ready
  plots from root inputs.

  M. Nelson, 2019 <michael.edward.nelson@cern.ch

'''

import os
import sys
import ROOT as r
from ROOT import gROOT
from array import array
import collections
from math import sqrt
import yaml
from core import MC

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()
    if iteration == total:
        print()

def restructureSampleMap(sampleDict):
    '''
    Restructure the sample dictionary to be more easily
    accessible for plotting.
    '''
    newDict = {}
    for key in sampleDict:
        for sample in sampleDict[key]['samples']:
            newDict[sample] = {}
            newDict[sample]['histoname'] = key
            newDict[sample]['color'] = sampleDict[key]['color']
            newDict[sample]['legend description'] = sampleDict[key]['legend description']
    return newDict

def createUpperPad(doRatio=True, logOn=False):

    if doRatio: 
        padhigh = r.TPad("padhigh","padhigh",0.0,0.3,1.,1.)
        padhigh.SetBottomMargin(0.02)
    else:
        #r.gStyle.SetPadLeftMargin(0.20)
        padhigh = r.TPad("padhigh","padhigh",0.0,0.0,1.,1.)
        padhigh.SetBottomMargin(0.15)

    if logOn: 
        padhigh.SetLogy()

    padhigh.SetGrid(0,0)

    return padhigh

def createLowerPad():

    padLow = r.TPad("padlow","padlow",0.0,0.0,1.,0.3)
    padLow.SetTopMargin(0.03)
    padLow.SetBottomMargin(0.3)
    padLow.SetFillStyle(4000)
    padLow.SetGrid(1,1)

    return padLow

def initializeLegend( x1=0.1, y1=0.1, x2=.9, y2=.9): 
#def initializeLegend(x1=0.1, y1=0.55, x2=0.90, y2=0.95):

    aLegend = r.TLegend(x1, y1, x2, y2)
    aLegend.SetLineColor(r.kWhite)
    aLegend.SetFillColor(r.kWhite)
    aLegend.SetNColumns(1)
    aLegend.SetTextSize(0.06)
    #aLegend.SetTextSize(0.115)
    #aLegend.SetTextSize(0.12)
    aLegend.SetBorderSize(0)
    aLegend.SetTextFont(42) # Remove bold text
    
    return aLegend

def getScaledHistogram(name, theHistos, scale=1):
    histo = theHistos.Get(name)
    histo.Scale(1/scale)
    return histo

def shape(histo, color, legend, legendText):
    histo.SetFillColor(color)
    histo.SetMarkerColor(color)
    histo.SetLineColor(r.kBlack)
    legend.AddEntry(histo, legendText, "f")

def shape_alt(histo, color):
    histo.SetFillColor(color)
    histo.SetMarkerColor(color)
    histo.SetLineColor(r.kBlack)

def defineHistos(histo, sampleDict, samplesToStack):
    # histomap append "name" : histo_{name}
    histomap = {}
    for sample in samplesToStack:
        histoname = sampleDict[sample]['histoname']
        legendtxt = sampleDict[sample]['legend description']

        if histoname not in histomap:
            histomap[histoname] = histo.Clone(histoname)
            histomap[histoname].Reset()
            histomap[histoname].Sumw2()
            colors = gROOT.GetColor(1)
            histomap[histoname].SetFillColor(colors.GetColor(*sampleDict[sample]['color']))
            histomap[histoname].SetLineColor(r.kBlack)
            histomap[histoname].SetLineWidth(0)
            histomap[histoname].SetTitle(legendtxt)
    
    return histomap

def addStack(histo, stack, legend):
    stack.Add(histo)
    legend.AddEntry(histo, histo.GetTitle(), "f")

def addSignalStack(histo, stack, color, legend, legendText):
    histo.SetLineWidth(2)
    histo.SetLineStyle(r.kDashed)
    histo.SetLineColor(color)
    stack.Add(histo)
    legend.AddEntry(histo, legendText, "l")

def addRatio(ratioHist, numeratorHist, denominatorHist):
    ratioHist = numeratorHist.Clone()
    ratioHist.Divide(denominatorHist)
    #ratioHist.Sumw2()

def getSumHist(histo, sumHist):
    nBins = histo.GetNbinsX()
    uBin = histo.GetXaxis().GetXmax()
    dBin = histo.GetXaxis().GetXmin()
    sumHist.SetBins(nBins, dBin, uBin)
    sumHist.Add(histo)

def rebin_hist(histo, bins_array):
    newname = histo.GetName()+'_rebinned'
    newhist = histo.Rebin(len(bins_array)-1, newname, bins_array)
    newhist.SetDirectory(0)
    newhist.GetYaxis().SetRangeUser(0.1,100000)

    return newhist

def rebin_THStack(stack, bins_array):
    tempStack = THStack('Background stack rebinned','')
    histList = stack.GetHists()
    
    for hist in histList:
        if type(bins_array) == int:
            tempHist = hist.Rebin(bins_array)
        else:
            tempHist = rebin_plot(hist, bins_array)
        tempHist.SetDirectory(0)
        tempStack.Add(tempHist)
    
    return tempStack

def GetYtitle(stackHist, units):
    theHisto = stackHist.GetStack().Last()
    bins = theHisto.GetNbinsX()
    xmin = theHisto.GetXaxis().GetXmin()
    xmax = theHisto.GetXaxis().GetXmax()
    res = (xmax-xmin)/bins

    y_title = "Events / " + str(round(res,1))+" "+units

    return y_title

def CheckXrange(theHisto, new_xmin, new_xmax):
    xmin = theHisto.GetXaxis().GetXmin()
    xmax = theHisto.GetXaxis().GetXmax()
    status = False
    if ((new_xmin < xmin) or (new_xmax > xmax)):
        print("WARNING x-min and/or x-max is outside the histogram range. Using TH1F edges instead")
    elif ((new_xmin > xmin) or (new_xmax < xmax)):
        print("Zooming in a sub-range of the original TH1F using x-min and x-max edges")
        status = True

    return status

def MergeBackgrounds(MergeBkgList, Reg, Bkg, yields):

    Merge = []
    Merge_unc = []
    NoHBkg = []
    for r in Reg:
        events = 0
        unc = 0
        for b in Bkg:
            if (b in MergeBkgList):
                events += yields[b][r][0]
                unc +=  yields[b][r][1]**2

        Merge.append(events)
        Merge_unc.append(sqrt(unc))

    for b in Bkg:
        if (b not in MergeBkgList): NoHBkg.append(b)

    return (Merge, Merge_unc, NoHBkg)

def drawATLASLabel(legend, include_ratio=False, atlastext="Internal", lumi=140, com=13):
    l = r.TLatex()
    l.SetNDC()
    l.SetTextColor(r.kBlack)
    l.SetTextFont(42)
    l1, l2 = 0.22, 0.88
    r.ATLASLabel(l1,l2,atlastext)
    if include_ratio:
        l.SetTextSize(0.06)
        l.DrawLatex(l1, 0.81, "#sqrt{{#it{{s}}}} = {} TeV, {} fb^{{-1}}".format(com, lumi))
        l.DrawLatex(l1, 0.74, "HH#rightarrowb#bar{b}ll")
        l.DrawLatex(l1, 0.68, legend['legend upper'])
        l.DrawLatex(l1, 0.60, legend['legend lower'])
    else:
        l.SetTextSize(0.05)
        l.DrawLatex(l1, 0.82, "#sqrt{{#it{{s}}}} = {} TeV, {} fb^{{-1}}".format(com, lumi))
        l.DrawLatex(l1, 0.76, "HH#rightarrowb#bar{b}ll")
        l.DrawLatex(l1, 0.69, legend['legend upper'])
        l.DrawLatex(l1, 0.64, legend['legend lower'])

def drawATLASLabel2D(legend, sample, atlastext="Internal"):
    l = r.TLatex()
    l.SetNDC()
    l.SetTextColor(r.kBlack)
    l.SetTextFont(42)
    # draw outside
    l1, l2 = 0.15, 0.95
    r.ATLASLabel(l1,l2,atlastext)
    l.SetTextSize(0.04)
    l.DrawLatex(l1, 0.9, "#sqrt{#it{s}} = 13 TeV, 140 fb^{-1}")
    l1 = 0.5
    l.DrawLatex(l1, 0.96, sample)
    l.DrawLatex(l1, 0.92, legend['legend upper'])
    l.DrawLatex(l1, 0.88, legend['legend lower'])

def setBlindedValuestoZero(dataHist, signficance_ratios, BLIND_THRESHOLD=0.01):
    for i in range(dataHist.GetNbinsX()):
        for s_histo in signficance_ratios:
            if signficance_ratios[s_histo].GetBinContent(i+1) > BLIND_THRESHOLD:
                dataHist.SetBinContent(i+1, 0)
                dataHist.SetBinError(i+1, 0)
    return dataHist

def ExtractBinning(signal):

    binning = []

    try:

        with open('/afs/cern.ch/work/l/lapereir/public/HH/SH_PNN_binning/histograms_h027_TransfoJ_1BinsInBkgRegion_TunedParameters_SR_pre_fit_'+signal+'.yaml', 'r') as stream:
            try:
                d=yaml.safe_load(stream)
            except yaml.YAMLError as e:
                print(e)

        for b in d['binning']:
            binning.append(round(b, 4))

        return binning


    except:
        print(signal," PNN binning file not available will use default from the config file")

        return 0

def get_sample_cuts(sample_name, sample_cuts_dict):
    for key in sample_cuts_dict:
        if sample_name in sample_cuts_dict[key]['samples']:
            if type(sample_cuts_dict[key]['cuts']) == list:
                return ' && '+' && '.join(sample_cuts_dict[key]['cuts'])
            elif type(sample_cuts_dict[key]['cuts']) == str:
                return ' && '+ sample_cuts_dict[key]['cuts']
    return ''

def sample_yield(sample, selection_name, cuts, weighted=1):
    sample.apply_selection(selection_name, cuts)
    s_yield = sample.event_sum(selection_name, weighted)
    return s_yield

def get_mc_yields(samples, selections, selection_dict, sample_cuts_dict):
    process_names = list(set(samples[s].hist_name for s in samples))
    event_yields = {}
    # Loop over selection required
    for i, selection in enumerate(selections):
        selection_cuts = selection_dict[selection]['cuts'][0]
        event_yields[selection] = {}
        # Initialize yield counts to zero
        event_yields[selection]['Background'] = 0
        for process_name in process_names:
            event_yields[selection][process_name] = 0
        # Loop over samples
        for sample_name, sample in samples.items():
            process_name = sample.hist_name
            # Apply extra cuts
            sample_cuts = get_sample_cuts(sample_name, sample_cuts_dict)
            cuts = selection_cuts + sample_cuts

            event_count = sample_yield(sample, selection, cuts)
            # Store each sample yield individually
            event_yields[selection][sample_name] = event_count
            # Summarize by process
            if not sample.signal:
                event_yields[selection]['Background'] += event_count
            event_yields[selection][process_name] += event_count
    return event_yields

def get_data_yields(samples, selections, selection_dict):
    event_yields = {}
    # Loop over selection required
    for i, selection in enumerate(selections):
        event_yields[selection] = {}
        # Initialize yield counts to zero
        event_yields[selection]['Data'] = 0
        if type(samples) == list:
            for sample_name, sample in samples.items():
                event_count = sample_yield(sample, selection, selection_dict[selection]['cuts'][0], weighted=0)
                # Store yields for each campaign and all data
                event_yields[selection][sample_name] = event_count
                event_yields[selection]['Data'] += event_count
        else:
            sample_name = samples.name
            event_count = sample_yield(samples, selection, selection_dict[selection]['cuts'][0], weighted=0)
            # Store yields for each campaign and all data
            event_yields[selection][sample_name] = event_count
            event_yields[selection]['Data'] += event_count
    return event_yields

def process_yield(event_yields, process_name, tex_name, blind=1):
    tex_name = tex_name.replace('#it','\\textit')
    tex_name = tex_name.replace('#bar{t}', '$\\bar{t}$')
    line = f'{tex_name} '
    for selection in event_yields:
        if blind and process_name == 'Data' and 'Signal_Region' in selection:
            n_events = -1
            line += f'& -'
        else:
            n_events = event_yields[selection][process_name]
            line += f' & {n_events:.3f}'

    line += ' \\\\\n'
    return line

def tex_header(num_columns):
    column_string = '{l' + 'r'*num_columns + '}'
    header = r'''\documentclass[varwidth=\maxdimen]{standalone}
\usepackage{amsmath}
\begin{document}
\begin{table}
\begin{tabular}''' + column_string + '\n'
    return header

def tex_footer():
    footer = r'''\end{tabular}
\end{table}
\end{document}'''
    return footer

def write_yields(event_yields, process_names, dest, SampleDict, per_sample=0, blind=1):
    # Set up output files
    txt_name = f'yields.txt'
    txt_out = open(f'{dest}/{txt_name}', 'w')
    tex_name = f'yields.tex'
    tex_out = open(f'{dest}/{tex_name}', 'w')

    # Create header
    header = tex_header(len(event_yields))

    # Create footer
    footer = tex_footer()

    tex_out.write(header)

    region_dict = {
        'preselection'  : 'Preselection',
        'Signal_Region' : 'SR 1',
        'Signal_Region2': 'SR 2',
        'ZHF_CR'        : '\\textit{Z}+HF CR',
        'ttbar_CR'      : '\\textit{t$\\bar{\\boldsymbol{t}}$} CR',
        'singletop_CR'  : '\\textit{Wt} CR'
        }

    # Create first line holding regions
    top_line = ' \\textbf{Process} '
    for selection in event_yields:
        if selection in region_dict:
            selection = region_dict[selection]
        top_line += f'& \\textbf{{{selection}}} '
    top_line += ' \\\\ \hline\n'
    tex_out.write(top_line)

    if 'Data' in process_names:
        line = process_yield(event_yields, 'Data', 'Data', blind)
        tex_out.write(line)
        process_names.remove('Data')
    if 'Background' in process_names:
        line = process_yield(event_yields, 'Background', 'Background')
        tex_out.write(line)
        process_names.remove('Background')

    signal_process_names = sorted([name for name in process_names if 'HH' in name], key=lambda x: int("".join([char for char in x if char.isdigit()])))
    background_process_names = sorted([name for name in process_names if name not in signal_process_names])

    tex_out.write('\hline\n')

    SignalDict = MC.SignalDict()
    SampleDict = SampleDict

    # Loop over signal samples and write a line for each
    for process_name in signal_process_names:
        display_name = SignalDict[process_name]["legend description"]
        line = process_yield(event_yields, process_name, display_name)
        tex_out.write(line)

    tex_out.write('\hline\n')

    # Loop over background samples and write a line for each
    for process_name in background_process_names:
        for sample in SampleDict:
            if SampleDict[sample]['histoname'] == process_name:
                display_name = SampleDict[sample]['legend description']
        line = process_yield(event_yields, process_name, display_name)
        tex_out.write(line)

    tex_out.write(footer)

    # Print yields to txt file
    for selection, selection_yields in event_yields.items():
        txt_out.write(f'{selection}:\n')
        for process_name, yields in selection_yields.items():
            txt_out.write(f'{process_name}:  {yields:.3f}\n')
        if 'Data' in selection_yields and 'Background' in selection_yields:
            n_back = selection_yields['Background']
            n_data = selection_yields['Data']
            txt_out.write(f'Normalization (B/D):  {n_back / n_data:.3f}\n')
        txt_out.write('\n')

    tex_out.close()
    txt_out.close()