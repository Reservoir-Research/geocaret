# ========================================================================================
# LICENSE: GPL 3.0 (GNU General Public License v3 (GNU GPLv3)
#
# This code is based on "find_watershed" (watershed.py) developed by Sit et al
# at the University of Iowa
#
# The following changes were made:
#   - Inputs modified from x/y of pour pixel and direction_matrix to 1d index
#     of pour pixel and drainage direction grid
#   - Function truncated to remove watershed border finding functionality
#   - Draining direction array (e) recoded to match the specific coding and
#     orientation of drainiage directions data used in this application.
#   - Function modified to return 1d indices of watershed points
#   - Addition of comments.
#
# The original code can be found here:
#   https://github.com/uihilab/watershed-delineation/blob/master/Python/watershed.py
# Supporting publication can be found here:
#   https://opengeospatialdata.springeropen.com/articles/10.1186/s40965-019-0068-9
# =======================================================================================

import math

lenx = None


def find_watershed_cs(watershed_image_data_2d, pour_pixel):
    """ """
    global lenx

    dimensions_2d = [
        len(watershed_image_data_2d), len(watershed_image_data_2d[0])]
    h = dimensions_2d[0]
    w = dimensions_2d[1]
    #print("[DEBUG] [find_watershed_cs] Preparing Watershed Inputs h, w", h, w )

    x = pour_pixel[0] % w
    y = int(math.floor(pour_pixel[0]/w))

    direction_matrix = [
        elem for row in watershed_image_data_2d for elem in row]

    # Define empty watershed matrix
    matrix = [None] * (w*h)
    # Include the pour point in the watershed
    # Not sure if indices mapping from 2d to 1d array are correct.
    matrix[x+(w*y)] = 1
    watershed_indices = []
    watershed_indices.append((y * w + x))
    # Directions
    j = 1
    dirf = [-1, 0, 1, -1, 1, -1, 0, 1]
    dirg = [1, 1, 1, 0, 0, -1, -1, -1]
    # RECODED
    # e = [9, 8, 7, 6, 4, 3, 2, 1]
    e = [3, 2, 1, 6, 4, 9, 8, 7]
    # Let process be an array of zeros (None)
    process = [None] * (11000*4)
    # Process[store]CURRENT <- FirstPoint
    process[0] = x
    process[1] = y
    # c is the current location in storage (current level)
    c = 2
    o1 = 0
    o2 = 5500
    f = 0
    # While there are unvisited nodes in storage
    while c > o1:
        numbr3 = o1
        o1 = o2
        o2 = numbr3 + o1 - o2
        lenx = c
        # c is the start index of the storage part
        c = o1
        k = o2
        # r2 defines the neighbours of the current node
        r2 = range(7, -1, -1)
        # For each unvisited node stored in previous step
        for i in range(k, lenx, 2):
            arx = process[i]
            ary = process[i+1]
            # For each neighbour of the current node in the image data.
            for j in r2:
                nx = arx + dirf[j]
                ny = ary + dirg[j]
                ind = ny*w+nx
                # If neighbour's flow direction is in to the node.
                # Add neighbour node to storage part of process.
                if direction_matrix[ind] == e[j]:
                    process[c] = nx
                    c += 1
                    process[c] = ny
                    c += 1
                    matrix[ind] = 1
                    watershed_indices.append(ind)
        f = f+1

    return watershed_indices
