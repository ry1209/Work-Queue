import configparser
import ast

class Config:
    def __init__(self, config_path : str = r'./setting.conf'):
        config = configparser.ConfigParser()
        config.read(config_path)
        self.config_dict = dict()
        for section in config.sections():
            self.config_dict[section] = {}
            for option in config.options(section):
                self.config_dict[section][option] = ast.literal_eval(config.get(section, option))

config = Config()
config = config.config_dict