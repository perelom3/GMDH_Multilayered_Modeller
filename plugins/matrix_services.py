
import app, sol
from math import sqrt

def mean_value(matrix):
    R = sol.new_matrix(1, matrix.col_count)
    for i in xrange(matrix.col_count):
        s = 0.0
        N = 0
        for j in xrange(matrix.row_count):
            v = matrix(j, i)
            if abs(v) < 0.9e+300:
                s += v
                N += 1
        R(0, i, s/N)
    return R

def variance(matrix, mv = None):
    if not mv:
        mv = mean_value(matrix)
    R = sol.new_matrix(1, matrix.col_count)
    for i in xrange(matrix.col_count):
        s = 0.0
        N = 0
        for j in xrange(matrix.row_count):
            v = matrix(j, i)
            if abs(v) < 0.9e+300:
                d = (v - mv(0, i))
                s += d**2
                N += 1
        if N > 1:
            R(0, i, s/(N-1))
        else:
            R(0, i, 1.0e+300)
    return R

def std_deviation(matrix, mv = None):
    v = variance(matrix, mv)
    R = sol.new_matrix(1, matrix.col_count)
    for i in xrange(matrix.col_count):
        R(0, i, sqrt(v(0, i)))
    return R

def avg_deviation(matrix, mv = None):
    if not mv:
        mv = mean_value(matrix)
    R = sol.new_matrix(1, matrix.col_count)
    for i in xrange(matrix.col_count):
        s = 0.0
        N = 0
        for j in xrange(matrix.row_count):
            v = matrix(j, i)
            if abs(v) < 0.9e+300:
                d = abs(v - mv(0, i))
                s += d
                N += 1
        if N != 0:
            R(0, i, s/N)
        else:
            R(0, i, 1.0e+300)
    return R

def pair_correlation(vec1, vec2):
    try:
        ma = mean_value(vec1)(0, 0)
        mb = mean_value(vec2)(0, 0)
        S1 = 0.0
        S21 = 0.0
        S22 = 0.0
        for i in xrange(vec1.row_count):
          if abs(vec1(i, 0)) < 0.9e+300 and abs(vec2(i, 0)) < 0.9e+300:
            D1 = vec1(i, 0) - ma
            D2 = vec2(i, 0) - mb
            S1 += D1*D2
            S21 += D1*D1
            S22 += D2*D2
        return S1/sqrt(S21*S22)
    except ArithmeticError:
        return 1.0e+300


def wanted_matrix():
    matrix = app.get_selected_matrix()
    if matrix.row_count == 1 and matrix.col_count == 1:
        names = []
        M = app.get_active_matrix()
        for i in xrange(M.col_count):
            names += [app.get_actmatrix_col_name(i)]
        M.col_names = names
        return M
    else:
        names = []
        for i in xrange(matrix.col_count):
            names += [app.get_selmatrix_col_name(i)]
        matrix.col_names = names
        return matrix



def matrix_mean_value():
    print "\n\nCalculate mean value. Wait..."
    matrix = wanted_matrix()
    R = mean_value(matrix)
    for i in xrange(R.col_count):
        print "Mean value of [%s]:\t\t" % matrix.col_names[i], R(0, i)

def matrix_variance():
    print "\n\nCalculate variance. Wait..."
    matrix = wanted_matrix()
    R = variance(matrix)
    for i in xrange(R.col_count):
        print "Variance of [%s]:\t\t" % matrix.col_names[i], R(0, i)

def matrix_std_deviation():
    print "\n\nCalculate standart deviation. Wait..."
    matrix = wanted_matrix()
    R = std_deviation(matrix)
    for i in xrange(R.col_count):
        print "Standart deviation of [%s]:\t\t" % matrix.col_names[i], R(0, i)

def matrix_avg_deviation():
    print "\n\nCalculate average deviation. Wait..."
    matrix = wanted_matrix()
    R = avg_deviation(matrix)
    for i in xrange(R.col_count):
        print "Average deviation of [%s]:\t\t" % matrix.col_names[i], R(0, i)

def pair_correlation_test(Show_max_count="1", Show_min_count="1"):
    """
    This test can halp you find most correlated variales.
    "Show_max_count" - number of most correlated elements to show
    "Show_min_count" - number of elements with minimal correlation to show
    """
    Show_max_count = int(Show_max_count)
    Show_min_count = int(Show_min_count)
    M = wanted_matrix()
    if M.col_count < 2:
        raise Exception("Two columns or greater needed for this test.")
    print "\n\nStart pair correlation test..."
    itr = sol.new_cmi_colref2(M, 2)
    wb = itr.buffer
    Max = None
    Min = None
    count = 0
    while itr.iterable:
        idx = itr.indexes
        V = pair_correlation(wb[0], wb[1])
        if abs(V) > 0.9e+300:
            continue
        if Show_max_count > 0:
            if not Max:
                Max = [(V, idx)]
            elif abs(V) > abs(Max[-1][0]):
                for i in xrange(len(Max)):
                    if abs(V) > Max[i][0]:
                        Max.insert(i, (V, idx))
                        break
                if len(Max) > Show_max_count:
                    Max = Max[:Show_max_count]
        if Show_min_count > 0:
            if not Min:
                Min = [(V, idx)]
            elif abs(V) < abs(Min[-1][0]):
                for i in xrange(len(Min)):
                    if abs(V) < Min[i][0]:
                        Min.insert(i, (V, idx))
                        break
                if len(Min) > Show_min_count:
                    Min = Min[:Show_min_count]

    print "\n------------ Summary ------------"
    if Show_max_count > 0:
        print "Maximum correlation: "
        for v, i in Max:
            print "    ", M.col_names[i[0]]
            print "    ", M.col_names[i[1]]
            print "    Value: ", v
            print "    Column numbers - ", map(lambda x: x+1, i)
    if Show_min_count > 0:
        print "Minimum correlation: "
        for v, i in Min:
            print "    ", M.col_names[i[0]]
            print "    ", M.col_names[i[1]]
            print "    Value: ", v
            print "    Column numbers - ", map(lambda x: x+1, i)



app.register_matrix_action("Mean value", matrix_mean_value)
app.register_matrix_action("Variance", matrix_variance)
app.register_matrix_action("Standart deviation", matrix_std_deviation)
app.register_matrix_action("Average deviation", matrix_avg_deviation)
app.register_matrix_action("Pair correlation test", pair_correlation_test)
