import os
import yaml
import re

def substitute_vars(config):
    """
    Recursively substitutes variables in the config dictionary.
    """
    def substitute(value, variables):
        """
        Substitute variables in a single value.
        """
        if isinstance(value, str):
            # Substitute variables in the form of $var$
            matches = re.findall(r'\$(\w+)\$', value)
            for match in matches:
                if match in variables:
                    value = value.replace(f'${match}$', variables[match])
        return value

    def recursive_substitute(data, variables):
        """
        Recursively substitute variables in all values of the data.
        """
        if isinstance(data, dict):
            # Create a new copy of the variables dictionary for each nested dictionary
            new_variables = variables.copy()
            new_variables.update(data)
            return {substitute(k, new_variables): recursive_substitute(substitute(v, new_variables), new_variables) for k, v in data.items()}
        elif isinstance(data, list):
            return [recursive_substitute(substitute(item, variables), variables) for item in data]
        else:
            return substitute(data, variables)
    
    return recursive_substitute(config, config)

def load_and_process_yaml(file_path):
    """
    Load a YAML file, process it to substitute variables, and return the result.
    """
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return substitute_vars(config)

def _deep_merge(base, override):
    """
    Recursively merge `override` into `base`. Dicts are merged recursively;
    all other types (including lists) are replaced by the override value.
    """
    result = base.copy()
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


def _apply_defaults(section, defaults):
    """
    For each entry in `section` (a dict of dicts), fill missing keys from `defaults`.
    Used to apply plots.yaml defaults to each variable definition.
    """
    out = {}
    for name, spec in section.items():
        merged = defaults.copy()
        if spec:
            merged.update(spec)
        out[name] = merged
    return out


def load_split_configs(include_paths, base_dir):
    """
    Load a list of auxiliary YAML files and deep-merge their contents into a
    single namespace dict. Variable substitution is applied after merging so
    $var$ references in auxiliary files can reference variables from any file.

    Returns a dict with top-level keys from all included files
    (e.g. 'samples', 'stacks', 'variables', 'selections', 'campaigns', etc.).
    """
    merged = {}
    for rel_path in include_paths:
        abs_path = os.path.join(base_dir, rel_path)
        with open(abs_path, 'r') as f:
            data = yaml.safe_load(f)
        if data:
            merged = _deep_merge(merged, data)

    merged = substitute_vars(merged)

    # Apply per-variable defaults from plots.yaml
    if 'variables' in merged and 'defaults' in merged:
        plot_defaults = merged.pop('defaults')
        merged['variables'] = _apply_defaults(merged['variables'], plot_defaults)

    return merged


def load_config(config_path):
    """
    Primary entry point — replaces the direct load_and_process_yaml() call in
    makePlot.py.

    If the config contains an `includes:` list, loads each referenced YAML file
    (relative to config_path's directory), deep-merges them, applies variable
    substitution, and injects the merged sections into the config dict under
    private keys (_samples_config, _stacks_config, _variables_config,
    _selections_config, _campaigns_config, _data_campaigns_config,
    _luminosity_config).

    If no `includes:` key is present, behaviour is identical to the old
    load_and_process_yaml() — full backward compatibility.
    """
    base_dir = os.path.dirname(os.path.abspath(config_path))
    raw_config = load_and_process_yaml(config_path)

    # Support `includes:` at either the top level or nested under `makePlot:`
    top = raw_config.get('makePlot', raw_config)
    include_paths = top.pop('includes', [])

    if not include_paths:
        return raw_config

    aux = load_split_configs(include_paths, base_dir)

    # Inject auxiliary sections as private keys so main1D() can detect them
    top['_samples_config'] = aux.get('samples', {})
    top['_stacks_config'] = aux.get('stacks', {})
    top['_variables_config'] = aux.get('variables', {})
    top['_selections_config'] = aux.get('selections', {})
    top['_campaigns_config'] = aux.get('campaigns', {})
    top['_data_campaigns_config'] = aux.get('data_campaigns', {})
    top['_luminosity_config'] = aux.get('luminosity', {})

    return raw_config


if __name__ == "__main__":
    file_path = 'config.yaml'  # Specify the path to your YAML file
    processed_config = load_and_process_yaml(file_path)
    print(processed_config)
