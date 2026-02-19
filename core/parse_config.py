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

if __name__ == "__main__":
    file_path = 'config.yaml'  # Specify the path to your YAML file
    processed_config = load_and_process_yaml(file_path)
    print(processed_config)
