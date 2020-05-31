import ast
import configparser
import os
from pathlib import Path
from typing import Tuple, List


def literal_eval(func):
    def wrapper(*args, **kwargs):
        orig_result = func(*args, **kwargs)
        return ast.literal_eval(orig_result)

    return wrapper


class Section:
    def __init__(self, config_parser: configparser.ConfigParser, section_name):
        self._name = section_name
        self._parser = config_parser
        self._raw_contents = config_parser[section_name]
        self._options = []
        self._parser_func_map = {
            'i': self._parser.getint,
            'f': self._parser.getfloat,
            'b': self._parser.getboolean,
            'e': literal_eval(self._parser.get),
            's': self._parser.get,
        }

        for key in self._raw_contents:
            parsed_key, parsed_value = self.parse_raw_option(self._name, key)
            self.set_option(parsed_key, parsed_value, append_key=True)

    def get_raw_contents(self):
        return self._raw_contents

    def get_options_list(self):
        return self._options

    def get_name(self):
        return self._name

    def set_option(self, key, value, append_key=False):
        setattr(self, key, value)
        if append_key:
            self._options.append(key)

    def get_option(self, key):
        return getattr(self, key, None)

    def parse_raw_option(self, sect_name: str, opt_key: str, mode='s') -> Tuple:
        if opt_key[1] == ',':
            mode = opt_key[0]
            parsed_key = opt_key[2:]
        else:
            parsed_key = opt_key
        get_func = self._parser_func_map[mode]
        parsed_value = get_func(sect_name, opt_key)
        return parsed_key, parsed_value

    def override_with(self, section):
        for key in section.get_options_list():
            value = section.get_option(key)
            self.set_option(key, value, append_key=key not in self.get_options_list())


class Config:
    def __init__(self, path=None):
        self._path = path
        self._sections = []
        self._section_names = []
        self._loaded_configs_list = []
        self._configparser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        self._parsers = [self._configparser, ]
        if path is not None:
            self._configparser.read(path)
            self.dynamic_load_sections(self._configparser)
            self._loaded_configs_list.append(path)

    def __repr__(self):
        repr_str = 'Loaded configs: '
        for conf_path in self._loaded_configs_list:
            repr_str += f'\n{conf_path}'
        for section in self._sections:
            repr_str += f'\n[{section.get_name()}]\n'
            for key in section.get_options_list():
                repr_str += f'    {key}={section.get_option(key)}\n'
        return repr_str

    def get_path(self) -> str:
        return self._path

    def get_parser(self) -> configparser.ConfigParser:
        return self._configparser

    def get_section(self, section_name) -> Section:
        return getattr(self, section_name, None)

    def set_section(self, section):
        self._sections.append(section)
        self._section_names.append(section.get_name())
        setattr(self, section.get_name(), section)

    def get_sections(self) -> List:
        return self._sections

    def get_section_names(self) -> List:
        return self._section_names

    def dynamic_load_sections(self, parser):
        for section_name in parser.sections():
            section = Section(parser, section_name)
            self.set_section(section)

    def override_with(self, conf):
        for section_name in conf.get_section_names():
            if section_name not in self._section_names:
                section = conf.get_section(section_name)
                self.set_section(section)
            else:
                self.get_section(section_name).override_with(conf.get_section(section_name))
        self._parsers.append(conf.get_parser())
        self._loaded_configs_list.append(conf.get_path())


class ConfigDirNotExistsError(BaseException):
    """app_dir/config directory does not exist"""


class DefaultConfigDirNotExistsError(BaseException):
    """app_dir/defaults directory does not exist"""


class ConfigManager:
    def __init__(self, debug):
        if debug:
            app_dir = str(Path(os.path.dirname(__file__)).parent)
        else:
            app_dir = os.getcwd()

        self.path_defaults = app_dir + '/defaults/'
        self.path_configs = app_dir + '/config/'
        if not os.path.exists(self.path_defaults):
            raise DefaultConfigDirNotExistsError()
        if not os.path.exists(self.path_configs):
            raise ConfigDirNotExistsError()

        self.config = Config()
        # load default config
        self.load_from_dir(self.path_defaults)
        # load env configs
        self.load_from_dir(self.path_configs)

    def load_from_dir(self, directory):
        path_list = []
        (dirpath, _, filenames) = next(os.walk(directory))
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            path_list.append(filepath)
        path_list.sort()
        for path in path_list:
            conf = Config(path)
            self.config.override_with(conf)
