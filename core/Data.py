import ROOT as r
from core.Sample import Sample

class Data(Sample):
	data_hist = None

	@classmethod
	def set_data_hist(cls, hist):
		cls.data_hist = hist

	@classmethod
	def create_default_hist(cls, hist):
		cls.data_hist = hist.Clone("dataHist")
		cls.data_hist.Reset()

	@classmethod
	def reset(cls):
		cls.data_hist = None

	@classmethod
	def blind_data_hist(cls, significance_ratios, threshold=0.01):
		for i in range(cls.data_hist.GetNbinsX()):
			for s_histo in significance_ratios:
				if significance_ratios[s_histo].GetBinContent(i+1) > threshold:
					cls.data_hist.SetBinContent(i+1, 0)
					cls.data_hist.SetBinError(i+1, 0)

	def __init__(self, name, file_path):
		super().__init__(name, file_path)
		if self.status:
			if self.do_yields:
				self.define_column("weight", "1")

	def get_histogram_ptr(self, observable_name, var_to_plot, selection_name, hist_model, toGev=False):
		if self.status:
			if toGev:
				self.df[selection_name] = self.df[selection_name].Define("GeV_"+var_to_plot, f"{var_to_plot}*1e-3")
				hist = self.df[selection_name].Histo1D(hist_model, "GeV_"+var_to_plot)
			else:
				hist = self.df[selection_name].Histo1D(hist_model, var_to_plot)
			self.histos_ptr[observable_name+selection_name] = hist
			self.graphs.append(hist)

	def eval_sample_yields(self, selection_name):
			if self.status:
				if selection_name not in self.global_yields.keys():
					self.global_yields[selection_name] = {}
				if "Data" not in self.global_yields[selection_name].keys():
					self.global_yields[selection_name]["Data"] = 0
				self.sample_yields[selection_name] = self.sample_yields_ptr[selection_name].GetValue()
				# self.global_yields[selection_name][self.name] = self.sample_yields[selection_name]
				self.global_yields[selection_name]["Data"] += self.sample_yields[selection_name]

	def eval_hist_value(self, observable_name, selection_name):
		if self.status:
			self.hist = self.histos_ptr[observable_name+selection_name].GetValue()
			if self.data_hist is None:
				self.set_data_hist(self.hist.Clone("dataHist"))
				self.data_hist.SetMarkerColor(r.kBlack)
				self.data_hist.SetMarkerStyle(r.kFullDotLarge)
				self.data_hist.SetLineColor(r.kBlack)
				self.data_hist.SetLineWidth(2)
			else:
				self.data_hist.Add(self.hist)
	
	# def eval_ttbar_reweighting_histogram(self, is_ttbar=False, is_mc=False):
	# 	if not self.status:
	# 	return None
	# 	if not self.do_ttbar_reweighting:
	# 		print("TTbar reweighting is not enabled for this sample.")
	# 		return None
	# 	if "ttbar_CR" not in self.df:
	# 		print(f"ttbar_CR selection not found in {self.name}")
	# 		return None
	# 	if len(self.HThistos_ptr) == 0:
	# 		print(f"No histograms found for ttbar reweighting in {self.name}")
	# 		return None
	# 	self.HThistos = {}
	# 	for i in self.HThistos_ptr:
	# 		self.HThistos[i] = self.HThistos_ptr[i].GetValue()
	# 		if i not in self.HThistos_data:
	# 			self.HThistos_data[i] = self.HThistos[i].Clone(f"HThistos_data_{i}")
	# 		else:
	# 			self.HThistos_data[i].Add(self.HThistos[i])
	# 	return self.HThistos
