# quickscript
Quickly configure a script runnable by terminal or as a class within python.

## Overview
A script should be represented as a class subclassing Script.

The __init__ method will take all args important to the script’s flexibility. The args must be type hinted, and described in the __init__ method’s docstring indented under an “Args:” section.

A run method must also be implemented, dictating how to use the arguments.

Finally, to allow for the terminal script choosing ability provided for by the ScriptChooser class, your script file should use ScriptChooser().complete_run().

A complete example is provided below:

    <main.py>
        from quickscript.scripts import Script, ScriptChooser

        class HelloScript(Script):
            def __init__(
                    self,
                    name:str = None,
                    **kwargs) -> None:
                """
                Script that says hello.

                Args:
                    name: person to which hello should be said.
                """
                super().__init__(**kwargs)
                self.name = name

            def run(self):
                print("Hello, {}".format(self.name))

        if __name__ == "__main__":
        ScriptChooser().complete_run()

    <terminal>
        $ python main.py HelloScript -n World
        Hello, World

## Documentation
See [Here](https://mzimm003.github.io/quickscript)
