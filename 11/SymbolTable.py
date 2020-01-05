STATIC = "static"
FIELD = "field"
ARG = "argument"
VAR = "var"

S_TYPE = 0
S_KIND = 1
S_INDEX = 2


class SymbolTable:
    """
    a service for creating, populating and using symbol table.
    """

    def __init__(self):
        # new empty symbol tables
        self._class_symbols = {}
        self._subroutine_symbols = {}
        # self._cur_scope = 0
        self._index_static, self._index_field = 0, 0
        self._index_arg, self._index_var = 0, 0

    def startSubroutine(self):
        """
        Starts a new subroutine scope
        (i.e. erases all names in the previous subroutine’s scope.)
        :return: none
        """
        # erase all names in prev subroutine symbol table
        self._subroutine_symbols.clear()
        self._index_arg, self._index_var = 0, 0
        return

    def define(self, name, type, kind):
        """
        defines a new identifier of given name, type, and kind
        and assigns it a running index.
        STATIC & FIELD have a class scope, ARG & VAR have a subroutine scope.
        :param name: string
        :param type: string
        :param kind: STATIC | FIELD | ARG | VAR
        :return: none
        """
        if kind == STATIC:
            self._class_symbols[name] = [type, kind, self._index_static]
            self._index_static += 1
        elif kind == FIELD:
            self._class_symbols[name] = [type, kind, self._index_field]
            self._index_field += 1
        elif kind == ARG:
            self._subroutine_symbols[name] = [type, kind, self._index_arg]
            self._index_arg += 1
        else: # kind == VAR
            self._subroutine_symbols[name] = [type, kind, self._index_var]
            self._index_var += 1
        return

    def varCount(self, kind):
        """
        :param kind: STATIC | FIELD | ARG | VAR
        :return: the number of variables of given kind in the current scope.
        """
        if kind == STATIC:
            return self._index_static
        elif kind == FIELD:
            return self._index_field
        elif kind == ARG:
            return self._index_arg
        else: # kind == VAR
            return self._index_var

    def kindOf(self, name):
        """
        :param name: string
        :return: Returns the kind of the named identifier in the current scope.
        Returns NONE if the identifier is unknown in the current scope.
        """
        if name in self._subroutine_symbols:
            return str(self._subroutine_symbols[name][S_KIND])
        elif name in self._class_symbols:
            return str(self._class_symbols[name][S_KIND])
        return None

    def typeOf(self, name):
        """
        :param name: string
        :return: Returns the type of the named identifier in the current scope.
        """
        if name in self._subroutine_symbols:
            return str(self._subroutine_symbols[name][S_TYPE])
        elif name in self._class_symbols:
            return str(self._class_symbols[name][S_TYPE])
        # return None

    def indexOf(self, name):
        """
        :param name: string
        :return: Returns the index assigned to named identifier.
        """
        if name in self._subroutine_symbols:
            return str(self._subroutine_symbols[name][S_INDEX])
        elif name in self._class_symbols:
            return str(self._class_symbols[name][S_INDEX])
        # return None

