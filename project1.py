# _*_ coding:utf-8 _*_


import scipy
import numpy as np
from math import log
import warnings
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from PIL import Image

warnings.filterwarnings("ignore")#屏蔽log2(0)时出现的警告


# X = [2/3,1/3] #信源概率分布
# Y_over_X = [[3/4,1/4,0],[0,1/2,1/2]] #信道转移矩阵

def input_one_row(string):
    '''
    用户输入一行数据，调用convert_to_float_matrix函数将一行数据转为浮点数array，
    检查一行数据之和是否为1，否则要求用户重新输入
    '''
    flag = 0
    while (flag!=1):
        str_matrix = raw_input(string)
        X = convert_to_float_matrix(str_matrix) #将一行数据转为浮点数array
        print X
        if sum(X) != 1:
            print "一行和不为1，请重新输入"
        else:
            flag = 1
    return X

def convert_to_float_matrix(x):
    '''
    将一行数据转为浮点数array
    '''
    float_matrix = []
    for i in x.split(","):
        try :
            i = float(i) #小数直接转浮点数
        except:
            y = i.split("/")  # 分数转浮点数
            i = float(y[0])/float(y[1])
        float_matrix.append(i)
    return float_matrix

# entropy 熵
def entropy_my(x):
    HX = 0
    for i in x:
        HX += i*log(i,2)
    return -HX

# Conditional entropy 条件熵 #H(Y/X)
def conditinalEntropy_my(Y_over_X):

    HY_over_X = 0 #H(Y/X)
    pXY = [] #p(X,Y),多个x和多个y联合概率
    pxy = []  #p(x,y),一个x和一个y联合概率

    for i,k in zip(X,Y_over_X):
        pxY = [] #p(x,Y)，一个x和多个y联合概率
        for v in k:
            pxy = i*v
            pxY.append(pxy)
        pXY.append(pxY)

    I_Y_over_X = np.log2(Y_over_X)
    I_Y_over_X[np.isneginf(I_Y_over_X)] = 0 #将矩阵中的inf转换为0
    HY_over_X = -np.sum(pXY*I_Y_over_X)
    return pXY,HY_over_X

string = "请输入信源概率分布（逗号分隔开,回车结束），如：1/2,0.5："
X = input_one_row(string)
print "信源概率分布:",X
HX = entropy_my(X)
print "信源熵：",HX

Y_over_X = []
Y_over_x = []
for i in range(len(X)):
    string = ("请输入信道转移概率矩阵第"+str(i+1)+"行（逗号分隔开,回车结束），如：1/2,0.5：")
    Y_over_x= input_one_row(string)
    Y_over_X.append(Y_over_x)
print "信道转移概率矩阵：",Y_over_X
pXY,HY_over_X = conditinalEntropy_my(Y_over_X)
print "条件熵H(Y/X)：",HY_over_X

#联合熵(H(X,Y))
HXY= HX + HY_over_X
print "联合熵H(X,Y)：", HXY

#条件熵H(X/Y)
Y = np.sum(pXY,axis=0)
HY = entropy_my(Y)
HX_over_Y = HXY - HY
print "条件熵H(X/Y):", HX_over_Y

#互信息I(X;Y)
IX_Y = HX - HX_over_Y
print "互信息I(X;Y):", IX_Y

#自学图像熵的相关概念，并应用所学知识，使用matlab求解图像熵
image = Image.open('Rick-and-Morty-NNTB.jpg') #打开图像文件
print "原图："
plt.imshow(image)
plt.show()


grey = np.array(image.convert('L'))#将图像文件转换成灰度图矩阵
print "灰度图："
plt.imshow(grey, cmap=cm.Greys_r)
plt.show()

histogram = plt.hist(grey.flatten(),bins = 256)
print "图像灰度直方图："
plt.show()

grey_shape = grey.shape #计算灰度图的维度

from scipy import stats
grey_frenquency = stats.itemfreq(grey)#计算每个灰度阶对应的频数


grey_Probability = []
for i,v in grey_frenquency:
    v = v/float(grey_shape[0]*grey_shape[1])#将频数除以总数求得每个灰度阶对应的频率
    grey_Probability.append([i,v])
grey_Probability = np.array(grey_Probability)

print "灰度阶像素概率(打印前5个阶及其对应概率)：",grey_Probability[0:5,:]
print "图像一维熵：", entropy_my(grey_Probability[:,1])
