import tomllib
from pathlib import Path

TOML_TEMPLATE = """title = Super Earth Armed Forces Surplus Equipment Allocation Facility

[auth]
token = "<insert token here>"

[config]
name = "Super Earth Armed Forces Surplus Equipment Allocation Facility"
prefix = "+"

[paths]
source = "./loadout.ods"
registry = "./registered"
temp = "./tmp"

"""

CONFIG_PATH = Path('./config.toml')

def load(config_path: Path = CONFIG_PATH) -> dict:
    if not config_path.exists():
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(TOML_TEMPLATE)
        raise FileNotFoundError('No "config.toml" file was found. A new one has been created.'
                                ' Please fill out the `token` field under the `[auth]` section'
                                ' and launch the program again.')
    with open(config_path, 'rb') as f:
        return tomllib.load(f)

