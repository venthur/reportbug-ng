
import os

def get_control(package):
    """Get /usr/share/bug/package/control info if available and return the data
    as a dictionary."""
    path = "/usr/share/bug/" + str(package) + "/control"
    control = dict()
    if not os.path.exists(path):
        return control
    f = file(path)
    for line in f.readlines():
        tokens = line.split(":")
        if len(tokens) < 2:
            continue
        cmd = str(tokens[0].strip().lower())
        args = [str(i).strip() for i in tokens[1].split()]
        control[cmd] = args
    f.close()
    return control

def submit_as(package):
    """Returns the submit-as value of the packge if available otherwise 
    package."""
    alias = get_control(package).get("submit-as")
    return alias[0] if alias else package
 