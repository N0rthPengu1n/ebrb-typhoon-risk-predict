#!/usr/bin/env python
# coding: utf-8

# In[12]:


from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def perform_pca_risk_assessment(file_path):
    # 加载数据
    data = pd.read_excel(file_path)

    # 选择需要降维的列
    columns_to_reduce1 = data.iloc[:, 2:6]  # 脆弱性相关列
    columns_to_reduce2 = data.iloc[:, 6:9]  # 防灾减灾相关列
    s3 = data.iloc[:, 1].values.reshape(-1, 1)  # 危险性列

    # 初始化 PCA，将维度降至1维
    pca = PCA(n_components=1)

    # 对选定的列应用 PCA
    reduced_data1 = pca.fit_transform(columns_to_reduce1)
    reduced_data2 = pca.fit_transform(columns_to_reduce2)

    # 初始化标准化器
    scaler = StandardScaler()

    # 标准化 PCA 降维结果和危险性数据
    standardized_pca_results1 = scaler.fit_transform(reduced_data1)
    standardized_pca_results2 = scaler.fit_transform(reduced_data2)
    standardized_results3 = scaler.fit_transform(s3)

    # 将标准化后的数据转换为 DataFrame
    reduced_data1_df = pd.DataFrame(standardized_pca_results1, columns=['脆弱性'])
    reduced_data2_df = pd.DataFrame(standardized_pca_results2, columns=['防灾减灾'])
    data3_df = pd.DataFrame(standardized_results3, columns=['危险性'])

    # 将降维和标准化后的数据合并
    data_final = pd.concat([data3_df, reduced_data1_df, reduced_data2_df], axis=1)

    return data_final

def perform_clustering(data, n_clusters=4):
    # 应用K-Means聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(data)

    return clusters

def perform_random_forest(data, labels):
    # 分割数据集
    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.3, random_state=42)

    # 创建并训练随机森林模型
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    # 在测试集上进行预测
    y_pred = rf.predict(X_test)

    return y_pred

def map_cluster_to_risk_level(cluster):
    # 根据图片中的对应关系映射聚类结果到风险等级
    mapping = {2: "低", 0: "中低", 3: "中高", 1: "高"}
    return mapping[cluster]

def run(standard_excelfile, progress_callback=None):
    # 报告进度函数
    def report_progress(step, total_steps):
        if progress_callback:
            progress = int((step / total_steps) * 100)
            print(f"Reporting progress: {progress}%")
            progress_callback(progress)

    total_steps = 4   # 现在我们有4个主要步骤
    current_step = 0

    # 步骤1: 特征提取
    processed_data = perform_pca_risk_assessment(standard_excelfile)
    current_step += 1
    report_progress(current_step, total_steps)

    # 步骤2: 聚类
    clusters = perform_clustering(processed_data, n_clusters=4)
    current_step += 1
    report_progress(current_step, total_steps)

    # 步骤3: 随机森林分类
    rf_predictions = perform_random_forest(processed_data, clusters)
    current_step += 1
    report_progress(current_step, total_steps)

    # 步骤4: 结果处理和输出
    output = pd.DataFrame({
        '序号': range(1, len(rf_predictions) + 1),
        '风险等级': [map_cluster_to_risk_level(pred) for pred in rf_predictions]
    })
    current_step += 1
    report_progress(current_step, total_steps)

    return output

if __name__ == "__main__":
    sample_path = Path(__file__).resolve().parents[1] / "data" / "standardized_risk_assessment.xlsx"
    print(run(sample_path).to_string(index=False))
