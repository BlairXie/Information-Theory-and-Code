#%%
import numpy as np
import pickle
file_path = 'project4.txt'
# %%
def cyclic_encode(input):
    '''
    (7,3)循环码编码,c = m*g,g(x) = x^4+x^3+x^2+1
    输入:码元序列
    输出:循环码编码后序列
    '''
    m = []
    c = []
    for k in input:
        m.append(k)
        if len(m) == 3: #对输入序列每3个取作一组进行编码
            r = [0,0,0,0]#余式r = [r0,r1,r2,r3]
            for i in range(3):    #构建g(x) = x^4+x^3+x^2+1形成的除法电路
                temp = (r[3] + m[i])%2
                r[3] = (r[2] + temp)%2
                r[2] = (r[1] + temp)%2
                r[1] = r[0]
                r[0] = temp

            k = r[3::-1]#将余式r = [r0,r1,r2,r3]转换为k = [r3,r2,r1,r0]
            c = c + m + k #c = m*x^(n-k)+r得到（7,3）系统循环码

            m = []
    return c


# %%
def dsc_channel(s,p):
    '''
    模拟信号通过DSB信道时增加的信道噪声
    随机差错:按照平均错误概率Pe=0.3随机产生差错图样e,0表示没错，1表示错误
    输入:发码序列,道错误概率Pe
    输出:收码序列
    '''
    channel_error_probablity = p#信道错误概率Pe
    e = np.random.choice([0,1],size = len(s),p = [1-channel_error_probablity,channel_error_probablity])
    #e为差错图样
    r = []
    for i,k in zip(s,e):
        r.append((i + k) % 2) #收到码字 = 循环码和差错图样模二加/亦或
    return r


#%%
def min_hamming_distance_decoder(r):
    '''
    对于BSC，汉明距离译码也是最大似然译码也是最佳译码
    将收码的每一个码字和发码的码字表相比较,选取发码码字表中和收码的汉明距离最小的码字作为译码估值
    输入:收码序列
    输出:发码的译码估值序列
    '''
    s_dict = {0:[0,0,0,0,0,0,0],1:[0,0,1,1,1,0,1],2:[0,1,0,0,1,1,1],3:[0,1,1,1,0,1,0], \
                4:[1,0,0,1,1,1,0],5:[1,0,1,0,0,1,1],6:[1,1,0,1,0,0,1],7:[1,1,1,0,1,0,0]}
    #发码（7,3）循环码所有码字组成字典

    s_ = []#译码估值，由收码估计发码
    n = []#缓存码字
    for i in r:
        n.append(i)
        if len(n) == 7:#每一个收码码字
            xor_sum_list = np.array([])#汉明距离列表
            for z in s_dict:#遍历发码码表
                xor_sum = 0#亦或和，即是汉明距离
                for j,k in zip(n,s_dict[z]): #将收码的每一个码字和发码的码表相比较
                    xor_sum += (j+k)%2 #求汉明距离
                xor_sum_list = np.append(xor_sum_list,xor_sum)

            min_i = np.argmin(xor_sum_list)#返回汉明距离列表中的最小值对应的index，多个最小返回第一个index
            s_.append(s_dict[min_i])#将index对应的发码码字表中的码字作为译码估值
            n = []#清空缓存码字


    return s_

if __name__ == '__main__':#直接运行本python文件时执行，调用本py文件不执行
    ave_err_ratio_list = []#平均误码率列表
    P = [i/float(10000) for i in range(0,101,1)] #信道错误概率Pe列表，P:让P取值为0到0.01，步长为0.0001，共101
    flag = 0
    for p in P:#遍历道错误概率Pe列表
        err_ratio_list = []#误码率列表
        for se in range(100):#遍历产生100个不同的发码
            np.random.seed(se)
            #生成随机码元序列，其中0和1概率分别为0.3和0.7
            m = np.random.choice([0,1], size = 10000, p = [0.3,0.7])#消息组m = [m^(n-1)...m4,m3,m2,m1,m0]
            s = cyclic_encode(m)#（7,3）循环码编码/发码
            r = dsc_channel(s,p)#通过信道得到收码序列
            s_ = min_hamming_distance_decoder(r)#汉明最小距离译码得到发码估值

            #还原消息
            m_ = []#还原的消息
            for i in s_:
                m_ += i[0:3]

            #计算误码率;
            err = 0 #错误个数
            for i,j in zip(m,m_):
                err += (i+j)%2
            err_ratio = float(err)/len(m) #误码率
            err_ratio_list.append(err_ratio)


            if p == 0.01:
                if flag == 0 and se == 20:
                    with open(file_path,'wb') as fw:
                        pickle.dump([m,s,r,s_,m_,p,err,err_ratio],fw)#记录某一次数据
                    flag = 1

        ave_err_ratio = float(sum(err_ratio_list))/len(err_ratio_list)
        ave_err_ratio_list.append(ave_err_ratio)

    import matplotlib.pyplot as plt
    figure = plt.gcf()
    plt.plot(P,ave_err_ratio_list)#信道错误概率Pe和平均误码率之间的关系曲线
    plt.xlabel('channel error probablity')
    plt.ylabel('average error ratio')
    plt.show()
    figure.savefig('project4.png',dpi = 100)#保存图片

    with open(file_path,'rb') as fr:
        m,s,r,s_,m_,p,err,err_ratio = pickle.load(fr)#读取并打印某一次数据
        print '消息序列（前15）',m[0:15].__repr__()
        print '发码（前15）', s[0:35]
        print '收码（前15）', r[0:35]
        print '发码估值（前15）', s_[0:5]
        print '还原消息（前15）', m_[0:15]
        print '消息序列长度', len(m),'信道错误概率', p, '误码个数', err, '误码率', err_ratio
