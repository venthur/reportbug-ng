
# submit-as
# package-status [plist], show installstatus of thos packages
# report-with [plist], show deps, recommends, etc for those packages
# the script
# send-to domain, not used anymore?


import os


def get_control(package):
    """
    Get /usr/share/bug/package/control info if available and return the
    data as a dictionary.
    """
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
    """
    Returns the submit-as value of the packge if available otherwise
    package.
    """
    alias = get_control(package).get("submit-as")
    return alias[0] if alias else package


def report_with(package):
    """
    Return a list of packages to report this package with, of none are
    given return at least a single elemented list containing package.
    """
    rw = [package]
    plist = get_control(package).get("report-with")
    if plist:
        rw.extend(plist)
    return rw


def package_status(package):
    """
    Returns list of packages which should also appear in statuslist or
    empty list if none given.
    """
    plist = get_control(package).get("package-status")
    return plist if plist else []

