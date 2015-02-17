import os
from .error import UnitNotFoundError

__author__ = 'Dan Bullok and Ben Lambeth'

# TODO: Loaders retrieve source code for the interpreter.  For this to be
# truly useful, we need to define a way to load code into the translation
# unit being processed (like an include or import statement).

# TODO: write tests


class Loader(object):
    '''
    Base class for a source code loader.
    '''

    def load_unit(self, unit_name, pos=None):
        '''
        :param unit_name: the name of the unit to load
        :type unit_name: str
        :param pos: the position in the source code where the load request
        was made.  Use None if the load request was not made from source code.
        :type pos: TokenPos or None
        :return: the text of the requested source unit
        :rtype: str
        :raises UnitNotFoundError: if the requested source unit cannot be
        found.
        '''
        pass


class DictLoader(Loader):
    '''
    A source code loader that retrieves units from a dict
    '''

    def __init__(self, units):
        '''
        :param units: the dict containing unit_name -> unit_text items
        :type units: dict
        '''
        self._units = units

    def load_unit(self, unit_name, pos=None):
        '''
        :param unit_name: the name of the unit to load
        :type unit_name: str or StaticDatum of type str
        '''
        # TODO: ensure that unit_name.value is actually a string.
        n = unit_name if isinstance(unit_name,str) else unit_name.value
        try:
            s = self._units.get(n)
            return s
        except KeyError as e:
            p = pos if not hasattr(unit_name, 'value') else unit_name.pos
            raise UnitNotFoundError(p, n)


class FileSysLoader(Loader):
    '''
    A Source code loader that retrieves units from a file system.

    Takes a list of directories to search.  When a unit is requested,
    the directories are searched in order.
    '''

    def __init__(self, module_dirs):
        '''
        :param module_dirs: the directories to search for units
        :type module_dirs: list[str]
        '''
        self._module_dirs = module_dirs

    def load_unit(self, unit_name, pos=None):
        for d in self._module_dirs:
            content = self._load(unit_name, d)
            if content is not None:
                return content
        raise UnitNotFoundError(pos, unit_name)

    def _load(self, unit_name, root_dir):
        '''
        Attempt to load a unit from a file.  The file name is the unit_name
        appended to the root_dir.
        :param unit_name: the unit name to attempt to load
        :type unit_name: str
        :param root_dir: the path of the directory to look in
        :type root_dir: str
        :return: the content of the file if found, or None if the file does
        not exist.
        :rtype: str or None
        '''
        # TODO: Handle file read errors such as permission errors, etc.
        p = os.path.join(root_dir, unit_name)
        if os.path.exists(p) and os.path.isfile(p):
            return open(p, 'r').read()
        return None
