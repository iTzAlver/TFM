# -------------------------------------------------------------------#
#                                                                    #
#    Author:    Alberto Palomo Alonso.                               #
#                                                                    #
#    Git user:  https://github.com/iTzAlver                          #
#    Email:     ialver.p@gmail.com                                   #
#                                                                    #
# -------------------------------------------------------------------#
import time
import package.newsegmentation as ns


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
def main() -> None:
    params = {'lcm': (0.42,),
              'tdm': 0.3,
              'sdm': (0.184, 1, 0.87 * 0.184)}
    x = list()
    cachefile = ''
    print('Start conversion.')
    init = time.perf_counter()
    x.append(ns.Segmentation('./db/vtt_files/Julen/1.vtt', **params, cache_file=cachefile))
    x.append(ns.Segmentation('./db/vtt_files/Julen/2.vtt', **params, cache_file=cachefile))
    x.append(ns.Segmentation('./db/vtt_files/Julen/3.vtt', **params, cache_file=cachefile))
    x.append(ns.Segmentation('./db/vtt_files/Julen/4.vtt', **params, cache_file=cachefile))
    x.append(ns.Segmentation('./db/vtt_files/Julen/5.vtt', **params, cache_file=cachefile))
    x.append(ns.Segmentation('./db/vtt_files/Julen/6.vtt', **params, cache_file=cachefile))
    x.append(ns.Segmentation('./db/vtt_files/Julen/7.vtt', **params, cache_file=cachefile))
    x.append(ns.Segmentation('./db/vtt_files/Julen/8.vtt', **params, cache_file=cachefile))
    x.append(ns.Segmentation('./db/vtt_files/Julen/9.vtt', **params, cache_file=cachefile))
    x.append(ns.Segmentation('./db/vtt_files/Julen/10.vtt', **params, cache_file=cachefile))
    print(f'Finished in ellapsed time: {time.perf_counter() - init}')
    for i in range(10):
        print(i)
        res = x[i].evaluate(f'./db/groundtruth/f1/Julen/{i + 1}.txt')
        if i == 6:
            x[i].plotmtx()
        print(res)


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
if __name__ == '__main__':
    main()
# -------------------------------------------------------------------#
#           E   N   D          O   F           F   I   L   E         #
# -------------------------------------------------------------------#
