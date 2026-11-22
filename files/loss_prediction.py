#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import numpy as np


def EBRB(x, u, Aw, xtst, b):
    # 训练数据集计算分布式置信度
    innuml = x.shape[1]  # 获取矩阵x的列数
    innumh = x.shape[0]  # 获取矩阵x的行数
    unum = u.shape[1]  # 获取矩阵u的列数

    A = np.zeros((innumh, unum, innuml))  # 构造三维零矩阵
    for k in range(0, innumh):
        for i in range(0, innuml):
            for j in range(0, unum - 1):
                if u.iloc[i, j] <= x.iloc[k, i] and x.iloc[k, i] <= u.iloc[i, j + 1]:
                    A[k, j, i] = (u.iloc[i, j + 1] - x.iloc[k, i]) / (u.iloc[i, j + 1] - u.iloc[i, j])
                    A[k, j + 1, i] = 1 - A[k, j, i]

    # 测试数据集计算分布式置信度
    innumltst = xtst.shape[1]  # 列数
    innumhtst = xtst.shape[0]  # 行数
    unum = u.shape[1]  # 获取矩阵u的列数(keshenglue)

    Atst = np.zeros((innumhtst, unum, innumltst))
    for k in range(0, innumhtst):
        for j in range(0, unum - 1):
            for i in range(0, innumltst):
                if u.iloc[i, j] <= xtst.iloc[k, i] and xtst.iloc[k, i] <= u.iloc[i, j + 1]:
                    Atst[k, j, i] = (u.iloc[i, j + 1] - xtst.iloc[k, i]) / (u.iloc[i, j + 1] - u.iloc[i, j])
                    Atst[k, j + 1, i] = 1 - Atst[k, j, i]

    # 计算个体匹配度
    E = []
    weight = []
    L = A.shape[0]  # 规则数(矩阵x)
    L1 = Atst.shape[0]  # 输入数据x数量，即xtst
    M = Aw.shape[0]  # 前提属性个数
    N = x.shape[1]  # 评价等级数
    Aw1 = Aw / np.max(Aw)
    dist1 = []
    dist = []
    sk = []
    sk3 = []
    sk1 = []
    sk1b = []
    for i1 in range(0, L1):
        for j1 in range(0, L):
            x2 = Atst[i1]
            a2 = A[j1]
            dist1.append(x2 - a2)
    for i in range(len(dist1)):
        dist.append(np.sum(dist1[i] ** 2, axis=0))
    for i in range(len(dist)):
        sk.append(1 - (np.divide(dist[i], 2) ** 0.5))

    # 计算激活权重
    count = 0
    for j in range(L1):
        sk2 = []
        for i in range(L):
            sk2.append(sk[count * L + i])
        count = count + 1
        sk3.append(sk2)
    for i in range(L1):
        for j in range(L):
            sk4 = sk3[i][j]
            Aw1_repeated = np.tile(Aw1, int(np.ceil(len(sk4) / len(Aw1))))[:len(sk4)]
            sk1b.append(np.power(sk4, Aw1_repeated))
        sk1.append(sk1b)
        sk1b = []
    for i in range(L1):
        E1 = []
        for j in range(L):
            E1.append(np.prod(sk1[i][j]))
        E.append(E1)

    weight = [[value / row_sum for value in row] for row, row_sum in zip(E, np.sum(E, axis=1))]

    # 合成激活规则
    F = []
    F1 = []
    E1 = []
    k1 = []
    mi = []
    mh1 = []
    for i2 in range(L1):
        n = b.shape[1]  # 评价等级数
        F.append(np.repeat(weight[i2], n))
    F1 = np.array(F).reshape(L1, L, n) * np.array(b)
    mnj = F1.transpose([0, 2, 1])
    mhj1 = np.negative(weight) + 1
    B = -np.sum(b, axis=1) + 1  # B = -np.sum(b) + 1
    C = np.array(B).T  # B.T
    mhj2 = (np.array(weight)) * C
    D1 = np.zeros((L1, L, n))
    for i2 in range(0, L1):
        for i in range(0, n):
            D1[i2, :, i] = mnj[i2][i] + mhj1[i2] + mhj2[i2]
        E1.append(mhj1[i2, :] + mhj2[i2, :])
    for i2 in range(0, L1):
        k1.append(1 / (np.sum(np.prod(D1[i2], axis=0)) - (n - 1) * np.prod(E1[i2])))
        mi.append(k1[i2] * (np.prod(D1[i2], axis=0) - np.prod(E1[i2])))
        mh1.append(k1[i2] * np.prod(mhj1[i2]))
    bi = []
    for i in range(L1):
        bi.append(mi[i] / (1 - mh1[i]))

    return pd.DataFrame(bi)

def equal_partition_df(input_df, n):
    # 初始化一个空的DataFrame，用于存放结果
    result_df = pd.DataFrame()

    # 对于输入DataFrame的每一列
    for column in input_df.columns:
        # 获取该列的最小值和最大值
        min_value = input_df[column].min()
        max_value = input_df[column].max()

        # 生成等分后的数组
        partitioned_array = np.linspace(min_value, max_value, num=n)

        # 将数组转换为DataFrame，并进行纵向拼接
        partitioned_df = pd.DataFrame(partitioned_array, columns=[column])
        result_df = pd.concat([result_df, partitioned_df], axis=1)
        result = result_df.T

    return result


######EBRB+CNN优化
def CNN_EBRB(x, u, Aw, xtst, b):
    # 训练数据集计算分布式置信度
    innuml = x.shape[1]  # 获取矩阵x的列数
    innumh = x.shape[0]  # 获取矩阵x的行数
    unum = u.shape[1]  # 获取矩阵u的列数

    import numpy as np

    A = np.zeros((innumh, unum, innuml))  # 构造三维零矩阵
    for k in range(0, innumh):
        for i in range(0, innuml):
            for j in range(0, unum - 1):
                if u.iloc[i, j] <= x.iloc[k, i] and x.iloc[k, i] <= u.iloc[i, j + 1]:
                    A[k, j, i] = (u.iloc[i, j + 1] - x.iloc[k, i]) / (u.iloc[i, j + 1] - u.iloc[i, j])
                    A[k, j + 1, i] = 1 - A[k, j, i]

    # 测试数据集计算分布式置信度
    innumltst = xtst.shape[1]  # 列数
    innumhtst = xtst.shape[0]  # 行数
    unum = u.shape[1]  # 获取矩阵u的列数(keshenglue)

    Atst = np.zeros((innumhtst, unum, innumltst))
    for k in range(0, innumhtst):
        for j in range(0, unum - 1):
            for i in range(0, innumltst):
                if u.iloc[i, j] <= xtst.iloc[k, i] and xtst.iloc[k, i] <= u.iloc[i, j + 1]:
                    Atst[k, j, i] = (u.iloc[i, j + 1] - xtst.iloc[k, i]) / (u.iloc[i, j + 1] - u.iloc[i, j])
                    Atst[k, j + 1, i] = 1 - Atst[k, j, i]

    # 个体匹配度
    L = A.shape[0]  # 规则数(矩阵x)
    L1 = Atst.shape[0]  # 输入数据数量，即xtst行数
    M = Aw.shape[0]  # 前提属性个数
    N = x.shape[1]  # 前提属性个数
    Aw1 = Aw / np.max(Aw)  # 前提属性权重归一化

    dist1b = []
    dist1c = []
    distb = []
    skb = []
    window_size = 6

    # 计算每条输入数据对k条规则
    for i1 in range(0, L1):  # 输入数量
        for j1 in range(0, L):  # 规则数
            x2 = Atst[i1].T
            a2 = A[j1].T
            L3 = x2.shape[0]
            L4 = x2.shape[1]
            for i2 in range(L3 - window_size + 1):
                for j2 in range(L4 - window_size + 1):
                    window_x2 = x2[i2:i2 + window_size, j2:j2 + window_size]
                    window_a2 = a2[i2:i2 + window_size, j2:j2 + window_size]
                    diff = window_x2 - window_a2
                    dist1b.append(diff)
    for i in range(len(dist1b)):
        distb.append(np.sum(dist1b[i] ** 2))
    for i in range(len(distb)):
        skb.append(1 - ((distb[i] / 2) ** 0.5))  # 个体匹配度

    # 计算激活权重
    sk3b = []
    com = (L3 - window_size + 1) * (L4 - window_size + 1)
    for j in range(L1):
        sk3b.append(skb[j * L * com:(j + 1) * L * com])
    L7 = L4 - window_size + 1
    L8 = L3 - window_size + 1
    sk3c = []
    group_size = L7
    for row in sk3b:
        num_groups = len(row) // group_size
        groups = [row[i * group_size:(i + 1) * group_size] for i in range(num_groups)]
        combined_groups = []
        for i in range(0, len(groups), L8):
            if i + 1 < len(groups):
                combined_group = [groups[i], groups[i + 1]]
                combined_groups.append(combined_group)
            else:
                combined_groups.append([groups[i]])
        sk3c.append(combined_groups)
    sk3d = np.array(sk3c)
    sk3e = np.transpose(sk3d, axes=(0, 1, 3, 2))
    Eb = []
    for i in range(L1):
        E1c = []
        for j in range(L):
            E1b = []
            for k in range(L7):
                E1b.append(np.prod(sk3e[i][j][k]))
            E1c.append(E1b)
        Eb.append(E1c)
    EB = np.array(Eb)
    weightb = np.zeros_like(EB, dtype=float)
    for i in range(EB.shape[0]):
        for j in range(EB.shape[1]):
            for k in range(EB.shape[2]):  #
                col_sum = np.sum(EB[i, :, k])
                weightb[i, j, k] = EB[i, j, k] / col_sum
    weight = [[max(row) for row in plane] for plane in weightb]
    bweight = np.array(weight)
    fweight = []
    for i in range(L1):
        weight = bweight[i]
        a = np.sort(bweight)[i][::-1][29]
        act_weight = np.where(weight > a, weight, 0)
        fweight.append(act_weight)
    weight1 = np.zeros_like(fweight)
    for i in range(L1):
        for j in range(L):
            epsilon = 1e-10
            weight1[i][j] = fweight[i][j] / (np.sum(fweight, axis=1)[i] + epsilon)

    # 合成激活规则
    F = []
    F1 = []
    E1 = []
    k1 = []
    mi = []
    mh1 = []
    for i2 in range(L1):
        n = b.shape[1]
        F.append(np.repeat(weight1[i2], n))
    F1 = np.array(F).reshape(L1, L, n) * np.array(b)
    mnj = F1.transpose([0, 2, 1])
    mhj1 = np.negative(weight1) + 1
    B = -np.sum(b, axis=1) + 1
    C = np.array(B).T
    mhj2 = (np.array(weight1)) * C

    D1 = np.zeros((L1, L, n))
    for i2 in range(0, L1):
        for i in range(0, n):
            D1[i2, :, i] = mnj[i2][i] + mhj1[i2] + mhj2[i2]
        E1.append(mhj1[i2, :] + mhj2[i2, :])

    for i2 in range(0, L1):
        k1.append(1 / (np.sum(np.prod(D1[i2], axis=0)) - (n - 1) * np.prod(E1[i2])))
        mi.append(k1[i2] * (np.prod(D1[i2], axis=0) - np.prod(E1[i2])))
        mh1.append(k1[i2] * np.prod(mhj1[i2]))

    bi = []
    epsilon = 1e-10
    for i in range(L1):
        bi.append(mi[i] / (((1 - mh1[i])) + epsilon))

    return pd.DataFrame(bi)


def run(train_csvfile, test_csvfile, progress_callback=None):
    # 报告进度函数
    def report_progress(step, total_steps):
        if progress_callback:
            progress = int((step / total_steps) * 100)
            print(f"Reporting progress: {progress}%")
            progress_callback(progress)

    total_steps = 5  # 假设我们有5个主要步骤
    current_step = 0

    # 步骤1: 数据加载和预处理
    Aw = np.array([1, 1, 1, 1, 1, 1, 1])
    x = pd.read_csv(train_csvfile, encoding="gbk")
    xtst = pd.read_csv(test_csvfile, encoding="gbk")
    for column in x.columns:
        x[column] = pd.to_numeric(x[column], errors='coerce')
    for column in xtst.columns:
        xtst[column] = pd.to_numeric(xtst[column], errors='coerce')
    current_step += 1
    report_progress(current_step, total_steps)

    # 步骤2: 数据分割和转换
    D = x.pop('直接经济损失(亿元)')
    Dtest = xtst.pop('直接经济损失(亿元)')
    Dtest = pd.DataFrame(Dtest).reset_index().drop(columns=['index'])
    df = pd.DataFrame(x)
    df2 = pd.DataFrame(D)
    current_step += 1
    report_progress(current_step, total_steps)

    # 步骤3: 模型参数设置
    urate = 7
    Durate = 8
    u = equal_partition_df(df, urate)
    Du = equal_partition_df(df2, Durate).T
    Du = Du.squeeze(1)
    Du = np.array(Du)
    xnum = x.shape[0]
    innum = len(D)
    unum = len(Du)
    b = np.zeros((innum, unum))
    for i in range(innum):
        for j in range(unum - 1):
            if Du[j] <= D[i] and D[i] <= Du[j + 1]:
                b[i, j] = (Du[j + 1] - D[i]) / (Du[j + 1] - Du[j])
                b[i, j + 1] = 1 - b[i, j]
    current_step += 1
    report_progress(current_step, total_steps)

    # 步骤4: 模型训练
    bi = CNN_EBRB(x, u, Aw, xtst, b)
    current_step += 1
    report_progress(current_step, total_steps)

    # 步骤5: 结果处理和输出
    f = []
    l = bi.shape[0]
    m = bi.shape[1]
    for i in range(l):
        sum = bi.iloc[i].sum()
        bN = bi.iloc[i][m - 1]
        b1 = bi.iloc[i][0]
        if (sum < 0.999999):
            f.append((b1 + bN) / 2 * (1 - sum))
        else:
            f.append(np.dot(bi.iloc[i], Du))

    f = pd.DataFrame(f, columns=['prediction'])
    f = f.round(6)
    Dtest = Dtest * 10000
    Dtest = Dtest.round(6)
    bi_rounded = bi.round(6)
    result = pd.concat([bi_rounded, Dtest], axis=1)
    output = result.rename(columns={0: 'D1', 1: "D2", 2: "D3", 3: "D4", 4: "D5", 5: "D6", 6: "D7", 7: "D8"})
    output.index = range(1, len(output) + 1)
    for col in output.columns:
        output[col] = output[col].apply(lambda x: f"{x:.6f}")
    current_step += 1
    report_progress(current_step, total_steps)

    return output.values.tolist()