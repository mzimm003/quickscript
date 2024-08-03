# quickscript
Quickly configure a script runnable by terminal or as a class within python.

## Overview
A script should be represented as a class subclassing Script.

The __init__ method will take all args important to the script’s flexibility.
The args must be type hinted, and described in the __init__ method’s docstring
indented under an “Args:” section. Arguments provided to the __init__ method
should not be initialized. Instead, the class and its configuration should be
passed separately, to be initialized in the setup method.

A setup method must be implemented, to complete setup not done in the __init__
method (e.g. initialize classes as necessary). This separation is to allow for
arguments to be read for terminal use, without excessive use of memory or
computation. If no additional setup is necessary, it is sufficient to implement
the setup method simply with `pass`, or an immediate `return`.

A run method must also be implemented, dictating how to use the arguments.

Finally, to allow for the terminal script choosing ability provided for by the
ScriptChooser class, your script file should use ScriptChooser().complete_run().

A complete example is provided below:

    <main.py>
        from quickscript.scripts import Script, ScriptChooser
        from random import Random
        from typing import Type, Dict, Any

        class HelloScript(Script):
            def __init__(
                    self,
                    name:str = None,
                    rng_class:Type[Random] = Random,
                    rng_config:Dict[str, Any] = None,
                    **kwargs) -> None:
                """
                Script that says hello.

                Args:
                    name: person to which hello should be said.
                    rng_class: Class for generating random numbers.
                    rng_config: Configuration dictionary for rng_class.
                """
                super().__init__(**kwargs)
                self.name = name
                self.rng = rng_class
                self.rng_config = rng_config if rng_config else {}

            def setup(self):
                self.rng = self.rng(**self.rng_config)
            
            def run(self):
                greeting = "Hello" if self.rng.randint(0,1) else "Hi"
                print("{}, {}".format(greeting, self.name))

        if __name__ == "__main__":
            ScriptChooser().complete_run()

    <terminal>
        $ python main.py HelloScript -n World
        Hello, World

## Documentation
See [Here](https://mzimm003.github.io/quickscript)
