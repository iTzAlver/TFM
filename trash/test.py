def GPA(g_size, sigma, mtx_size):
    """This function creates the Gaussian Proximity Adapter based on 3 parameters:

            sigma = Sigma parameter of the Normal Distribution (zero mean)
            mtx_size = Size of the GPA
            g_size = Number of elements taken

    """

    x = np.linspace(0, g_size-1, g_size)
    g = np.exp(-1*(x**2)/(2*(sigma**2)))
    GPA = np.zeros((mtx_size, mtx_size))
    for index1 in range(mtx_size):
        for index2 in range(g_size):
            append_index = (index1 + index2) % mtx_size
            if (index1 + index2) < mtx_size:
                GPA[index1][append_index] = g[index2]
        for index3 in range(g_size):
            append_index = (index1 - index3) % mtx_size
            if (index1 - index3) >= 0:
                GPA[index1][append_index] = g[index3]
    return GPA






