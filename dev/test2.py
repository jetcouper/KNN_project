import numpy as np

Y, X = np.ogrid[0:3, 0:4]
Y1, X1 = np.meshgrid(np.arange(3), np.arange(4), indexing='xy')
Y2, X2 = np.mgrid[0:3, 0:4]
Y3, X3 = np.indices((3,4))


print(Y.shape, X.shape)
print(Y1.shape, X1.shape)
print(Y2.shape, X2.shape)
print(Y3.shape, X3.shape)
pass
