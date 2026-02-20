# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a HEP (High Energy Physics) plotting tool for the HH→bbll+Etmiss analysis at ATLAS. It uses ROOT/PyROOT and requires an Athena release <= 25.0.24.

## Running the Tool

```bash
# Basic run with ratio plot and signal
python3 makePlot.py -r -s

# Full argument reference
python3 makePlot.py \
  -c config.yaml       # config file (default: config.yaml)
  -m                   # MC only (no data)
  -r                   # include ratio plot
  -s                   # include signal
  -l                   # log scale y-axis
  -y                   # produce yields (txt + tex)
  -oy                  # old yields method
  -np                  # no plots (use with -oy for yields only)
  -rs [2|3|23]         # Run2, Run3, or combined (default: 2)
  -UB                  # unblind data (prompts confirmation)

# Generate FastFrames file listing
python3 GetFastFrameFiles.py --input_dir <path/to/root/files/> --output_file <output.json>
```

There are no automated tests or linting tools configured.

## Architecture

### Data Flow

1. **Config parsing** (`core/parse_config.py`) — loads YAML with `$var$` variable substitution
2. **Sample instantiation** — creates `MC` and `Data` objects from ROOT files
3. **Selection + histogramming** — applies cuts via ROOT RDataFrame (`.Filter()`, `Histo1D()`)
4. **Styling + stacking** — `core/utils.py` handles pad layout, legends, ATLAS labels
5. **Output** — saves PNG/PDF plots; optionally writes yields to TXT/LaTeX

### Key Files

- **`makePlot.py`** — main entry point; `main1D()` orchestrates the full pipeline; `argument_parser()` defines CLI
- **`histoDict.py`** — central registry of all samples (`SampleDict_run2/3`), histograms (`PlottingDict`), signals (`SignalDict`), and selections (`SelectionDict`)
- **`PlottingList.py`** — maps sample/campaign names to dataset IDs (not needed when `fastframes_input` is enabled)
- **`core/Sample.py`** — base class; manages yields, ttbar reweighting, ROOT graph lifecycle
- **`core/MC.py`** — extends `Sample`; manages histogram stacks, significance ratios, ttbar reweighting weight functions (C++ via ROOT)
- **`core/Data.py`** — extends `Sample`; handles data histogram aggregation and blinding
- **`core/utils.py`** — shared plotting utilities: pad creation, legend setup, histogram styling/rebinning, ATLAS labels, yield formatting
- **`AtlasStyle/`** — C++ macros for ATLAS visual style; compiled separately via `AtlasStyle/makefile`

### Two Input Modes

**Traditional ntuples** (`fastframes_input: false`): ROOT files discovered via `PlottingList.py` sample/campaign maps + `input_path` from config.

**FastFrames output** (`fastframes_input: true`): ROOT files listed in a JSON produced by `GetFastFrameFiles.py`; `samplelist_path` must point to the JSON. `PlottingList.py` is not used.

### Extending the Tool

- **Add a sample**: add an entry to `SampleDict_run2()` or `SampleDict_run3()` in `histoDict.py`, and (for traditional mode) add to `sample_map` in `PlottingList.py`
- **Add a histogram variable**: add an entry to `PlottingDict()` in `histoDict.py`; key must match a branch name in the ntuples
- **Add a selection**: add to `SelectionDict()` in `histoDict.py` or under `customSelection` in `config.yaml`
- **Add a signal**: add to `SignalDict()` in `histoDict.py` and reference it under `signalName` in `config.yaml`

Custom selections and histograms can also be defined directly in the YAML config under `customSelection` and `customHists` without modifying `histoDict.py`.

## Long-Term Vision: AI Agent Workflow

The project is being refactored so that all sample definitions, histogram parameters, selections, colors, and legends live in YAML config files (`configs/samples.yaml`, `configs/plots.yaml`, `configs/selections.yaml`) rather than hard-coded Python. This enables an AI agent workflow:

1. Agent runs `makePlot.py` to generate output plots
2. Agent reads the output images and identifies issues (e.g., data outside axis bounds, overlapping labels)
3. Agent modifies the relevant YAML config entry (e.g., increases `x-max` in `plots.yaml`)
4. Agent re-runs `makePlot.py`; only plots whose config hash changed are regenerated (others are skipped)

The refactoring is incremental — `histoDict.py` and `PlottingList.py` remain as fallbacks while YAML files are being populated.
