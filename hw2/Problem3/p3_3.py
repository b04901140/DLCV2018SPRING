import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier


def hard_sum(distance_table):
    hist_data = np.zeros((distance_table.shape[1]))
    for i, dis in enumerate(distance_table):
        hist_data[np.argmin(dis)] += 1
    return hist_data

def soft_sum(distance_table):
    hist_data = np.zeros((distance_table.shape[1]))
    for dis in distance_table:
        normalized_dis = np.reciprocal(dis)/np.sum(np.reciprocal(dis))
        hist_data += normalized_dis
    return hist_data

def soft_max(distance_table):
    hist_data = np.zeros((distance_table.shape[1]))
    normalized_dis_table = np.copy(distance_table)

    for i, dis in enumerate(normalized_dis_table):
        normalized_dis_table[i,:] = np.reciprocal(dis)/np.sum(np.reciprocal(dis))
    for i, centroid_i in enumerate(normalized_dis_table.T):
        hist_data[i] = np.max(centroid_i)

    return hist_data


# train total 50 pics and get centroids
category_list = ['Coast', 'Forest', 'Highway', 'Mountain', 'Suburb']

#def Get_keypoints(mode):
key_dict = []
train_list = []
for category in category_list:
    train_list += [category+'/'+img_name for img_name in os.listdir('train-10/'+category)]
for img_name in train_list:
    img = cv2.imread('train-10/'+img_name)
    surf = cv2.xfeatures2d.SURF_create(1000)
    kp, des = surf.detectAndCompute(img, None)
    for des_i in des:
        key_dict.append(des_i)
    #return img_name_list, key_point_dict


#train_list, key_dict = Get_keypoints('train-10/')
train_interst_points = np.array(key_dict)
print(train_interst_points.shape)

kmeans = KMeans(n_clusters=50, max_iter=5000).fit(train_interst_points)
#np.save('centroids.npy', kmeans.cluster_centers_)
#centroids = np.load('centroids.npy')
centroids = kmeans.cluster_centers_
print(centroids.shape)  # 50 * 64
print("===== Get centroids Done =====")

# construct distance table of targer images with the centroids
"""
target_list = ['Coast/image_0022.jpg',
            'Forest/image_0020.jpg',
            'Highway/image_0018.jpg',
            'Mountain/image_0044.jpg',
            'Suburb/image_0016.jpg']

for img_path in target_list:
    img = cv2.imread('train-10/'+ img_path)
    #surf = cv2.xfeatures2d.SURF_create()
    kp, des = surf.detectAndCompute(img, None)
    distance_table = np.zeros((des.shape[0], centroids.shape[0]))
    for i, des_i in enumerate(des):
        for j, centroids_j in enumerate(centroids):
            distance_table[i, j] = np.linalg.norm(des_i-centroids_j)
    #print(distance_table)
    print(distance_table.shape)

    plt.bar(range(distance_table.shape[1]), hard_sum(distance_table))
    plt.savefig('results/p3_3_1000/'+img_path.replace('/', '_')+'_hardsum_hist.jpg')
    plt.clf()
    plt.bar(range(distance_table.shape[1]), soft_sum(distance_table))
    plt.savefig('results/p3_3_1000/'+img_path.replace('/', '_')+'_softsum_hist.jpg')
    plt.clf()
    plt.bar(range(distance_table.shape[1]), soft_max(distance_table))
    plt.savefig('results/p3_3_1000/'+img_path.replace('/', '_')+'_softmax_hist_.jpg')
    plt.clf()
"""


# Problem 3(d)
#knn = KNeighborsClassifier(n_neighbors=k)
train_data_hardsum = []
train_data_softsum = []
train_data_softmax = []

train_size = 10
train_label = [0]*train_size + [1]*train_size + [2]*train_size + [3]*train_size + [4]*train_size
test_label = [i for i in range(5) for j in range(100)]

for img_path in train_list:
    img = cv2.imread('train-10/'+ img_path)
    kp, des = surf.detectAndCompute(img, None)
    distance_table = np.zeros((des.shape[0], centroids.shape[0]))
    for i, des_i in enumerate(des):
        for j, centroids_j in enumerate(centroids):
            distance_table[i, j] = np.linalg.norm(des_i-centroids_j)
    train_data_hardsum.append(hard_sum(distance_table))
    train_data_softsum.append(soft_sum(distance_table))
    train_data_softmax.append(soft_max(distance_table))
print("===== training done =====")
#test_key_dict = Get_keypoints('test-100/')
#train_interst_points = np.array(test_key_dict)
#print(train_interst_points.shape)
test_list = []
for category in category_list:
    test_list += [category+'/'+img_name for img_name in os.listdir('test-100/'+category)]

test_data_hardsum = []
test_data_softsum = []
test_data_softmax = []

for img_path in test_list:
    img = cv2.imread('test-100/'+ img_path)
    kp, des = surf.detectAndCompute(img, None)
    distance_table = np.zeros((des.shape[0], centroids.shape[0]))
    for i, des_i in enumerate(des):
        for j, centroids_j in enumerate(centroids):
            distance_table[i, j] = np.linalg.norm(des_i-centroids_j)
    #print(distance_table.shape)
    test_data_hardsum.append(hard_sum(distance_table))
    test_data_softsum.append(soft_sum(distance_table))
    test_data_softmax.append(soft_max(distance_table))

train_data_hardsum = np.array(train_data_hardsum)
train_data_softsum = np.array(train_data_softsum)
train_data_softmax = np.array(train_data_softmax)
test_data_hardsum = np.array(test_data_hardsum)
test_data_softsum = np.array(test_data_softsum)
test_data_softmax = np.array(test_data_softmax)

print(train_data_hardsum.shape)
print(test_data_hardsum.shape)
#print(train_data_softmax.shape)

knn1 = KNeighborsClassifier(n_neighbors=5)
knn1.fit(train_data_hardsum, train_label)
correct = knn1.score(test_data_hardsum, test_label)
print("Hard-Sum Score : ", correct)

knn2 = KNeighborsClassifier(n_neighbors=5)
knn2.fit(train_data_softsum, train_label)
correct = knn2.score(test_data_softsum, test_label)
print("Soft-Sum Score : ", correct)

knn3 = KNeighborsClassifier(n_neighbors=5)
knn3.fit(train_data_softmax, train_label)
correct = knn3.score(test_data_softmax, test_label)
print("Soft-Max Score : ", correct)