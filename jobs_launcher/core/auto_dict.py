#!usr/bin/env python3

class AutoDict(dict):
    '''
        perl-like dict

    >>> x = AutoDict()
    >>> x[1][2][3]=4
    >>> x
    {1: {2: {3: 4}}}

    >>> x = AutoDict()
    >>> x[1,2,3][4] = 5
    >>> x
    {(1, 2, 3): {4: 5}}

    >>> x = AutoDict()
    >>> x["1","2","3"]["4"] = 5
    >>> x
    {('1', '2', '3'): {'4': 5}}

    '''
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    import doctest
    doctest.testmod()