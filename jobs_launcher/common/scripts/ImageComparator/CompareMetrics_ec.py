import numpy as np

import scipy
if scipy.__version__ > '1.1.0':
    from imageio import imread
else:
    from scipy.misc import imread

from scipy import sum

from scipy.spatial.distance import hamming
from scipy.spatial.distance import cityblock
from scipy.spatial.distance import correlation
from scipy.spatial.distance import euclidean
from scipy.spatial.distance import chebyshev
from scipy.spatial.distance import sqeuclidean
from scipy.spatial.distance import braycurtis
from scipy.spatial.distance import canberra
from scipy.spatial.distance import cosine


class CompareMetrics(object):

    def __init__ (self, file1, file2):
        self.file1 = file1
        self.file2 = file2

        self.img1 = 0
        self.img2 = 0

        if self.readImages():

            self.diff_pixeles = 0

            self.nrmds_norm = 0
            self.hamming_norm = 0
            self.manhattan_norm = 0
            self.correlation_norm = 0
            self.euclidean_norm = 0
            self.sqeuclidean_norm = 0
            self.chebyshev_norm = 0
            self.braycurtis_norm = 0
            self.cosine_norm = 0
            self.canberra_norm = 0


    def normalize(self, arr):
        rng = arr.max()-arr.min()
        amin = arr.min()
        return (arr-amin)*255/rng


    def getDiffPixeles(self, tolerance=3):

        if self.diff_pixeles:
            return self.diff_pixeles
        else:
            # self.img1 = self.normalize(self.img1)
            # self.img2 = self.normalize(self.img2)

            img1R = self.img1[:, :, 0]
            img1G = self.img1[:, :, 1]
            img1B = self.img1[:, :, 2]
            # img1A = self.img1[:, :, 3]

            img2R = self.img2[:, :, 0]
            img2G = self.img2[:, :, 1]
            img2B = self.img2[:, :, 2]
            # img2A = self.img2[:, :, 3]

            if img1R.shape != img2R.shape:
                self.diff_pixeles = "Imgs resolution error"
                return self.diff_pixeles

            diffR = abs(img1R - img2R)
            diffG = abs(img1G - img2G)
            diffB = abs(img1B - img2B)
            # diffA = abs(img1A - img2A)

            self.diff_pixeles = len(list(filter(
                lambda x: x[0] <= tolerance and x[1] <= tolerance and x[2] <= tolerance, zip(diffR.ravel(), diffG.ravel(), diffB.ravel())
            )))

            # get percent
            self.diff_pixeles = len(diffR.ravel()) - self.diff_pixeles
            self.diff_pixeles = float (self.diff_pixeles / len(diffR.ravel())) * 100

            return round(self.diff_pixeles, 2)


    def readImages(self):
        self.img1 = imread(self.file1).astype(float)
        self.img1ravel = self.img1.ravel()
        self.img2 = imread(self.file2).astype(float)
        self.img2ravel = self.img2.ravel()

        return True


    def getNrmsd(self):
        if self.nrmds_norm:
            return self.nrmds_norm
        else:
            self.nrmds_norm = np.sqrt(np.mean((self.img1 - self.img2) ** 2)) / 255
            return self.nrmds_norm

    def getHamming(self):
        if self.hamming_norm:
            return self.hamming_norm
        else:
            self.hamming_norm = hamming(self.img1ravel, self.img2ravel)
            return self.hamming_norm

    def getManhattan(self):
        if self.manhattan_norm:
            return self.manhattan_norm
        else:
            self.manhattan_norm = cityblock(self.img1ravel, self.img2ravel)
            return self.manhattan_norm

    def getCorrelation(self):
        if self.correlation_norm:
            return self.correlation_norm
        else:
            self.correlation_norm = correlation(self.img1ravel, self.img2ravel)
            return self.correlation_norm

    def getEuclidean(self):
        if self.euclidean_norm:
            return self.euclidean_norm
        else:
            self.euclidean_norm = euclidean(self.img1ravel, self.img2ravel)
            return self.euclidean_norm

    def getSqueclidean(self):
        if self.sqeuclidean_norm:
            return self.sqeuclidean_norm
        else:
            self.sqeuclidean_norm = sqeuclidean(self.img1ravel, self.img2ravel)
            return self.sqeuclidean_norm

    def getChebyshev(self):
        if self.chebyshev_norm:
            return self.chebyshev_norm
        else:
            self.chebyshev_norm = chebyshev(self.img1ravel, self.img2ravel)
            return self.chebyshev_norm

    def getBraycurtis(self):
        if self.braycurtis_norm:
            return self.braycurtis_norm
        else:
            self.braycurtis_norm = braycurtis(self.img1ravel, self.img2ravel)
            return self.braycurtis_norm

    def getCanberra(self):
        if self.canberra_norm:
            return self.canberra_norm
        else:
            self.canberra_norm = canberra(self.img1ravel, self.img2ravel)
            return self.canberra_norm

    def getCosine(self):
        if self.cosine_norm:
            return self.cosine_norm
        else:
            self.cosine_norm = cosine(self.img1ravel, self.img2ravel)
            return self.cosine_norm