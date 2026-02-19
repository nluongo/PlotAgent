''' 
  A python directory summarising the plotting properties
  of each histogram produced for the final plots

  M. Nelson, 2019 <michael.edward.nelson@cern.ch>
'''


import ROOT as r 


def SampleDict_run2():
    dict = {
        'SM Signals': {
            'samples': ['bbWW_SM_new', 'bbtt_SM_new', 'bbZZ_SM_new'],
            'color': (255, 0, 0),
            'legend description': 'SM Signals'
        },
        'bb4l': {
            'samples': ['top_bb4l_alldilepflav'],
            'color': (93, 175, 188),
            'legend description': '#it{bb4l}'
        },
        'HH (251 GeV)': {
            'samples': ['bbWW_251', 'bbZZ_251', 'bbtt_251','bbZZ_llqq_251'],
            'color': (227, 173, 102),
            'legend description': '#it{HH_251}'
        },
        'HH (260 GeV)': {
            'samples': ['bbWW_260', 'bbZZ_260', 'bbtt_260','bbZZ_llqq_260'],
            'color': (227, 173, 102),
            'legend description': '#it{HH_260}'
        },
        'HH (300 GeV)': {
            'samples': ['bbWW_300', 'bbZZ_300', 'bbtt_300','bbZZ_llqq_300'],
            'color': (227, 73, 102),
            'legend description': '#it{HH_300}'
        },
        'HH (400 GeV)': {
            'samples': ['bbWW_400', 'bbZZ_400', 'bbtt_400','bbZZ_llqq_400'],
            'color': (227, 73, 102),
            'legend description': '#it{HH_400}'
        },
        'HH (500 GeV)': {
            'samples': ['bbWW_500', 'bbZZ_500', 'bbtt_500','bbZZ_llqq_500'],
            'color': (227, 73, 102),
            'legend description': '#it{HH_500}'
        },
        'HH (600 GeV)': {
            'samples': ['bbWW_600', 'bbZZ_600', 'bbtt_600','bbZZ_llqq_600'],
            'color': (227, 73, 102),
            'legend description': '#it{HH_600}'
        },
        'HH (800 GeV)': {
            'samples': ['bbWW_800', 'bbZZ_800', 'bbtt_800','bbZZ_llqq_800'],
            'color': (227, 73, 102),
            'legend description': '#it{HH_800}'
        },
        'HH (1000 GeV)': {
            'samples': ['bbWW_1000', 'bbZZ_1000', 'bbtt_1000','bbZZ_llqq_1000'],
            'color': (227, 73, 102),
            'legend description': '#it{HH_1000}'
        },
        'HH (1500 GeV)': {
            'samples': ['bbWW_1500', 'bbZZ_1500', 'bbtt_1500','bbZZ_llqq_1500'],
            'color': (227, 73, 102),
            'legend description': '#it{HH_1500}'
        },
        'HH (3000 GeV)': {
            'samples': ['bbWW_3000', 'bbZZ_3000', 'bbtt_3000','bbZZ_llqq_3000'],
            'color': (227, 73, 102),
            'legend description': '#it{HH_3000}'
        },
        'ttbar': {
            'samples': ['ttbar_dilep', 'ttbar_nonallhad', 'ttbar_allhad'],
            'color': (93, 175, 188),
            'legend description': '#it{t#bar{t}}'
        },
        'Z+HF': {
            'samples': ['Zee+jet_Bfilt', 'Zmumu+jet_Bfilt', 'Ztautau+jet_Bfilt', 'Zee+jet_CFilterBveto', 'Zee+jet_CfiltBveto', 'Zmumu+jet_CfiltBveto', 'Ztautau+jet_CfiltBveto', 'Zee+jet_CvetoBveto', 'Zee+jet_CvetoBveto_fix', 'Zmumu+jet_CvetoBveto', 'Zmumu+jet_CvetoBveto_fix', 'Ztautau+jet_CvetoBveto', 'Zee+jet_lowmass_Bfilt', 'Zee+jet_lowmass_CfiltBveto', 'Zee+jet_lowmass_CvetoBveto', 'Zmumu+jet_lowmass_Bfilt', 'Zmumu+jet_lowmass_CfiltBveto', 'Zmumu+jet_lowmass_CvetoBveto'],
            'color': (80, 80, 227),
            'legend description': '#it{Z}+HF',
        },
        'Z+jet': {
            'samples': ['Zee+jet_Bfilt_light', 'Zmumu+jet_Bfilt_light', 'Ztautau+jet_Bfilt_light', 'Zee+jet_CfiltBveto_light', 'Zmumu+jet_CfiltBveto_light', 'Ztautau+jet_CfiltBveto_light', 'Zee+jet_CvetoBveto_light', 'Zee+jet_CvetoBveto_light_fix', 'Zmumu+jet_CvetoBveto_light', 'Zmumu+jet_CvetoBveto_light', 'Zmumu+jet_CvetoBveto_light_fix', 'Ztautau+jet_CvetoBveto_light', 'Zee+jet_lowmass_Bfilt_light', 'Zee+jet_lowmass_CfiltBveto_light', 'Zee+jet_lowmass_CvetoBveto_light', 'Zmumu+jet_lowmass_Bfilt_light', 'Zmumu+jet_lowmass_CfiltBveto_light', 'Zmumu+jet_lowmass_CvetoBveto_light'],
            'color': (130, 130, 130),
            'legend description': '#it{Z}+jet',
        },
        'Diboson': {
            'samples': ['Diboson_2lep_os', 'Diboson_2lep_ss', 'Diboson_3lep', 'Diboson_4lep', 'Diboson_ZqqZll', 'Diboson_ZbbZll', 'Diboson_ZbbZvv', 'Diboson_WqqZll', 'Diboson_WqqZvv', 'Diboson_WlvZqq', 'Diboson_WlvZbb', 'Diboson_WlvWqq', 'Diboson_WW_ewk', 'Diboson_ZZ_ewk', 'Diboson_4l_0M4l130', 'Diboson_4l_130M4l', 'Diboson_4l_0M4l130_nohiggs', 'Diboson_4l_130M4l_nohiggs'],
            'color': (20, 100, 150),
            'legend description': 'Diboson'
        },
        'singletop': {
            'samples': ['singletop_schan_top', 'singletop_schan_antitop', 'singletop_tchan_top', 'singletop_tchan_antitop', 'singletop_Wt_inc_antitop', 'singletop_Wt_dil_antitop', 'singletop_Wt_inc_top', 'singletop_Wt_dil_top'],
            'color': (20, 200, 20),
            'legend description': '#it{Wt}'
        },
        'ttX': {
            'samples': ['ttll_ee', 'ttll_mm', 'ttll_Zqq', 'ttll_Zvv', 'ttW'],
            'color': (200, 200, 20),
            'legend description': '#it{ttX}'
        },
        'singleH': {
            'samples': ['ggH_tautaul13l7', 'ggH_tautaulm15hp20', 'ggH_tautaulp15hm20', 'ggH_tautauh30h20', 'ggH_etau', 'ggH_mutau', 'ggH_WWlvlv', 'VH_WmH_lvbb', 'VH_WpH_lvbb', 'VH_ZH_llbb', 'VH_ZH_vvbb', 'ggVH_ZH_llbb', 'VH_WpH_WWlvlv', 'VH_WmH_WWlvlv', 'VH_mWinc_tautau', 'VH_pWinc_tautau', 'VH_WpH_lvWWlvqq', 'VH_WmH_qqWWlvlv', 'VH_WmH_lvWWlvqq', 'VH_ZH_Zinc_tautau', 'VH_ZH_qqWWlvlv', 'VH_ZH_ZinclWWlvlv', 'ttH_allhad', 'ttH_semilep', 'ttH_dilep', 'H_ZZ_llvv', 'VH_ZZ_llvv', 'VH_ggZZ_llvv', 'VH_ZH_ZincWWlvlv', 'VH_ZH_ZincWWlvqq', 'VH_ZH_ZllWWlvqq', 'VH_ggZH_Zinc_tautau', 'VH_ggZH_ZincWWlvqq', 'VH_ggZH_ZincWWlvlv', 'VH_mWH_WincWWlvlv', 'VH_mWH_WincWWlvqq', 'VH_mWH_WlepWWlvlv', 'VH_mWH_WlepWWlvqq', 'VH_mWH_WlepWWlvqq', 'VH_pWH_WincWWlvlv', 'VH_pWH_WincWWlvqq', 'VH_pWH_WlepWWlvqq', 'ggH_VH_WWlvlv', 'ggH_WWlvlv', 'ggH_WWlvqq', 'VH_pWH_WlepWWlvlv'],
            'color': (255, 0, 255),
            'legend description': 'Higgs'
        },
        'W+jet': {
            'samples': ['Wenu+jet_Bfilt', 'Wenu+jet_CFilterBveto', 'Wenu+jet_CvetoBveto', 'Wmunu+jet_Bfilt', 'Wmunu+jet_CfiltBveto', 'Wmunu+jet_CvetoBveto', 'Wtaunu_H+jet_CfiltBveto', 'Wtaunu_L+jet_Bfilt', 'Wtaunu_L+jet_CfiltBveto', 'Wtaunu_L+jet_CvetoBveto'],
            'color': (80, 80, 255),
            'legend description': 'W+jet'
        },
    }
    return dict

def SampleDict_run3():
    d = SampleDict_run2()
    d['ttbar']['samples'] = [
        'ttbar_dilep_fix', 
        'ttbar_singlelep_fix',
        'ttbar_allhad',
    ]
    d['Z+HF']['samples'] = [
        "Zee+jet_Bfilt",
        "Zee+jet_CFilterBveto",
        "Zee+jet_CvetoBveto_fix",
        "Zmumu+jet_Bfilt",
        "Zmumu+jet_CFilterBveto",
        "Zmumu+jet_CvetoBveto_fix",
        "Zee+jet_lowmass_Bfilt",
        "Zee+jet_lowmass_CfiltBveto",
        "Zee+jet_lowmass_CvetoBveto",
        "Zmumu+jet_lowmass_Bfilt",
        "Zmumu+jet_lowmass_CfiltBveto",
        "Zmumu+jet_lowmass_CvetoBveto",
        "Ztautau+jet_Bfilt",
        "Ztautau+jet_CFilterBveto",
        "Ztautau+jet_CvetoBveto",
    ]
    d['Z+jet']['samples'] = [
        "Zee+jet_Bfilt_light",
        "Zee+jet_CFilterBveto_light",
        "Zee+jet_CvetoBveto_light_fix",
        "Zmumu+jet_Bfilt_light",
        "Zmumu+jet_CFilterBveto_light",
        "Zmumu+jet_CvetoBveto_light_fix",
        "Zee+jet_lowmass_Bfilt_light",
        "Zee+jet_lowmass_CfiltBveto_light",
        "Zee+jet_lowmass_CvetoBveto_light",
        "Zmumu+jet_lowmass_Bfilt_light",
        "Zmumu+jet_lowmass_CfiltBveto_light",
        "Zmumu+jet_lowmass_CvetoBveto_light",
        "Ztautau+jet_Bfilt_light",
        "Ztautau+jet_CFilterBveto_light",
        "Ztautau+jet_CvetoBveto_light",
    ]
    d['singletop']['samples'] = [
        "singletop_tb_lep_antitop",
        "singletop_tb_lep_top",
        "singletop_tqb_lep_antitop",
        "singletop_tqb_lep_top",
        "singletop_tW_inc_antitop",
        "singletop_tW_inc_top",
        "singletop_tW_dil_antitop",
        "singletop_tW_dil_top",
    ]
    d['Diboson']['samples'] = [
        "Diboson_2lep_os",
        "Diboson_2lep_ss",
        "Diboson_3lep",
        "Diboson_4lep",
        "Diboson_ZqqZll",
        "Diboson_ZbbZll",
        "Diboson_ZbbZvv",
        "Diboson_WqqZll",
        "Diboson_WqqZvv",
        "Diboson_WlvZqq",
        "Diboson_WlvZbb",
        "Diboson_WlvWqq",
    ]
    d['singleH']['samples'] = [
        "VH_WmH_lvbb",
        "VH_WpH_lvbb",
        "VH_ZZ_llvv",
        "VH_ggZZ_llvv",
        "ggH_tautaul13l7",
        "ggH_tautaulm15hp20",
        "ggH_tautaulp15hm20",
        "ggH_tautauh30h20",
        "VH_mWinc_tautau",
        "VH_pWinc_tautau",
        "VH_ZH_Zinc_tautau",
        "VH_ZH_ggZinc_tautau",
        "ttH_semilep",
        "ttH_dilep",
        "ttH_semilep_tautau",
        "ttH_dilep_tautau",
        "ttH_allhad_tautau",
        "VH_ZH_Zhad_tautau",
        "VH_ZH_WWlvlv_fix",
        "VH_ZH_WWlvqq_fix",
        "VH_WH_mWlep_lvlv_fix",
        "VH_WH_mWlep_lvqq_fix",
        "VH_WH_pWlep_lvlv_fix",
        "VH_WH_pWlep_lvqq_fix",
        "VH_ZH_WW_lvlv_fix",
        "VH_ZH_WW_lvqq_fix",
        "VH_ZH_Zinc_WWlvlv_fix",
        "VH_ZH_Zinc_WWlvqq_fix",
        "VH_WH_mWinc_WWlvlv_fix",
        "VH_WH_mWinc_WWlvqq_fix",
        "VH_WH_pWinc_WWlvlv_fix",
        "VH_WH_pWinc_WWlvqq_fix",
        "VH_ZH_qqZinc_WWlvlv_fix",
        "VH_ZH_qqZinc_WWlvqq_fix",
        "ggH_WW_lvlv_fix",
        "ggH_ZZ_llvv_fix",
        "ttH_allhad", 
        "ttH_semilep",
        "ttH_dilep", 
        "H_ZZ_llvv", 
        "VH_ggZZ_llvv",
        "VH_ZH_ZincWWlvlv",
        "VH_ZH_ZincWWlvqq",
        "VH_ZH_ZllWWlvqq",
        "VH_ggZH_ZincWWlvlv",
        "VH_ggZH_ZincWWlvqq",
        "VH_ggZH_Zinc_tautau",
        "VH_mWH_WincWWlvlv",
        "VH_mWH_WincWWlvqq",
        "VH_mWH_WlepWWlvlv",
        "VH_pWH_WincWWlvlv",
        "VH_pWH_WincWWlvqq",
        "VH_pWH_WlepWWlvqq",
        "ggH_VH_WWlvlv",
        "ggH_WWlvlv",
        "ggH_WWlvqq",
        "ggVH_ZH_llbb",
        "VH_ZH_llbb",
        "VH_mWH_WlepWWlvqq",
        "VH_pWH_WlepWWlvlv",
    ]
    d['W+jet']['samples'] = [
        "Wenu+jet_Bfilt",
        "Wenu+jet_CFilterBveto",
        "Wenu+jet_CvetoBveto",
        "Wmunu+jet_Bfilt",
        "Wmunu+jet_CFilterBveto",
        "Wmunu+jet_CvetoBveto",
        "Wtaunu+jet_Bfilt",
        "Wtaunu+jet_CFilterBveto",
        "Wtaunu+jet_CvetoBveto",
        ]
    d['ttX']['samples'] = [
        "ttW_2L",
        "ttll_ee",
        "ttll_mm",
        "ttll_tautau",
        "ttll_Zqq",
        ]
    return d

def CutPerSampleDict():
    dict = {
        'top_dileptonic_removal': {
            'samples': ['ttbar_nonallhad', "singletop_Wt_inc_antitop", "singletop_Wt_inc_top"],
            'cuts': ['(nWLep < 2)']
        },
    }
    return dict

def CutPerStackDict():
    dict = {
        'HFcutlist': {
            'stacks': ['Z+HF'],
            'cuts': ['(bbll_Jet_b1_truthLabel_NOSYS >= 4 && bbll_Jet_b2_truthLabel_NOSYS >= 4)']
        },
        'LFcutlist': {
            'stacks': ['Z+jet'],
            'cuts': ['(bbll_Jet_b1_truthLabel_NOSYS < 4 && bbll_Jet_b2_truthLabel_NOSYS < 4)']
        },
    }
    return dict


def PlottingDict():
    dict = {
        'bbll_mll_NOSYS': { # Name of histogram as defined the PlottingList.py
            'x-axis title': '#it{m}_{ll} [GeV]',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 1000,
            'nBins' : 50,
            'toGeV' : True
        },
        'bbll_HT2_NOSYS': {
            'x-axis title': '#it{HT2} [GeV]',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 800,
            'nBins' : 80,
            'toGeV' : True
            },
        'bbll_nJets_NOSYS': {
            'x-axis title': '#it{nJet} [GeV]',
            'units' : '',
            'x-min' : 0,
            'x-max' : 10,
            'nBins' : 10,
            },        
        'bbll_PNN_Score_X251_NOSYS': {
            'x-axis title': 'PNN SR1 251 GeV',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 1,
            'nBins' : 10,
        },
        'bbll_PNN_Score_X1000_NOSYS': {
            'x-axis title': 'PNN SR1 1000 GeV',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 1,
            'nBins' : 10,
        },
        'bbll_mbb_NOSYS': { 
            'x-axis title': '#it{m_{bb}} [GeV]',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 500,
            'nBins' : 20,
            'toGeV' : True
        },
        'bbll_pTll_NOSYS': {
            'x-axis title': '#it{pT}_{ll} [GeV]',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 300,
            'nBins' : 30,
            'toGeV' : True
        },
        'bbll_mbbllmet_NOSYS': { 
            'x-axis title': '#it{m_{bbll}+MET} [GeV]',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 4000,
            'nBins' : 200,
            'toGeV' : True
        },
        'bbll_Etabb_NOSYS': { 
            'x-axis title': '#it{eta_{bb}}',
            'units' : 'GeV',
            'x-min' : -2.5,
            'x-max' : 2.5,
            'nBins' : 30,
        },
        'bbll_Etall_NOSYS': { 
            'x-axis title': '#it{eta_{ll}}',
            'units' : 'GeV',
            'x-min' : -2.5,
            'x-max' : 2.5,
            'nBins' : 30,
        },
        'bbll_Jet_b1_pt_NOSYS': { 
            'x-axis title': '#it{p_{T}^{b,lead}} [GeV]',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 500,
            'nBins' : 25,
            'toGeV' : True
        },
        'bbll_Jet_b2_pt_NOSYS': { 
            'x-axis title': '#it{p_{T}^{b,sublead}} [GeV]',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 300,
            'nBins' : 30,
            'toGeV' : True
        },
        'bbll_Lepton1_pt_NOSYS': { 
            'x-axis title': '#it{p_{T}^{l,lead}} [GeV]',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 300,
            'nBins' : 30,
            'toGeV' : True
        },
        'bbll_Lepton2_pt_NOSYS': { 
            'x-axis title': '#it{p_{T}^{l,sublead}} [GeV]',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 100,
            'nBins' : 20,
            'toGeV' : True
        },
        'bbll_mbl_NOSYS': { 
            'x-axis title': '#it{m_{bl}} [GeV]',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 1000,
            'nBins' : 50,
            'toGeV' : True
        },
        'bbll_dRbl_min_NOSYS': { 
            'x-axis title': 'min \Delta R_{bl}',
            'units' : 'GeV',
            'x-min' : 0.25,
            'x-max' : 3,
            'nBins' : 11,
        },
        'bbll_dRll_NOSYS': { 
            'x-axis title': '\Delta R_{ll}',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 4.5,
            'nBins' : 18,
        },
        'bbll_dRbb_NOSYS': { 
            'x-axis title': '\Delta R_{bb}',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 5,
            'nBins' : 30,
        },
        'bbll_Lepton1_eta_NOSYS': { 
            'x-axis title': '#it{eat_{lep1}}',
            'units' : 'GeV',
            'x-min' : -2.5,
            'x-max' : 2.5,
            'nBins' : 30,
        },
        'bbll_Lepton2_eta_NOSYS': { 
            'x-axis title': '#it{eta_{lep2}}',
            'units' : 'GeV',
            'x-min' : -2.5,
            'x-max' : 2.5,
            'nBins' : 30,
        },
        'bbll_Jet_b1_eta_NOSYS': { 
            'x-axis title': '#it{eta_{b1}}',
            'units' : 'GeV',
            'x-min' : -2.5,
            'x-max' : 2.5,
            'nBins' : 30,
        },
        'bbll_Jet_b2_eta_NOSYS': { 
            'x-axis title': '#it{eta_{b2}}',
            'units' : 'GeV',
            'x-min' : -2.5,
            'x-max' : 2.5,
            'nBins' : 30,
        }
    }

    return dict

def SignalDict():
    dict = {
        'SM Signals': {
            'legend description': 'SM Signals',
            'color': (127, 0, 0),
            'multiplier': 100
        },
        'bb4l': {
            'legend description': '#it{bb4l}',
            'color': (93, 175, 188),
            'multiplier': 1
        },
        'ttbar': {
            'legend description': '#it{t#bar{t}}',
            'color': (93, 175, 188),
            'multiplier': 0.919 #???
        },
        'HH (251 GeV)': {
            'legend description': '#it{HH} (251 GeV)',
            #'color': (227, 73, 102),
            'color': (176, 82, 74),
            'multiplier': 200
        },
        'HH (260 GeV)': {
            'legend description': '#it{HH} (260 GeV)',
            #'color': (227, 73, 102),
            'color': (186, 102, 82),
            'multiplier': 200
        },
        'HH (300 GeV)': {
            'legend description': '#it{HH} (300 GeV)',
            #'color': (227, 73, 102),
            'color': (196, 122, 90),
            'multiplier': 200
        },
        'HH (400 GeV)': {
            'legend description': '#it{HH} (400 GeV)',
            #'color': (227, 73, 102),
            'color': (204, 142, 102),
            'multiplier': 200
        },
        'HH (500 GeV)': {
            'legend description': '#it{HH} (500 GeV)',
            #'color': (227, 73, 102),
            'color': (198, 160, 122),
            'multiplier': 200
        },
        'HH (600 GeV)': {
            'legend description': '#it{HH} (600 GeV)',
            #'color': (227, 73, 102),
            'color': (180, 176, 150),
            'multiplier': 200
        },
        'HH (800 GeV)': {
            'legend description': '#it{HH} (800 GeV)',
            #'color': (227, 73, 102),
            'color': (158, 168, 168),
            'multiplier': 200
        },
        'HH (1000 GeV)': {
            'legend description': '#it{HH} (1000 GeV)',
            #'color': (227, 73, 102),
            'color': (158, 168, 168),
            'multiplier': 200
        },
        'HH (1500 GeV)': {
            'legend description': '#it{HH} (1500 GeV)',
            #'color': (227, 73, 102),
            'color': (108, 146, 196),
            'multiplier': 200
        },
        'HH (3000 GeV)': {
            'legend description': '#it{HH} (3000 GeV)',
            #'color': (227, 73, 102),
            'color': (90, 130, 202),
            'multiplier': 200
        },
        'ZH': {
            'legend description': 'ZH(b#bar{b}#gamma#gamma)',
            'color': (20, 100, 150),
            'multiplier': 200
        },
        'Z+HF': {
            'legend description': '#it{Z}+HF',
            'color': (80, 80, 227),
            'multiplier': 1.086
        },
    }
    return dict

def SelectionDict():
    dict = {
        'preselection': {
            'legend upper': 'Preselection',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS)']
        },
        'preselection_Wt_CR': {
            'legend upper': 'Preselection_Wt_CR',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>200e3)']
        },
        'preselection_mll': {
            'legend upper': 'Pre-sel and #it{m_{ll}} > 15GeV',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_mll_NOSYS>15e3)']
        },
        'preselection_mbb': {
            'legend upper': 'Pre-sel and #it{m_{ll}} [40-210]GeV',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_mbb_NOSYS>40e3 && bbll_mbb_NOSYS<210e3)']
        },
        'preselection_SF': {
            'legend upper': 'OS and SF leptons',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_IS_SF_NOSYS)']
        },
        'preselection_DF': {
            'legend upper': 'OS and DF leptons',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_IS_em_NOSYS)']
        },
        'preselection_ee': {
            'legend upper': 'OS and SF leptons (ee only)',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_IS_ee_NOSYS)']
        },
        'preselection_mm': {
            'legend upper': 'OS and SF leptons (mm only)',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_IS_mm_NOSYS)']
        },
        'Signal_Region': {
            'legend upper': 'SR1',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && ((bbll_mll_NOSYS>15e3 && bbll_mll_NOSYS<75e3 && bbll_IS_SF_NOSYS) || (bbll_mll_NOSYS>15e3 && bbll_mll_NOSYS<110e3 && bbll_IS_em_NOSYS)) && bbll_mbb_NOSYS >60e3 && bbll_mbb_NOSYS < 160e3)'] #new cuts
            # 'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && ((bbll_mll_NOSYS>15e3 && bbll_mll_NOSYS<75e3 && bbll_IS_SF_NOSYS) || (bbll_mll_NOSYS>15e3 && bbll_mll_NOSYS<110e3 && bbll_IS_em_NOSYS)))'] #old cuts
        },
        'Signal_Region2': {
            'legend upper': 'SR2',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_IS_SF_NOSYS && (bbll_mll_NOSYS > 75e3 && bbll_mll_NOSYS < 110e3) && (bbll_mbb_NOSYS > 60e3 && bbll_mbb_NOSYS < 160e3) )'] #new cuts
            # 'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_IS_SF_NOSYS && (bbll_mll_NOSYS > 75e3 && bbll_mll_NOSYS < 110e3) && (bbll_mbb_NOSYS > 40e3 && bbll_mbb_NOSYS < 210e3) )'] #old cuts
        },
        'ZHF_CR': {
            'legend upper': 'ZHF_CR',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_IS_SF_NOSYS && bbll_mll_NOSYS>75e3 && bbll_mll_NOSYS<110e3 && (bbll_mbb_NOSYS < 40e3 || bbll_mbb_NOSYS > 210e3) && bbll_Lepton2_pt_NOSYS < 40e3 && bbll_MET_sig_NOSYS<3.5)']
            # 'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_IS_SF_NOSYS && bbll_mll_NOSYS>75e3 && bbll_mll_NOSYS<110e3 && (bbll_mbb_NOSYS < 40e3 || bbll_mbb_NOSYS > 210e3) && bbll_Lepton2_pt_NOSYS < 40e3)'] #old cuts
        },
        'ttbar_CR': {
            'legend upper': 'ttbar_CR',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS<250e3)']
        },
        'ttbar_CR_SF': {
            'legend upper': 'ttbar_CR_SF',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_IS_SF_NOSYS && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS<250e3)'] # cuts unchanged
        },
        'ttbar_CR_DF': {
            'legend upper': 'ttbar_CR_DF',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_IS_em_NOSYS && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS<250e3)']
        },
        'ttbar_CR_VBFVeto': {
            'legend upper': 'ttbar_CR_VBFVeto',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_VBFVETO_SR1_NOSYS && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS<250e3)']
        },
        'singletop_CR': {
            'legend upper': 'stop_CR',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>250e3 && met_met_NOSYS>50e3)']
            # 'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>250e3)'] #old cuts
        },
        'singletop_CR_lowmass': {
            'legend upper': 'stop_CR_lowmass',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>250e3 && bbll_Jet_b2_pt_NOSYS > 45e3 && met_met_NOSYS>50e3)']
            # 'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>250e3 && bbll_Jet_b2_pt_NOSYS > 45e3)'] #old cuts

        },
        'singletop_CR_pTcuts': {
            'legend upper': 'stop_CR_lowmass',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>250e3 && bbll_Jet_b1_pt_NOSYS > 45e3 && bbll_Jet_b2_pt_NOSYS > 45e3 && met_met_NOSYS>50e3)']
            # 'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>250e3 && bbll_Jet_b1_pt_NOSYS > 45e3 && bbll_Jet_b2_pt_NOSYS > 45e3)'] #old cuts

        },
        'singletop_CR_ee': {
            'legend upper': 'stop_CR_ee',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>250e3 && bbll_IS_ee_NOSYS && met_met_NOSYS>50e3)']
            # 'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>250e3 && bbll_IS_ee_NOSYS)'] #old cuts
        },
        'singletop_CR_mm': {
            'legend upper': 'stop_CR_mm',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>250e3 && bbll_IS_mm_NOSYS && met_met_NOSYS>50e3)']
            # 'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>250e3 && bbll_IS_mm_NOSYS)'] #old cuts
        },
        'singletop_CR_em': {
            'legend upper': 'stop_CR_em',
            'legend lower': '',
            'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>250e3 && bbll_IS_em_NOSYS && met_met_NOSYS>50e3)']
            # 'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && (bbll_IS_SF_NOSYS || bbll_IS_em_NOSYS) && bbll_mll_NOSYS>110e3 && bbll_mbl_NOSYS>250e3 && bbll_IS_em_NOSYS)'] #old cuts
        }
    }
    return dict
