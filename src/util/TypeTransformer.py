def bool2int(row):
    '''
    transform every bool in row(list) to int
    :param row: list of num/bool
    :return: None
    '''
    if not isinstance(row, list):
        return
    for index, elem in enumerate(row):
        row[index] = {True: 1, False: 0}[elem]
