# bbll Analysis Plotting Tool

**Note: This README needs to be updated**

*Plotting script inspired by the bbyy analysis*

The bbll Analysis Plotting Tool is a script that allows you to generate high-quality plots for the HH->bbll+Etmiss analysis. It provides a flexible and customizable way to visualize your data, allowing you to specify various parameters. The tool relies on a yaml configuration file to define these parameters.

You can customize the behavior of the script by providing command-line arguments. For example, you can specify the path to the config file using the `-c` or `--config` argument. By default, the script uses `config.yaml` as the config file.

The `makePlot.py` script relies on a yaml configuration file to define various parameters. You can specify the username, version, input and output paths, weight and scale factors, signal names, samples to stack, selections to apply, and variables to plot. The configuration file also supports the use of variables defined earlier in the file, allowing for easy reuse and flexibility.

In addition to the configuration file, you can define custom selections and histograms in the `config.yaml` file. Custom selections allow you to define specific criteria for your data, while custom histograms allow you to define the properties of the plots. You can specify the x-axis title, units, range, number of bins, and whether to convert the x-axis values to GeV.

For even more customization options, you can modify the `histoDict.py` file. This file contains dictionaries that define the properties of each sample, histogram, signal, and selection. You can add new samples, modify existing ones, and define the properties of each histogram. The `PlottingList.py` script also provides dictionaries to map sample and campaign names to their corresponding dataset names.

The PlottingTool can be used to plot FastFrames output from the FastFramesbbll framework. The `GetFastFramesFiles.py` script can be used to create a json with all the paths to your FastFrames output. This json can then be used in your config file for the PlottingTool to use. Note that in order for the tool to use the FastFrames out the `fastframes_input` option must be enabled.

## Running Tool

`makePlot.py` is the main Python script that generates the plots. It takes several command-line arguments that allow you to customize its behavior.

Usage
PLEASE use Athena releases <= 25.0.24

To run `makePlot.py`, use the following command (see example.sh):

```shell
python3 makePlot.py [arguments]
```

Arguments
- `-c` or `--config`: Specifies the path to the config file. The default is `config.yaml`.
- `-m` or `--mcOnly`: The script will only use Monte Carlo data.
- `-r` or `--include_ratio`: The script will include a ratio plot.
- `-s` or `--dosignal`: The script will include a signal in the plot.
- `-l` or `--logOn`: The script will use a logarithmic scale for the y-axis.
- `-t` or `--twoDim`: The script will produce a 2D plot. [NOT IMPLEMENTED YET]
- `-y` or `--yields`: The script will produce a txt and tex with the yields of the various samples.
- `-oy` or `--old-yields`: The script will use an older method to produce a txt and tex with the yields of the various samples.
- `-np` or `--noPlots`: Run plotting tool without producing plots. This can be used with the older yields method to just produce yields. Note: this option doesn't currently work with the newer yields calculation method.
- `-rs` or `--runs`: The script will produce either Run2, Run3 or Run2+Run3 plots (2, 3, or 23",default="2")
- `-UB` or `--UNBLIND`: The script will unblind the data. The tool will prompt you to confirm if you actually want to do this or not, if you do answer 'yes'.

### Example

Here's an example of how to run makePlot.py with some arguments:

```shell
python3 makePlot.py -c my_config.yaml -s -r
```

This command will run makePlot.py with the config file my_config.yaml, using only Monte Carlo data, including a signal, and using a logarithmic scale for the y-axis.

## Configuration of tool

A yaml configuration file is used to define various parameters for the `makePlot.py` script. Here's a breakdown of what each entry means:

- `user_name`: The username of the person running the script (e.g. "user.giuseppe").
- `version`: The version of the script being run (e.g. "v2"). [NOT USED]
- `BLIND_THRESHOLD`: The threshold for blinding data.
- `fastframes_input`: The tool will be configured for processing FastFrames output.
- `samplelist_path`: The path to the json file produced by the GetFastFramesFiles.py script. Note: this option must be used when `fastframes_input` is enabled.
- `input_path`: The path to the input data.
- `output_path`: The path where the output plots will be saved.
- `weight_factor`: A list of branches in the ntuples to be used when caclculating the weight. The weight will be calculated from the product of each branch given, or if the branch is given as "1/BRANCH_NAME" then the inverse of that branch will be used instead. The `$var$` syntax can be used if branch names are defined earlier in the yaml file.
- `scale_factor`: A list of branches in the ntuples to be used when caclculating the scale factor. The scale factor will be calculated from the product of each branch given, or if the branch is given as "1/BRANCH_NAME" then the inverse of that branch will be used instead. The `$var$` syntax can be used if branch names are defined earlier in the yaml file.
- `signalName`: A list of signal names. Must be used as a 'histoname' for plots in histoDict.py.
- `samplesToStack`: A list of sample names to be stacked in the plot. Must be used as a 'histoname' for plots in histoDict.py.
- `customCutPerSample`: Perform custom cuts on specific samples.
- `customCutPerStack`: Perform custom cuts on specific samples.
- `selectionToPlot`: A list of selections to be applied to the ntuples for plotting. It should be a list of names that correspond to selections defined within the config file under `customSelection`, or within histoDict.py under `SelectionDict`.
- `histosToPlot`: A list of variables corresponding to branches within the ntuples to be plotted. It should be a list of names that correspond to variables defined within the config file under `customHists`, or within `histoDict.py` under `PlottingDict`.

The `$var$` syntax is used to denote variable names. When the script sees a string enclosed in `$` signs, it replaces it with the value of the variable. For example, if `Lumi` is `"Luminosity"`, then `$Lumi$` would be replaced with `Luminosity`. This allows you to define variables in one place and then use them in multiple places in the configuration file.

For an example of how this can be done, see `config.yaml`.

## Custom Selections and Histograms

When creating your yaml file, you can define custom selections and histograms for your data.

### Custom Selections

Under the customSelection key, you can define a set of selection criteria for your data. Each selection is defined by a unique name and a set of properties:

- `legend upper`: The text that will appear in the upper legend for this selection.
- `legend lower`: The text that will appear in the lower legend for this selection.
- `cuts`: A list of cuts to apply to the data. Each cut is a string that represents a condition that the data must meet. The `$var$` syntax can be used to denote variable names.

For example, the `NW_weight_selection` entry defines a selection where the NW_weight is less than 0.

### Custom Histograms

Under the customHists key, you can definef histograms to be plotted. Each histogram is defined by the name of the variable to be plotted and a set of properties:

- `x-axis title`: The title of the x-axis for this histogram.
- `units`: The units for the x-axis values.
- `x-min`: The minimum x-axis value for this histogram.
- `x-max`: The maximum x-axis value for this histogram.
- `nBins`: The number of bins for this histogram.
- `toGeV`: A boolean indicating whether to convert the x-axis values to GeV.

For example, the `$NW_weight$` entry defines a histogram with the NW_weight on the x-axis, no units, x-axis values ranging from -2 to 1, 50 bins, and no conversion to GeV.

## More configuration options with histoDict.py

### SampleDict

The `SampleDict()` function returns a dictionary where each key is a sample name and each value is another dictionary that defines the properties of the histogram for that sample:

- `histoname`: The name of the histogram.
- `color`: The color of the histogram, represented as an RGB tuple.
- `legend description`: The description of the histogram that will appear in the legend.

To add a new sample, simply add a new key to the dictionary and define the properties of the histogram for that sample. For example, to add a sample named 'bbWW_500', you would add the following entry:

```python
'bbWW_500':
{
    'histoname': 'HH',
    'color': (227, 73, 102),
    'legend description': '#it{bbWW_500GeV}'
},
```

To modify an existing sample, simply change the values of the properties in the dictionary for that sample. For example, to change the color of the 'bbWW_1000' sample, you would change the 'color' entry:

```python
'bbWW_1000':
{
    'histoname': 'HH',
    'color': (0, 0, 255),  # Change this to the desired color
    'legend description': '#it{bbWW_1000GeV}'
},
```

Please note that the color is represented as an RGB tuple, where each value is between 0 and 255. The 'legend description' supports LaTeX syntax for mathematical symbols and italics.

### PlottingDict

The main dictionary returned by `PlottingDict()` defines the properties of each histogram:

- `x-axis title`: The title of the x-axis for this histogram.
- `units`: The units for the x-axis values.
- `x-min`: The minimum x-axis value for this histogram.
- `x-max`: The maximum x-axis value for this histogram.
- `nBins`: The number of bins for this histogram.
- `toGeV`: A boolean indicating whether to convert the x-axis values to GeV.

To add a new histogram, simply add a new key to the dictionary and define the properties of the histogram. For example, to add a histogram named 'bbll_mbbllmet_NOSYS', you would add the following entry:

```python
'bbll_mbbllmet_NOSYS': { 
    'x-axis title': '#it{m_{bbll}+MET} [GeV]',
    'units' : 'GeV',
    'x-min' : 100,
    'x-max' : 1500,
    'nBins' : 30,
    'toGeV' : True
}
```

Note: the name of the key must be a valid branch name in your ntuples.

### SignalDict

The `SignalDict()` function returns a dictionary that defines the properties of each signal:

- `legend description`: The description of the signal that will appear in the legend.
- `color`: The color of the signal, represented as an RGB tuple.
- `multiplier`: The multiplier for the signal.

To add a new signal, simply add a new key to the dictionary and define the properties of the signal. For example, to add a signal named 'HH', you would add the following entry:

```python
'HH': {
    'legend description': 'HH(b#bar{b}ll)',
    'color': (227, 73, 102),
    'multiplier': 1000
}
```

### SelectionDict

The SelectionDict() function returns a dictionary that defines the properties of each selection:

- `legend upper`: The text that will appear in the upper legend for this selection.
- `legend lower`: The text that will appear in the lower legend for this selection.
- `cuts`: A list of cuts to apply to the data. Each cut is a string that represents a condition that the data must meet.

To add a new selection, simply add a new key to the dictionary and define the properties of the selection. For example, to add a selection named 'preselection', you would add the following entry:

```python
'preselection': {
    'legend upper': 'OS and SF leptons',
    'legend lower': '',
    'cuts': ['(bbll_TWO_OPPOSITE_CHARGE_LEPTONS_NOSYS && bbll_IS_SF_NOSYS)']
}
```
### Plotting FastFrames Output 

The PlottingTool has a specific configuration when plotting FastFrames output. First, the `GetFastFrameFile.py` script should be run to fetch all the paths to the various samples and save them to a json. The script has the following arguments:

- `--input_dir`: input directory containing FastFrames root files.
- `--output_file`: output file to save the list of root files.

Example:
```bash
python3 GetFastFrameFiles.py --input_dir <path/to/your/root/files/> --output_file <path/to/save/output/>
```

The `fastframes_input` option must be enabled within your config file to use the FastFrames configuration of the PlottingTool. Additionally, the `sampleslist_path` should be set to the path to your output from `GetFastFrameFiles.py`. Note that this configuration does not require the `PlottingList.py` file for plotting.

### Configurations in PlottingList.py (Not Needed when using FastFrames Ouput)

This Python script contains three dictionaries: sample_map, campaign_map and data_campaign_map. These dictionaries are used to map the names of samples and campaigns to their corresponding dataset names in the common folder.

#### sample_map

The `sample_map` dictionary maps the names of samples to their corresponding dataset names. Each key is a sample name and each value is a dataset name. For example, the key 'ttbar' maps to the dataset name '410472.e6337_s3681'.

```python
sample_map = {
    "ttbar": "410472.e6337_s3681",
    "Zee+jet_Bfilt": "700320.e8351_s3681",
    ...
}
```

When adding a new sample to `sample_map`, make sure that the key matches the name of the sample in `histoDict.py`. This is because the plotting script uses the keys in `sample_map` to look up the properties of the histograms in `histoDict.py`.

#### campaign_map

The `campaign_map` dictionary maps the names of campaigns to their corresponding dataset names. Each key is a campaign name and each value is a dataset name. For example, the key 'a' maps to the dataset name 'r13167_p6026'.

```python
campaign_map = {
    "a": "r13167_p6026",
    "d": "r13144_p6026",
    ...
}
```

When adding a new campaign to `campaign_map`, make sure that the key matches the name of the campaign in your data. This is because the plotting script uses the keys in `campaign_map` to look up the datasets for each campaign.

#### data_campaign_map

The `data_campaign_map` dictionary is another mapping tool, similar to `campaign_map`. It maps the names of data campaigns to their corresponding dataset names. Each key is a data campaign name and each value is a dataset name.

```python
data_campaign_map = {
    "data15": "r9264",
    "data16": "r9264",
    ...
}
```

When adding a new data campaign to `data_campaign_map`, ensure the key accurately represents the data campaign in your dataset. The plotting script will use these keys to retrieve the appropriate datasets for each data campaign.

### getCutflow.py Script
NEED TO WRITE