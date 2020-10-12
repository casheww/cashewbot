e_a_dict = {' ': '   ',
            'a': 'ר',
            'b': 'コ',
            'c': '┘',
            'd': 'п',
            'e': 'ߛ',
            'f': 'ப',
            'g': '厂',
            'h': 'ⵎ',
            'i': 'ட',
            'j': 'ᒣ',
            'k': 'ᓗ',
            'l': 'ᒧ',
            'm': 'ᒉ',
            'n': 'ᑭ',
            'o': 'ᘂ',
            'p': 'ᒥ',
            'q': 'ᓕ',
            'r': 'ᒪ',
            's': 'ᒭ',
            't': 'ᓘ',
            'u': 'ᒨ',
            'v': 'ᒕ',
            'w': 'ᑮ',
            'x': 'ᒎ',
            'y': 'ᓟ',
            'z': 'ᓛ'}


def eta(content):
    """ english to anglen translator """
    content = content.lower()
    anglen = ''
    for char in content:
        try:
            anglen += e_a_dict[char]
        except KeyError:
            anglen += char
    return anglen


def ate(content):
    """ anglen to english translator """
    content = content.lower()
    a_e_dict = {v: k for k, v in e_a_dict.items()}
    english = ''
    for char in content:
        try:
            english += a_e_dict[char]
        except KeyError:
            english += char
    return english
