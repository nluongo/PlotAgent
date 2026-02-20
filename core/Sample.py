import os
import ROOT as r
from datetime import datetime

class _CachedHistWrapper:
	"""Wraps a pre-computed histogram clone so it looks like an RDF lazy result.
	Allows inject_cached_histogram() to be transparent to eval_hist_value()."""
	def __init__(self, hist):
		self._hist = hist

	def GetValue(self):
		return self._hist


class Sample:
	graphs = []
	do_yields = False
	yields = None
	do_ttbar_reweighting_calc = False

	@classmethod
	def init_yields(cls):
		cls.do_yields = True
		cls.global_yields = {}
		cls.ttbar_reweighting_normalization = 1
		# cls.ttbar_reweighting_norms = {
		# 	2: 0.86,
		# 	3: 0.88,
		# 	4: 0.90,
		# 	5: 0.92,
		# 	6: 0.95,
		# 	7: 1.01,
		# 	8: 1.07,
		# 	9: 1.16,
		# 	10: 1.19,
		# }
	
	@classmethod
	def setup_ttbar_reweighting_calc(cls):
		cls.do_ttbar_reweighting_calc = True
		cls.mc_yield_wo_ttbar = 0
		cls.HThistos_background = {}
		cls.HThistos_data = {}
	
	@classmethod
	def set_mc_yield_wo_ttbar(cls, yield_value):
		cls.mc_yield_wo_ttbar = yield_value
	
	@classmethod
	def calc_ttbar_reweighting_normalization(cls):
		if cls.do_ttbar_reweighting_calc:
			if "ttbar_CR" in cls.global_yields:
				cls.ttbar_reweighting_normalization = (cls.global_yields["ttbar_CR"]["Data"] - cls.mc_yield_wo_ttbar) / cls.global_yields["ttbar_CR"]["ttbar"]
				print(f"Data yield in ttbar_CR: {cls.global_yields['ttbar_CR']['Data']}")
				print(f"ttbar yield in ttbar_CR: {cls.global_yields['ttbar_CR']['ttbar']}")
				print(f"MC yield without ttbar in ttbar_CR: {cls.mc_yield_wo_ttbar}")
				print(f"ttbar reweighting normalization: {cls.ttbar_reweighting_normalization}")
			else:
				print(f"ttbar_CR not found in config for ttbar reweighting normalization")
				cls.ttbar_reweighting_normalization = 1
		else:
			cls.ttbar_reweighting_normalization = 1
	
	@classmethod
	def evaluate_ttbar_reweighting(cls, run):
		if cls.do_ttbar_reweighting_calc:
			# Save the ttbar reweighting normlization factor to ROOT file
			root_file = r.TFile(f"ttbar_reweighting_histograms_Run{run}.root", "RECREATE")
			normalization = r.TH1F("ttbar_reweighting_normalization", "TTbar reweighting normalization", 1, 0, 1)
			normalization.SetBinContent(1, cls.ttbar_reweighting_normalization)
			print(f"Writing ttbar reweighting normalization: {cls.ttbar_reweighting_normalization}")
			normalization.SetDirectory(root_file)
			normalization.Write()
			# Write the histograms for ttbar reweighting
			for i in cls.HThistos_background:
				reweighting_hist = cls.HThistos_data[i].Clone(f"ttbar_reweighting_hist_{i}_nJets")
				reweighting_hist.Divide(cls.HThistos_background[i])
				bins = []
				for j in range(1, reweighting_hist.GetNbinsX() + 1):
					if reweighting_hist.GetBinContent(j) == 0:
						reweighting_hist.SetBinContent(j, 1)
					bins.append(reweighting_hist.GetBinContent(j))
				bins_formatted = ', '.join(f'{b:.3f}' for b in bins)
				print(f"{i} Jets : [{bins_formatted}]")
				reweighting_hist.SetDirectory(root_file)
				reweighting_hist.Write()
			root_file.Close()
		else:
			print("TTbar reweighting is not enabled for this sample.")

	@classmethod
	def runGraphs(cls):
		r.RDF.RunGraphs(cls.graphs)
	
	@classmethod
	def write_yields_txt(cls, blind=1):
		time = datetime.now().strftime("%Y-%m-%d")
		yield_fname = f"yields_{time}.txt"
		#Create basic yields text file
		with open(yield_fname, "w") as f:
			f.write("Selection\tSample\tYield\n")
			#write yields
			for selection in cls.global_yields:
				for sample in cls.global_yields[selection]:
					if blind and sample == 'Data':
						f.write(f"{selection}\t{sample}\t(BLIND)\n")
					else:
						f.write(f"{selection}\t{sample}\t{cls.global_yields[selection][sample]}\n")
	
	@classmethod
	def process_yield(cls, process_name, blind=1):
		line = f'{process_name} '
		for selection in cls.global_yields:
			if blind and process_name == 'Data':
				n_events = -1
				line += f'& -'
			else:
				n_events = cls.global_yields[selection][process_name]
				line += f'& {n_events:.3f}'

		line += ' \\\\\n'
		return line

	@classmethod
	def write_yields_tex(cls, signal_map, histomap, blind=1):
		#Create local copy of global yields
		event_yields = cls.global_yields
		#Create tex yields file
		time = datetime.now().strftime("%Y-%m-%d")
		tex_fname = f"yields_{time}.tex"
		with open(tex_fname, "w") as f:
			# Create header
			column_string = '{l' + '|r'*len(event_yields) + '}'
			header = r'''\documentclass[varwidth=\maxdimen]{standalone}
\begin{document}
\begin{table}
\begin{tabular}''' + column_string + '\n'
    		# Create footer
			footer = r'''\end{tabular}
\end{table}
\end{document}'''
			f.write(header)

			# Create first line holding regions
			top_line = ' '
			for selection in event_yields:
				test_sel = selection
				selection = selection.replace('_', '\_')
				top_line += f'& {selection} '
			top_line += ' \\\\ \hline\n'
			f.write(top_line)

			if 'Data' in event_yields[test_sel]:
				line = cls.process_yield('Data', blind)
				f.write(line)
			if 'Background' in event_yields[test_sel]:
				line = cls.process_yield('Background')
				f.write(line)
			
			f.write('\hline\n')

			for sig in signal_map:
				line = cls.process_yield(sig)
				f.write(line)
			for sample in histomap:
				line = cls.process_yield(sample)
				f.write(line)
			
			f.write(footer)
			f.close()

	def __init__(self, name, file_path):
		self.name = name
		self.file_path = file_path
		self.df = {}
		self.status = False
		self.histos_ptr = {}
		if self.do_yields:
			self.sample_yields_ptr = {}
			self.sample_yields = {}
		try:
			self.tfile = r.TFile(file_path, "READ")
			self.ttree = self.tfile.AnalysisMiniTree
			self.status = self.check_columns(self.ttree)
		except:
			self.status = False
			print(f"Failed to open file {file_path}") 
		if self.status:
			self.df["0"] = r.RDataFrame("AnalysisMiniTree", file_path)
		else:
			print(f"{self.name} has no columns in the file {file_path}")
			self.df = {}
			self.hist = None

	def check_columns(self, ttree):
		# No branches implies no events in TTree
		if len(ttree.GetListOfBranches()) > 0:
			return True
		else:
			return False

	def define_column(self, column_name, column_expr):
		if self.status:
			if column_name in self.df["0"].GetColumnNames():
				self.df["0"] = self.df["0"].Redefine(column_name, column_expr)
			else:
				self.df["0"] = self.df["0"].Define(column_name, column_expr)

	def apply_selection(self, selection_name, selection):
		if self.status:
			self.df[selection_name] = self.df["0"].Filter(selection)

	def set_sample_yields(self, selection, weight="weight"):
		if self.status:
			self.sample_yields_ptr[selection] = self.df[selection].Sum(weight)
			self.graphs.append(self.sample_yields_ptr[selection])

	def event_sum(self, selection, weighted=1, weight="weight"):
		if not self.status:
			return 0
		if weighted:
			events = self.df[selection].Sum(weight).GetValue()
		else:
			events = self.df[selection].Count().GetValue()
		return events

	def load_cutflows(self):
		self.abs_efficiency = self.tfile.Get("AbsoluteEfficiency")
		self.rel_efficiency = self.tfile.Get("RelativeEfficiency")
		self.standard_cutflow = self.tfile.Get("StandardCutFlow")
		if not self.standard_cutflow:
			print(f'Did not find StandardCutFlow for {self.file_path}')
		self.events_passed = self.tfile.Get("EventsPassed_BinLabeling")

	def queue_ttbar_reweighting_yields(self, hist_models, weight=None, nJets=15):
		self.HThistos_ptr = {}
		if not self.status:
			return
		if "ttbar_CR" not in self.df:
			print(f"ttbar_CR selection not found in {self.name}")
			return
		if "bbll_nJets_NOSYS" in self.df["ttbar_CR"].GetColumnNames() and "bbll_HT2_NOSYS" in self.df["ttbar_CR"].GetColumnNames():
			for i in range(2, nJets + 1):
				df_njet_filtered = self.df["ttbar_CR"].Filter(f"bbll_nJets_NOSYS == {i}")
				self.HThistos_ptr[i] = (
					df_njet_filtered.Histo1D(hist_models[i], "bbll_HT2_NOSYS", weight)
				)
				self.graphs.append(self.HThistos_ptr[i])
		else:
			print(f"bbll_nJets_NOSYS or bbll_HT2_NOSYS not found in {self.name}")
			return

	def eval_ttbar_reweighting_histogram(self, is_ttbar=False, is_mc=False):
		if not self.status:
			return None
		if not self.do_ttbar_reweighting_calc:
			print("TTbar reweighting is not enabled for this sample.")
			return None
		if "ttbar_CR" not in self.df:
			print(f"ttbar_CR selection not found in {self.name}")
			return None
		if len(self.HThistos_ptr) == 0:
			print(f"No histograms found for ttbar reweighting in {self.name}")
			return None
		self.HThistos = {}
		for i in self.HThistos_ptr:
			self.HThistos[i] = self.HThistos_ptr[i].GetValue()
			if is_ttbar:
				self.HThistos[i].Scale(self.ttbar_reweighting_normalization)
			# if is_mc:
				if i not in self.HThistos_background:
					self.HThistos_background[i] = self.HThistos[i].Clone(f"HThistos_background_{i}")
				else:
					self.HThistos_background[i].Add(self.HThistos[i])
			else:
				if i not in self.HThistos_data:
					if is_mc:
						self.HThistos_data[i] = self.HThistos[i].Clone(f"HThistos_data_{i}")
						self.HThistos_data[i].Reset()
						self.HThistos_data[i].Sumw2()
						self.HThistos_data[i].Add(self.HThistos[i], -1.0)
					else:
						self.HThistos_data[i] = self.HThistos[i].Clone(f"HThistos_data_{i}")
				else:
					if is_mc:
						self.HThistos_data[i].Add(self.HThistos[i], -1.0)
					else:
						self.HThistos_data[i].Add(self.HThistos[i])
				# if i not in self.HThistos_data:
				# 	self.HThistos_data[i] = self.HThistos[i].Clone(f"HThistos_data_{i}")
				# else:
				# 	self.HThistos_data[i].Add(self.HThistos[i])
		return self.HThistos

	def inject_cached_histogram(self, observable_name, selection_name, cached_hist):
		"""Store a pre-computed histogram so eval_hist_value() can use it without
		calling get_histogram_ptr() or touching the RDF graph."""
		key = observable_name + selection_name
		self.histos_ptr[key] = _CachedHistWrapper(cached_hist)

	def get_computed_histogram(self, observable_name, selection_name):
		"""Return a detached clone of the histogram computed by get_histogram_ptr().
		Returns None if this slot was already filled by inject_cached_histogram()
		(i.e., it was a cache hit and there is nothing new to store)."""
		key = observable_name + selection_name
		entry = self.histos_ptr.get(key)
		if entry is None or isinstance(entry, _CachedHistWrapper):
			return None
		h = entry.GetValue().Clone()
		h.SetDirectory(0)
		return h
