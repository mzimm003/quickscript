

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