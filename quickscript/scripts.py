import argparse
import string
import inspect
import abc
import sys

from typing import (
    Type,
    Dict,
    List,
    Union,
    Literal,
    Callable
)

_SCRIPTREGISTRY = {}

class ArgumentCollector:
    DOCSTRARGSHEAD = "Args:"
    ARGHELPSEP = ": "
    def __init__(self, script, parser=None) -> None:
        super().__init__()
        self.parser = argparse.ArgumentParser() if parser is None else parser
        self.script:Script = script
        self.abstract_method_args = { # UPDATE IF additional methods requiring command line arg input are introduced
            # self.script.run:set([]),
            # self.script.setup:set([]),
            self.script.__init__:set([])
        }
        self.args = {}
        self.short_flag_taken = {k:False for k in string.ascii_lowercase}
        self.collectArgs()
        self.subparsers = {}

    def collectArgs(self):
        '''
        Automatically generate necessary arguments for some script for each abstract method.
        '''
        for method in self.abstract_method_args.keys():
            self.__addArgs(method)

    def __addArgs(self, method):
        params = inspect.signature(method).parameters
        param_help = self.__parseDocStr(inspect.getdoc(method))
        for n, p in params.items():
            if not n in ["kwargs", "self"]:
                self.__addArg(p, method, param_help[p.name])

    def __addArg(self, param, method, help):
        flags = []
        if not self.short_flag_taken[param.name[:1]]:
            flags.append('-{}'.format(param.name[:1]))
            self.short_flag_taken[param.name[:1]] = True
        flags.append('--{}'.format(param.name.replace('_','-')))
        if param._annotation is bool:
            self.parser.add_argument(
                *flags,
                action='store_true',
                help=help)
        else:
            self.parser.add_argument(
                *flags,
                action='store',
                default=param.default,
                type=param._annotation,
                help=help)
        self.abstract_method_args[method].add(param.name)

    def __parseDocStr(self, docstr:str):
        args_start_idx = docstr.index(ArgumentCollector.DOCSTRARGSHEAD)
        args = docstr[args_start_idx:]
        help = {}
        for line in args.split('\n'):
            if ArgumentCollector.ARGHELPSEP in line:
                k, h = line.split(ArgumentCollector.ARGHELPSEP)
                help[k.strip()] = h.strip()
        return help

    def getParser(self):
        return self.parser
    
    def addSubParser(self, title, name):
        if not title in self.subparsers:
            self.subparsers[title] = self.parser.add_subparsers(title=title, dest=title)
        return self.subparsers[title].add_parser(name)

    def parseArgs(self, args=None, namespace=None):
        self.args = vars(self.parser.parse_args(args, namespace))
    
    def getArgs(self, method):
        if method in self.args:
            return self.args[method]
        elif method in self.abstract_method_args:
            return {k:self.args[k] for k in self.abstract_method_args[method]}
        else:
            return {}
    
    def setAbstractMethodArgs(self, ama):
        self.abstract_method_args = ama
    
    def getAbstractMethodArgs(self):
        return self.abstract_method_args

class Script(abc.ABC):
    """
    Base class for script.

    All scripts should subclass this, and must then implement a .run method.
    A simple example is provided in ExampleScript. There, it is important to
    note the script args are provided as part of the __init__ method, should
    each be given a type hint and a default (None is OK). Further, the docstring
    must be included where an "Args:" section describes all arguments available
    for the script (which will be used in the terminal as well when "-h" is
    invoked.)
    """
    def __init__(self, args=None, namespace=None, parser=None) -> None:
        super().__init__()
        self.argCol = ArgumentCollector(self, parser=parser)
        self.args = args
        self.namespace = namespace

    def __init_subclass__(cls):
        super().__init_subclass__()
        _SCRIPTREGISTRY[cls.__name__] = cls

    @abc.abstractmethod
    def setup(self):
        raise NotImplementedError

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError

    def update(self, **kwargs):
        temp = self.__class__(**kwargs)
        for k, v in self.__dict__.items():
            self.__dict__[k] = temp.__dict__[k]

    def parseArgs(self):
        self.argCol.parseArgs(self.args, self.namespace)

    def getArgumentCollector(self):
        return self.argCol
    
    def complete_run(self):
        """
        Runs argument parser before running script.

        Useful for allowing files to run scripts dynamically from the terminal.
        """
        self.parseArgs()
        self.setup()
        self.run()

class ScriptChooser(Script):
    def __init__(self, **kwargs) -> None:
        """
        Args:
        """
        super().__init__(**kwargs)
        self.scripts:Dict[str,Script] = {
            name:script for name, script in _SCRIPTREGISTRY.items()
            if not name in ['ScriptChooser']
        }
        self.script_title = "Scripts"
        self.selected_script = None
        self.selected_script_args = None
    
    def __selectScript(self):
        self.selected_script = self.scripts[self.argCol.getArgs(self.script_title)]
        self.argCol.setAbstractMethodArgs(self.selected_script.getArgumentCollector().getAbstractMethodArgs())
        self.selected_script.update(**self.argCol.getArgs(self.selected_script.__init__))

    def setup(self):
        pass

    def run(self):
        """
        Args:
        """
        self.__selectScript()
        self.selected_script.setup()
        self.selected_script.run(**self.argCol.getArgs(self.selected_script.run))

    def parseArgs(self):
        for n, scr in self.scripts.items():
            temp_parse = self.argCol.addSubParser(self.script_title, n)
            self.scripts[n] = scr(parser=temp_parse)
        super().parseArgs()

class ExampleScript(Script):
    def __init__(
            self,
            name:str = "World",
            **kwargs) -> None:
        """
        An example of how to subclass Script.

        Args:
            name: person to which hello should be said.
        """
        super().__init__(**kwargs)
        self.name = name
    
    def setup(self):
        pass
    
    def run(self):
        print("Hello, {}".format(self.name))


if __name__ == "__main__":
    x = ScriptChooser()
    x.complete_run()
    pass