"""
Created on 4/6/23
@author: josephloeffler
"""

import turtle as t

def histogram(file, n):

    f = open(file, 'r')

    lines = []
    count = 0
    # h = []

    for line in f:
        if count == 0:
            # h = line.strip().split("\t")
            count += 1
        else:
            lines.append((line.strip()).split("\t"))

    f.close()
    # print(lines)
    sorted_lines = (sorted(lines, key=lambda x: float(x[7])))
    # sorted_lines.insert(0, h)

    length = len(sorted_lines)
    tot_lines = 0
    tot = 0
    ret = []
    first = 0
    last = 0
    while True:
        counter = 0
        if tot_lines == length:
            break
        tot = 0
        while counter < n:
            if counter == 0:
                first = sorted_lines[tot_lines][7]
            elif counter == n-1:
                last = sorted_lines[tot_lines][7]
            if tot_lines == length:
                last = sorted_lines[tot_lines-1][7]
                break

            wl = sorted_lines[tot_lines][6]
            if wl == "WIN":
                tot += 1
            elif wl == "TIE":
                tot += 0.5

            counter += 1
            tot_lines += 1
        avg = tot/counter
        ret.append((first + "–" + last, avg, counter))

    return ret


if __name__ == '__main__':

    histy = histogram("PreviousLines.txt", 200)

    max_len_0 = 0
    max_len_1 = 0
    for line in histy:
        currLength_0 = len(line[0])
        currLength_1 = len(str(line[1]))

        if currLength_0 > max_len_0:
            max_len_0 = currLength_0
        if currLength_1 > max_len_1:
            max_len_1 = currLength_1

    for line in histy:
        len_0 = len(line[0])
        len_1 = len(str(line[1]))
        spaces0 = max_len_0 - len_0
        spaces1 = max_len_1 - len_1
        print(line[0] + " " * spaces0 + "\t" + str(line[1]) + " "*spaces1 +
              "\t" + str(line[2]))

    # win = t.Screen()
    #
    # t.pu()
    # t.goto(-300, -300)
    # t.pd()

    # for line in histy:
    #     t.goto(t.xcor()+5, line[1]*200-300)

    # win.exitonclick()
    pass
