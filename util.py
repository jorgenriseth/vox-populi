import os

def listdir_fullpath(dir):
    """
    Creates a list with full paths to all files in the given directory.
    """
    return [os.path.join(dir, f) for f in os.listdir(dir)]