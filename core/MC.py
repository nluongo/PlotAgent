import ROOT as r
from math import log, sqrt
from histoDict import SignalDict, SampleDict_run2, SampleDict_run3
from core.Sample import Sample


class MC(Sample):
	
	colors = r.gROOT.GetColor(1)
	
	SignalDict = SignalDict()
	SampleDict = SampleDict_run2() | SampleDict_run3()
	
	r.gInterpreter.Declare("""
	float get_scale(TTree* ttree, std::vector<std::string> branches) {
		TTreeReader reader(ttree);
		float scale = 1;
		std::vector<TTreeReaderValue<float>> values;
		std::vector<bool> do_inverse;
		for (auto& branch : branches) {
			size_t pos = branch.find("1/");
			if (pos != std::string::npos) {
				branch.erase(pos, 2);
				TTreeReaderValue<float> reader_value(reader, branch.c_str());
				values.push_back(reader_value);
				do_inverse.push_back(true);
			} else {
				TTreeReaderValue<float> reader_value(reader, branch.c_str());
				values.push_back(reader_value);
				do_inverse.push_back(false);
			}
		}
		reader.Next();
		for (size_t i = 0; i < values.size(); i++) {
			if (do_inverse[i]) {
				scale = scale * (1 / *values[i]);
			} else {
				scale = scale * *values[i];
			}
		}
		return scale;
	}
	""")


	scale_formula = None
	weight_formula = None
	stack = r.THStack()
	# signalStack = r.THStack()
	histomap = {}
	signal_map = {}

	sampleStackNames = []
	sampleSignalNames = []

	doSignal = False

	significance_ratios = {}
	significance_all = {}

	drawn_first_hist = False

	apply_ttbar_reweighting = False

	@classmethod
	def reset(cls):
		cls.stack = r.THStack()
		cls.histomap = {}
		cls.signal_map = {}
		cls.significance_all = {}
		cls.significance_ratios = {}

	@classmethod
	def setup_ttbar_weights(cls, file_path, nJets=15):
		cls.ttbar_weights_hists = {}
		cls.ttbar_weights_file = r.TFile(file_path, "READ")
		# Set ttbar normalization factor
		norm_hist = cls.ttbar_weights_file.Get("ttbar_reweighting_normalization")
		if not norm_hist:
			print(f"Normalization histogram not found in {file_path}, using default value of 1.0")
			cls.ttbar_reweighting_normalization = 1.0
		else:
			cls.ttbar_reweighting_normalization = norm_hist.GetBinContent(1)
			print(f"TTbar reweighting normalization factor set to {cls.ttbar_reweighting_normalization} from {file_path}")
		# cls.ttbar_reweighting_normalization = 1.0
		# Loop over histograms for ttbar reweighting
		for i in range(2, nJets + 1):
			# Get histograms for the ttbar reweighting
			hist_name = f"ttbar_reweighting_hist_{i}_nJets"
			hist = cls.ttbar_weights_file.Get(hist_name)
			if not hist:
				print(f"Histogram {hist_name} not found in {file_path}")
				continue
			hist.SetDirectory(0)
			hist.SetName(hist_name)  # Ensure the histogram has a name
			cls.ttbar_weights_hists[i] = hist
		# Declare static cache and weight lookup in C++
		r.gInterpreter.Declare("""
		#include <TH1.h>
		static TH1D* __ttbar_hists["""+str(nJets+1)+"""] = {nullptr};
		double get_ttbar_weight(int nJets, double HT2) {
			if (nJets < 2 || nJets > """+str(nJets)+""") return 1.0;
			TH1D* h = __ttbar_hists[nJets];
			if (!h) return 1.0;
			int bin = h->GetXaxis()->FindBin(HT2);
			return h->GetBinContent(bin);
		}
		""")
		# Populate static array (once at setup)
		for i, hist in cls.ttbar_weights_hists.items():
			r.gInterpreter.ProcessLine(
				f"__ttbar_hists[{i}] = (TH1D*)gROOT->FindObject(\"{hist.GetName()}\");"
			)

		# cls.ttbar_weights = {}
		# cls.ttbar_weights_hists = {}
		# cls.ttbar_weights_file = r.TFile(file_path, "READ")
		# for i in range(2, 11):
		# 	# Get histograms for the reweighting
		# 	hist_name = f"ttbar_reweighting_hist_{i}_nJets"
		# 	hist = cls.ttbar_weights_file.Get(hist_name)
		# 	if not hist:
		# 		print(f"Histogram {hist_name} not found in {file_path}")
		# 		continue
		# 	hist.SetDirectory(0)  # Detach histogram from file
		# 	cls.ttbar_weights_hists[i] = hist
		# 	cls.ttbar_weights[i] = {}
		# 	for j in range(1, hist.GetNbinsX() + 1):
		# 		# Store the bin content and error in a dictionary
		# 		cls.ttbar_weights[i][j] = {
		# 			"bin_range": (hist.GetXaxis().GetBinLowEdge(j), hist.GetXaxis().GetBinUpEdge(j)),
		# 			"value": hist.GetBinContent(j),
		# 			"error": hist.GetBinError(j)
		# 		}
		cls.apply_ttbar_reweighting = True
	
	@classmethod
	def set_sampleDict(cls, sampleDict):
		cls.SampleDict = sampleDict
 
	@classmethod
	def set_scale_formula(cls, branches):
		cls.scale_formula = branches

	@classmethod
	def set_weight_formula(cls, branches):
		cls.weight_formula = branches

	@classmethod
	def set_sampleStackNames(cls, sampleStackNames):
		stack_list = []
		for stack in list(sampleStackNames.values()):
			stack_list += stack
		cls.sampleStackNames = stack_list
		stack_list = []
		for stack in list(sampleStackNames.values()):
			stack_list += stack
		cls.sampleStackNames = stack_list

	@classmethod
	def set_sampleSignalNames(cls, sampleSignalNames):
		cls.sampleSignalNames = sampleSignalNames

	@classmethod
	def set_doSignal(cls, bool):
		cls.doSignal = bool
	
	@classmethod
	def calc_mc_global_yields(cls, selection):
		cls.global_yields[selection]["MC"] = 0
		cls.global_yields[selection]["Background"] = 0
		for hist_name in cls.signal_map:
			cls.global_yields[selection]["MC"] += cls.global_yields[selection][hist_name]
			if cls.do_ttbar_reweighting_calc and selection == "ttbar_CR":
				cls.mc_yield_wo_ttbar += cls.global_yields[selection][hist_name]
		for hist_name in cls.histomap:
			if hist_name not in cls.signal_map:
				cls.global_yields[selection]["Background"] += cls.global_yields[selection][hist_name]
			cls.global_yields[selection]["MC"] += cls.global_yields[selection][hist_name]
			if cls.do_ttbar_reweighting_calc and selection == "ttbar_CR" and hist_name != "ttbar":
				cls.mc_yield_wo_ttbar += cls.global_yields[selection][hist_name]

	@classmethod
	def create_Stack(cls, legend):
		#TEMPORARY
		for histo in cls.histomap.values():
			legend.AddEntry(histo, histo.GetTitle(), "f")
			cls.stack.Add(histo)
		# for hname in cls.histomap:
		# 	legend.AddEntry(cls.histomap[hname], cls.histomap[hname].GetTitle(), "f")
		# 	if "ttbar" in hname:
		# 		cls.stack.Add(cls.histomap[hname])
	# @classmethod
	# def addSignalStack(cls, histo, stack, color, legend, legendText):
	# 	histo.SetLineWidth(2)
	# 	histo.SetLineStyle(r.kDashed)
	# 	histo.SetLineColor(color)
	# 	stack.Add(histo)
	# 	legend.AddEntry(histo, legendText, "l")
	
	@classmethod
	def create_significance_histogram(cls):
		for k, s_name in enumerate(cls.signal_map):
			cls.signal_map[s_name].Sumw2()
			histo_allbkg = cls.significance_ratios[s_name].Clone("histo_allbkg")
			histo_allbkg.Reset()
			for hname in cls.histomap:
				if hname != s_name:
					histo_allbkg.Add(cls.histomap[hname])
			for i in range(cls.signal_map[s_name].GetNbinsX()):
				if histo_allbkg.GetBinContent(i+1) > 0:
					s = cls.signal_map[s_name].GetBinContent(i+1)
					b = histo_allbkg.GetBinContent(i+1)
					val = 2*((s+b)*log(1+s/b)-s)
					if val > 0:
						s_bin = sqrt(2*((s+b)*log(1+s/b)-s))
					else:
						s_bin = 0.
					cls.significance_ratios[s_name].SetBinContent(i+1, s_bin)
					cls.significance_ratios[s_name].SetBinError(i+1, s_bin)
					cls.significance_all[s_name] += s_bin*s_bin
				else:
					cls.significance_ratios[s_name].SetBinContent(i+1, 0)
					cls.significance_ratios[s_name].SetBinError(i+1, 0)
			cls.significance_all[s_name] = sqrt(cls.significance_all[s_name])

	@classmethod
	def get_significance_ratios(cls):
		return cls.significance_ratios

	@classmethod
	def draw_signal_histograms(cls, legend):
		for s_name in cls.signal_map:
			cls.signal_map[s_name].SetLineWidth(2)
			cls.signal_map[s_name].SetLineColor(cls.colors.GetColor(*SignalDict()[s_name]["color"]))
			cls.signal_map[s_name].Scale(cls.SignalDict[s_name]["multiplier"])
			cls.signal_map[s_name].Draw("SAME HIST")
			legend.AddEntry(cls.signal_map[s_name], 
							cls.SignalDict[s_name]["legend description"]+ " #times "+str(cls.SignalDict[s_name]["multiplier"]), 
							"l")
	
	def __init__(self, name, info_map, file_path, signal=0):
		super().__init__(name, file_path)
		self.hist_name = info_map["histoname"]
		self.color = info_map["color"]
		self.legend = info_map["legend description"]
		self.signal = signal
		if self.status:
			if type(self.weight_formula) is list:
				weight_expr = ''.join([self.weight_formula[0]]+[f"*{branch}" for branch in self.weight_formula[1:]])
			elif type(self.weight_formula) is str:
				weight_expr = self.weight_formula
			else:
				weight_expr = "1"
			if self.scale_formula is not None:
				self.df["0"] = self.df["0"].DefinePerSample("scale", str(self.get_scale(self.ttree)))
				weight_expr += "*scale*1e3"
			if info_map["histoname"] in ["HH_251", "HH_260", "HH_300", "HH_400", "HH_500", "HH_600", "HH_800", "HH_1000"]:
				weight_expr += "*1e-3" #TEMP fix for HH signal xsec
			self.define_column("weight", weight_expr)

	def get_scale(self, ttree):
		scale = r.get_scale(ttree, self.scale_formula)
		return scale

	def apply_cutPerSample(self, cuts):
		if self.status:
			self.df["0"] = self.df["0"].Filter(cuts)
	
	def define_ttbar_weight(self, selection_name, weight=None):
		if self.status:
			if "weight_wTTbarWeight" not in self.df[selection_name].GetColumnNames():
				if self.hist_name == "ttbar":
					self.df[selection_name] = self.df[selection_name].Define("ttbar_weight", "get_ttbar_weight(bbll_nJets_NOSYS, bbll_HT2_NOSYS)")
					# Define normalization factor in dataframe
					self.df[selection_name] = self.df[selection_name].Define("ttbar_Norm", f"{self.ttbar_reweighting_normalization}")
					if weight:
						self.df[selection_name] = self.df[selection_name].Define("weight_wTTbarWeight", f"{weight}*ttbar_weight")
						self.df[selection_name] = self.df[selection_name].Define("weight_wTTbarWeight_andNorm", f"weight_wTTbarWeight*ttbar_Norm")
					else:
						self.df[selection_name] = self.df[selection_name].Define("weight_wTTbarWeight", "ttbar_weight")
						self.df[selection_name] = self.df[selection_name].Define("weight_wTTbarWeight_andNorm", "ttbar_weight*ttbar_Norm")
						self.df[selection_name] = self.df[selection_name].Define("ttbar_weight_andNorm", "ttbar_weight*ttbar_Norm")
				else:
					print(f"Warning: {self.hist_name} is not ttbar, no ttbar weight defined for selection {selection_name}")

	def get_histogram_ptr(self, observable_name, var_to_plot, selection_name, hist_model, weight=None, toGev=False):
		if self.status:
			if self.apply_ttbar_reweighting and self.hist_name == "ttbar":
				# Apply ttbar reweighting if applicable
				if weight:
					weight = "weight_wTTbarWeight_andNorm"
				else:
					weight = "ttbar_weight_andNorm"
			if weight is None:
				if toGev:
					self.df[selection_name] = self.df[selection_name].Define("GeV_"+var_to_plot, f"{var_to_plot}*1e-3")
					hist = self.df[selection_name].Histo1D(hist_model, "GeV_"+var_to_plot)
				else:
					hist = self.df[selection_name].Histo1D(hist_model, var_to_plot)
			else:
				if toGev:
					self.df[selection_name] = self.df[selection_name].Define("GeV_"+var_to_plot, f"{var_to_plot}*1e-3")
					hist = self.df[selection_name].Histo1D(hist_model, "GeV_"+var_to_plot, weight)
				else:
					hist = self.df[selection_name].Histo1D(hist_model, var_to_plot, weight)
			self.histos_ptr[observable_name+selection_name] = hist
			self.graphs.append(hist)
	
	def eval_sample_yields(self, selection_name):
		if self.status:
			if selection_name not in self.global_yields.keys():
				self.global_yields[selection_name] = {}
			self.sample_yields[selection_name] = self.sample_yields_ptr[selection_name].GetValue()
			if self.hist_name not in self.global_yields[selection_name].keys():
				self.global_yields[selection_name][self.hist_name] = self.sample_yields[selection_name]
			else:
				self.global_yields[selection_name][self.hist_name] += self.sample_yields[selection_name]
			if self.name not in self.global_yields[selection_name].keys():
				self.global_yields[selection_name][self.name] = self.sample_yields[selection_name]
			else:
				self.global_yields[selection_name][self.name] += self.sample_yields[selection_name]

	def eval_hist_value(self, observable_name, selection_name):
		if self.status:
			self.hist = self.histos_ptr[observable_name+selection_name].GetValue()
			# Create background histogram in map if not yet created, skip signal
			if self.hist_name not in self.histomap and self.name in self.sampleStackNames and self.hist_name not in self.sampleSignalNames:
				self.histomap[self.hist_name] = self.hist.Clone(self.hist_name)
				self.histomap[self.hist_name].Sumw2()
				self.histomap[self.hist_name].SetFillColor(self.colors.GetColor(*self.color))
				self.histomap[self.hist_name].SetLineColor(r.kBlack)
				self.histomap[self.hist_name].SetLineWidth(0)
				self.histomap[self.hist_name].SetTitle(self.legend)
			# If exists, add
			elif self.name in self.sampleStackNames and self.hist_name not in self.sampleSignalNames:
				self.histomap[self.hist_name].Add(self.hist)
			# Add signal to separate map
			if self.hist_name in self.sampleSignalNames:
				sig_ratio_hist = self.hist.Clone("ratioHist_"+self.hist_name)
				sig_ratio_hist.Reset()
				MC.significance_ratios[self.hist_name] = sig_ratio_hist
				MC.significance_all[self.hist_name] = 0
				if self.doSignal:
					if self.hist_name not in self.signal_map:
						self.signal_map[self.hist_name] = self.hist.Clone(f"hist_signal_{self.hist_name}")
						self.signal_map[self.hist_name].Sumw2()
						self.signal_map[self.hist_name].SetLineColor(self.colors.GetColor(*self.SignalDict[self.hist_name]["color"]))
					else:
						self.signal_map[self.hist_name].Add(self.hist)
