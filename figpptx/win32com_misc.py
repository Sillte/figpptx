"""Here, I'd like to gather utility function / classes related to `pywin32com`. 
Notice that this library is not library, but recipes for reading codes of `pywin32com`.  
""" 

from win32com.client import DispatchEx 
from win32com.client.selecttlb import EnumTlbs
from win32com.client.makepy import GenerateFromTypeLibSpec
from win32com import __gen_path__

print(__gen_path__)  # In this folder, the generated object resides. 

def assure_generation():
    """We would like to `generated` pywin32 PowerPoint module.
    """
    def _gen():
        targets = []
        for s in EnumTlbs():
            if s.desc.startswith("Microsoft PowerPoint"):
                targets.append(s)
        target = targets[0]
        GenerateFromTypeLibSpec(target, verboseLevel=1)
    def _required_generation():
        app = DispatchEx("PowerPoint.Application")
        if app.Presentations.__class__.__name__ == "Presentations":
            return False
        if isinstance(app.Presentations, CDispatch):
            del app
            return True
        raise NotImplementedError("Error.")

    if _required_generation():
        _gen()

assure_generation()

