import math
import sys

def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if type(item) == list:
            flat_list.append(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list

def is_symmetric(matrix):
    if len(matrix) != len(matrix[0]):
        return False
    for y in range(len(matrix)):
        for x in range(len(matrix)):
            if x < y:
                if matrix[y][x] != matrix[x][y]:
                    return False
    return True

def cluster(matrix, average):
    """
    Args: 
       matrix
       average: a boolean, cluster using average if true, sum if false.
    """
    if is_symmetric(matrix):
        order = flatten_list(get_clusters(get_delta_matrix(matrix, True), average))
        return reorder_matrix(matrix, order, order)
    else:
        return reorder_matrix(
            matrix,
            flatten_list(get_clusters(get_delta_matrix(matrix, True), average)),
            flatten_list(get_clusters(get_delta_matrix(matrix, False), average))
        )

def reorder_matrix(matrix, order_x, order_y):
    """
    Reorders and returns the argued array based on the order of
    indexes in the comma-delimited string (e.g., "2,1" would flip
    a 2x2 array across a 45-degree axis)
    """
    x_len = len(matrix[0])
    y_len = len(matrix)
    new_matrix = [[0 for i in range(x_len)] for j in range(y_len)]
    # reorder rows
    for y in range(y_len):
        for x in range(x_len):
            new_matrix[y][x] = matrix[order_y[y]][order_x[x]]
    return new_matrix

def remove_row_col(matrix, i):
    assert is_symmetric(matrix)
    new_matrix = [[0 for i in range(len(matrix) - 1)] for j in range(len(matrix) - 1)]
    for y1 in range(len(matrix)):
        if y1 == i:
            continue
        for x1 in range(len(matrix)):
            if x1 == i:
                continue
            y2 = y1
            if y2 > i:
                y2 -= 1
            x2 = x1
            if x2 > i:
                x2 -= 1
            new_matrix[y2][x2] = matrix[y1][x1]
    return new_matrix

# this was distance_arr in the InsightMatrix. 
def get_delta_matrix(matrix, by_x_axis):
    """
    Returns a symmetric matrix with 0's across diagonal.

    If you pass this a 3x5 matrix, and you're working by the x axis, you'll get
    a 5x5 matrix back. By the y axis you'll get a 3x3 matrix back.
    """
    if by_x_axis:
        s = len(matrix[0])
        t = len(matrix)
    else:
        s = len(matrix)
        t = len(matrix[0])
    delta_matrix = [[0 for i in range(s)] for j in range(s)]
    for j in range(s):
        for i in range(s):
            acc = 0
            for k in range(t):
                if by_x_axis:
                    acc += abs(matrix[k][i] - matrix[k][j])
                else:
                    acc += matrix(arr[i][k] - matrix[j][k])
            delta_matrix[j][i] = acc
    return delta_matrix

def get_clusters(delta_matrix, average):
    """
    Returns the index order for the matrix that generated the delta matrix.

    Args:
        delta_matrix
        average: bool...use average or sum

    Returns:
        [[0], [1], [2], [3], [4], [5], [6]]
        [[0, 1], [2, 3], [4, 5, 6]]
        [[0, 1, 2, 3, 4, 5, 6]]
    """
    assert len(delta_matrix) == len(delta_matrix[0])

    # the initial order is a flattened list, like [0, 1, 2...n]
    clusters = [[i] for i in range(len(delta_matrix))]
    
    # while new array isn't one big cluster
    while len(clusters) > 1:
        # this will be a 2-tuple, the index positions of the lowest values in
        # the delta matrix.
        min_value = None
        min_index = (0, 0)
        for j in range(len(delta_matrix)):
            for i in range(len(delta_matrix)):
                if i >= j:
                    continue
                if min_value == None or delta_matrix[j][i] < min_value:
                    min_value = delta_matrix[j][i]
                    min_index = (j, i)

        # in the original code they enlarge the delta matrix by 1 in each
        # direction to create a "totals" column.        
        new_size = len(delta_matrix) + 1
        # add a new row.
        delta_matrix.append([])
        for i in range(new_size - 1):
            if average: 
                # AVERAGE the corresponding row/column
                summary = delta_matrix[min_index[0]][i] + delta_matrix[min_index[1]][i] / 2.0
            else:
                # SUM the corresponding row/column
                summary = delta_matrix[min_index[0]][i] + delta_matrix[min_index[1]][i]
            # append the summary to the end of each row.
            delta_matrix[i].append(summary)
            # append the summary to the end of each column. 
            delta_matrix[-1].append(summary)
        # add a zero value to the bottom right corner of array.
        delta_matrix[-1].append(0)
    
        # append sortArray with new values to match new_arr
        clusters, delta_matrix = build_cluster_and_modify_delta_matrix(
            clusters,
            delta_matrix,
            min_index[0],
            min_index[1]
        )
    return clusters
    

def build_cluster_and_modify_delta_matrix(clusters, delta_matrix, i1, i2):
    """
    Adds a new index/row to the end of the array, then populates it with
    comma-delimited values from the two argued rows.
    ASSUMES: the sortArray is the only array being passed.

    Args:
        clusters: a nested list of indices. 
        delta_matrix
        i1: index of row 1.
        i2: index of row 2.
    """
    assert i1 != i2
    # if the two values to concatenate are single values...
    print(i1)
    print(i2)
    print(clusters)
    if len(clusters[i1]) == 1 and len(clusters[i2]) == 1:
        # ...just cluster them
        clusters.append([clusters[i1][0], clusters[i2][0]])
    else:
        # get the index values to compare
        indices = [[None, None], [None, None]]
        # populate the upper left intersection of index array
        indices[0][0] = clusters[i1][0]
        # populate the upper right intersection of index array (if necessary)
        if len(clusters[i1]):
            indices[0][1] = clusters[i1][-1]
        # populate the lower left intersection of index array
        indices[1][0] = clusters[i2][0]
        # populate the lower right intersection of index array (if necessary)
        if len(clusters[i2]):
            indices[1][1] = clusters[i2][-1]
        # lookup the intersections of the index values in the distance matrix
        values = [[None, None], [None, None]]
        values[0][0] = delta_matrix[indices[0][0]][indices[1][0]]
        if indices[0][1] != None:
            values[0][1] = delta_matrix[indices[0][1]][indices[1][0]]
        if indices[1][1] != None:
            values[1][0] = delta_matrix[indices[0][0]][indices[1][1]]
        if indices[0][1] != None and indices[1][1] != None:
            values[1][1] = delta_matrix[indices[0][1]][indices[1][1]]

        # find the index of the lowest value in the value array
        lowest = values[0][0]
        low_row = 0
        low_col = 0
        for j in range(2):
            for i in range(2):
                if values[j][i] < lowest:
                    lowest = values[j][i]
                    low_row = i
                    low_col = j

        # create the new concatenation based on which
        # index of intValue was the lowest
            if low_row == 0 and low_col == 0:
                clusters.append([clusters[i1][-1], clusters[i2][-1]])
            elif low_row == 0 and low_col == 1:
                clusters.append([clusters[i1][0], clusters[i2][0]])
            elif low_row == 1 and low_col == 0:
                clusters.append([clusters[i1][-1], clusters[i2][-1]])
            else:
                clusters.append([clusters[i1][0], clusters[i2][-1]])

    if i1 < i2:
        delta_matrix = remove_row_col(delta_matrix, i1)
        delta_matrix = remove_row_col(delta_matrix, i2)
        clusters.pop(i1)
        clusters.pop(i2)
    else:
        delta_matrix = remove_row_col(delta_matrix, i2)
        delta_matrix = remove_row_col(delta_matrix, i1)
        clusters.pop(i2)
        clusters.pop(i1)
    return clusters, delta_matrix

if __name__ == '__main__':
    # use fruits and vegetables sample data. 
    matrix = [[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0], [0.0, 1.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.75, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.75, 0.0, 0.0, 0.0, 0.0, 0.25, 0.75, 0.0, 0.0, 0.25, 0.25], [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.25, 0.25, 0.5, 0.0, 0.0, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.25, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0], [0.0, 0.25, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.5, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.5], [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.75, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.25, 0.0, 0.0, 0.25, 1.0, 0.25, 0.25, 0.0, 0.0, 0.25, 0.25, 0.0, 0.0, 0.25, 0.0, 0.0, 0.75, 0.0, 0.25, 0.25, 0.0, 0.5, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0], [0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 1.0, 0.25, 0.25, 0.0, 0.25, 0.75, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.5, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0], [0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.25, 0.25, 1.0, 0.25, 0.0, 0.5, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.25, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.25, 1.0, 0.0, 0.5, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.75, 0.25, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0], [0.0, 0.75, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.25, 0.75, 0.0, 0.25, 0.25, 0.25], [0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.25, 0.5, 0.5, 0.0, 1.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.25, 0.0, 0.25, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0], [0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.75, 0.25, 0.25, 0.0, 0.25, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.5, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.0], [0.0, 0.25, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.75, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.5, 0.0, 0.25, 0.25, 0.5], [0.0, 0.0, 0.0, 0.0, 0.0, 0.75, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0], [0.0, 0.25, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.75, 0.0, 0.0, 1.0, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.5, 0.0, 0.25, 0.25, 0.75], [0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.75, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0], [0.0, 0.75, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 1.0, 0.0, 0.0, 0.25, 0.0, 0.25, 0.75, 0.0, 0.25, 0.25, 0.25], [0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.25, 0.25, 0.75, 0.0, 0.5, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5, 0.0, 0.25, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0], [0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.5, 0.25, 0.25, 0.0, 0.25, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0], [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.0, 0.0, 1.0, 0.0, 0.0, 0.25, 0.0, 0.25, 0.25, 0.25], [0.0, 0.0, 0.25, 0.0, 0.25, 0.25, 0.5, 0.25, 0.25, 0.25, 0.0, 0.25, 0.25, 0.0, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.25, 0.0, 1.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0], [0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.25, 0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 1.0, 0.25, 0.0, 0.5, 0.25, 0.0], [0.0, 0.75, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.75, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.5, 0.0, 0.75, 0.0, 0.0, 0.25, 0.0, 0.25, 1.0, 0.0, 0.25, 0.25, 0.5], [0.0, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.25, 0.25, 0.25, 0.0, 0.5, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.5, 0.25, 0.0, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0], [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.25, 0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.5, 0.25, 0.0, 1.0, 0.25, 0.25], [0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.25, 0.25, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.25, 0.0, 0.25, 1.0, 0.25], [0.0, 0.25, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.75, 0.0, 0.25, 0.0, 0.0, 0.25, 0.0, 0.0, 0.5, 0.0, 0.25, 0.25, 1.0]]


    # cluster matrix.
    matrix = cluster(matrix, True)

    # output as ASCII art.
    ascii = ' .,;!vlLFE#'
    for row in matrix:
        for cell in row:
            sys.stdout.write(ascii[math.floor(cell * 10)])
            sys.stdout.write(' ')
        sys.stdout.write('\n')
