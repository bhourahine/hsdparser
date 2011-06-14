def find_first_occurence(current, signs, check_signs):
    pos = []
    sign = None
    minpos = len(current)
    for aa in range(len(signs)):
        if check_signs[aa]:
            pos.append(current.find(signs[aa]))
    for aa in range(len(pos)):
        if pos[aa] != -1 and pos[aa] < minpos:
            minpos = pos[aa]
    if minpos == len(current):
        return None, current
    else:
        sign = current[minpos]
        current = current.split(sign,1)
        return sign, current
