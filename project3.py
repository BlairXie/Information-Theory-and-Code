#-*-coding:utf-8-*-
from math import log
import numpy as np
import pprint


def rlc_encode(a):
    '''
    游程码编码
    '''
    flag = a[0] #初始化标签
    count_list = [] #初始化计数值累加序列
    count = 0 #初始化计数值
    for i in range(len(a)):#遍历每一个
        if a[i] == flag:
            count += 1; #当前个计入当前计数值
        else:
            flag = 1-flag #转换flag
            count_list.append(count)
            count = 1 #当前个计入下一个计数值
    count_list.append(count)#将最后一个计数值累加到count_list
    return count_list


def probability_dic(rlc):
    '''
    构造概率字典，符号为字典的键，其概率为字典的值
    '''
    unique, count = np.unique(rlc,return_counts = True) #统计每个数字及其频数
    print('符号',unique,'频数',count)
    prob = {} #概率统计字典初始化

    for i,v in zip(unique,count):
        v = float(v)/len(rlc)#从频数计算概率/频率
        prob[i]=v
    print ('概率统计字典')
    for i in prob.keys():
        print("{0},{1:.4f}".format(i, prob[i]))
    return prob


class huffman_node(object):
    '''
    Huffman节点
    '''
    left = None #初始化类的属性
    right = None
    symbol  = None
    weight = 0
    def __init__(self,i,w):#初始化函数
        self.symbol = i
        self.weight = w
    def __repr__(self):#显示节点内容的函数
        return "%s-%.4f->%s_%s" %(self.item, self.weight,self.left,self.right)


def huffman_tree(prob_dic):
    '''
    构造Huffman树
    '''
    nodes = [huffman_node(k,prob_dic.get(k)) for k in prob_dic.keys()]#每个概率为一个节点

    for _ in range(len(prob_dic)-1):
        nodes.sort(key=lambda x:x.weight)#节点集合按概率从小到大排序，同概率情况下后出现的排在后面
        left = nodes.pop(0)#将比重最小的两个从集合pop出来作为子节点，最小的为左叶子，次小的为右子叶
        right = nodes.pop(0)
        parent = huffman_node('',left.weight+right.weight)#建立父节点，其概率为子节点概率和
        parent.left = left#将比重最小的两个作为子节点
        parent.right = right
        nodes.append(parent)#将父节点重新加入节点集合中
        # pprint.pprint(nodes) #检查每次的节点集合变化情况
    return nodes.pop(0)#返回Huffman树


def huffman_encode(symbol,tree):
    bits = None
    def pre_order(tree,path):
        '''
        采用二叉树先序遍历preorder的方法为对应的符号编码
        '''
        if tree.left:
            pre_order(tree.left, path + '1')#最小的为左叶子，码编为1
        if tree.right:
            pre_order(tree.right, path + '0')#次小的为右子叶，编为0
        if tree.symbol == symbol:#到叶子时检测是否是我们要编码的符号
            nonlocal bits#定义非本地变量bits，可改变外部函数中的bits的值
            bits = path#编码路径对应的编码

    pre_order(tree,"")#运行先序遍历的函数
    return bits


def huffman_decode(bits,tree):
    '''
    Huffman解码，收到1往左子叶走，收到0往右子叶走，走到码字完时对应的节点的符号即为信源符号
    '''
    symbol = None
    for i in bits:
        if i == "1":
            tree = tree.left
        if i == "0":
            tree = tree.right
    symbol = tree.symbol
    return symbol


def entropy(dic):
    '''
    求信源熵
    '''
    HX = 0
    for i in dic.keys():
        HX += dic[i]*log(dic[i],2)
    return -HX

#%%
if __name__ == '__main__':
    np.random.seed(102)#伪随机数种子
    a = np.random.choice([0,1], size=1000, p=[0.3,0.7])#随机生成序列a，每一次出现0,1的概率分别为0.3,0.7
    print ('二进制序列(这里显示前20)',a[0:20])
    a_rlc = rlc_encode(a)#a的游程编码
    print ('游程码(这里显示前20)')
    pprint.pprint(a_rlc[0:20])
    a_prob = probability_dic(a_rlc)#a的概率字典
    tree = huffman_tree(a_prob)#a概率字典对应的Huffman数

    a_huffman_encode_list = {}#a的Huffman编码表
    for i in a_prob.keys():
        a_huffman_encode_list[i] = huffman_encode(i,tree)
    print('Huffman编码表')
    pprint.pprint (a_huffman_encode_list)

    a_rlc_huffman = []#a的Huffman编码
    for i in a_rlc:
        a_rlc_huffman.append(a_huffman_encode_list[i])
    print('游程码转Huffman码(这里显示前20)')
    print(a_rlc_huffman[0:20])

    huffman_rlc = []#a的Huffman解码
    for i in a_rlc_huffman:
        huffman_rlc.append(huffman_decode(i,tree))
    print('Huffman转游程码(这里显示前20)')
    print(huffman_rlc[0:20])

    huffman_rlc_a = []#a的游程码解码
    bit = a[0]
    for count in huffman_rlc:
        while count != 0:
            huffman_rlc_a.append(bit)
            count -= 1
        bit = 1-bit

    print('游程码转源码(这里显示前20)',huffman_rlc_a[0:20])
    print('源码(这里显示前20)',a[0:20])


    k = 0
    for i in a_prob.keys():
        p = a_prob[i]#码字概率
        l = len(a_huffman_encode_list[i])#码字长度
        k += p*l#平均码长
    print ('平均码长',k)
    h = entropy(a_prob)#求信源熵
    y = float(h)/k#编码效率
    print('编码效率{0:.2f}'.format(y))



import pickle

def lzw_compress(file_uncompressed, file_compressed):
    '''
    compress a file use lzw algorithm
    '''

    with open(file_uncompressed,'r') as fo:#打开文件
        string_uncompressed = fo.read()#读取文件内容
    print('原文(前100个字符)',string_uncompressed[0:100])
    dict_size = 256
    dict = {chr(i): chr(i) for i in range(dict_size)}#字典的0-255项预置为ASKII的全部8位字符
    now = '' #当前读入的字符
    result = [] #压缩结果
    for next in string_uncompressed: #遍历整个字符串
        now_next = now + next #当前字符加下一个字符
        if now_next in dict.keys(): #判断当前字符加下一个字符的和在字典中是否存在
            now = now_next#当前字符累加
        else:
            result.append(dict[now]) #输出当前字符
            dict[now_next] = dict_size#把当前字符加下一个字符的和作为一个新字符加入字典
            dict_size += 1#字典长度加1
            now = next#更新当前字符
    result.append(dict[now])#输出最后一个字符

    with open(file_compressed, 'wb') as fw:
        pickle.dump(result, fw)#将压缩序列以2进制文件形式存放在磁盘上
    print('LZW压缩完成')
    return None


def decompress(file_compressed, file_uncompressed):
    '''
    '''
    with open (file_compressed, 'rb') as fr:
        itemlist = pickle.load(fr)#将压缩序列从2进制文件形式恢复出来
    print('LZW压缩结果(前100个字符)', itemlist[0:100])

    dict_size = 256
    dict = {chr(i):chr(i) for i in range(dict_size)}#字典的0-255项预置为ASKII的全部8位字符

    pre = result = itemlist.pop(0)#第一个元素读入上一个元素和输出结果中
    for now in itemlist:#遍历压缩后的list，判断当前元素是否在字典中
        if now in dict.keys():
            w = dict[now]#将对应的元素在字典的值作为输出结果
        elif now == dict_size:#如果此时元素刚好为字典长度
            w = pre + pre[0]#将上一个元素和上一个元素的首个字符的和作为输出结果
        else:
            raise ValueError('Bad compressed value: {0}'.format(now))#输出错误的压缩值
        result += w#输出结果的累加
        dict[dict_size] = pre + w[0]#将上一个元素和当前输出结果的首个字符的和作为输出结果
        dict_size += 1#字典长度加1

        pre = w#更新上一个元素
    with open(file_uncompressed,'w') as fw:
        fw.write(result)#将输出结果（字符串）写入解压缩文件
    print('LZW解压缩结果(前100个字符)',result[0:100])
    print('LZW解压完成')
    return None


file_uncompressed = 'lzw_origin.txt'
file_compressed = 'lzw_compressed.txt'
lzw_compress(file_uncompressed, file_compressed)
file_uncompressed = 'lzw_uncompressed.txt'
decompress(file_compressed,file_uncompressed)

# Arithmetic Coding
# a = ['d','a','c','a','b']
# dict = {'a':{0:0,1:0.4},'b':{0:0.4,1:0.6},'c':{0:0.6,1:0.8},'d':{0:0.8,1:1.0}}
# a = ['a','b','c','c','d']
# dict = {'a':{0:0,1:0.2},'b':{0:0.2,1:0.4},'c':{0:0.4,1:0.8},'d':{0:0.8,1:1.0}}
a = ['d','c','a','c','b']
dict = {'a':{0:0,1:0.2},'b':{0:0.2,1:0.4},'c':{0:0.4,1:0.8},'d':{0:0.8,1:1.0}}
start_pre = 0
end_pre = 1
l = 1
for i in a:# Arithmetic Coding
    start_now = start_pre + l*dict[i][0]
    end_now = start_pre + l*dict[i][1]
    l = (end_now - start_now)
    start_pre = start_now
    # print start_now,end_now
print start_now,end_now
