import numpy as np
import matplotlib.pyplot as plt
import random

class Node:
    def __init__(self, data_list = np.array([]), ad_node_list = np.array([]), edge_weight_list = np.array([]), k_i = 0):
        self.data_list = data_list
        self.af_cluster = -1
        self.ad_node_list = ad_node_list
        self.edge_weight_list = edge_weight_list
        self.k_i = k_i


    def get_data_list(self):
        return self.data_list

    def set_af_cluster(self, cluster):
        self.af_cluster = cluster

    def get_af_cluster(self):
        return self.af_cluster

    def get_ad_node_list(self):
        return self.ad_node_list

    def get_edge_weight_list(self):
        return self.edge_weight_list

    def get_k_i(self):
        return self.k_i


class Cluster:
    def __init__(self, node_list = np.array([]), sigma_tot = 0):
        self.node_list = node_list
        self.sigma_tot = sigma_tot

    def get_node_list(self):
        return self.node_list

    def get_sigma_tot(self):
        return self.sigma_tot

    def add_node_list(self, node):
        self.node_list = np.append(self.node_list, node)
        self.sigma_tot += node.get_k_i()

    def remove_node_list(self, node):
        self.node_list = np.delete(self.node_list, np.where(self.node_list == node)[0][0], 0)
        self.sigma_tot -= node.get_k_i()


class Louvain:
    def __init__(self, input_data):
        self.data_list = input_data.copy()
        self.node_list = np.array([])
        self.cluster_list = np.array([])
        self.before_cluster_list = np.array([])
        self.m = self.data_list.sum() / 2

    def fit(self, seed = -1):
        #初期のデータ構造を作成
        for i, data in enumerate(self.data_list):
            edge_list = np.where(data != 0)[0]
            weight_list = data[edge_list]
            k_i = weight_list.sum()
            node_obj = Node(data_list = np.array([i]), ad_node_list = edge_list, edge_weight_list = weight_list, k_i = k_i)
            cluster_obj = Cluster(node_list = np.array([node_obj]), sigma_tot = k_i)
            node_obj.set_af_cluster(cluster_obj)
            self.cluster_list = np.append(self.cluster_list, cluster_obj)
            self.node_list = np.append(self.node_list, node_obj)

        self.before_cluster_list = self.cluster_list

        if seed != -1:
            while True:
                check = False #ノードの移動を確認する変数
                np.random.seed(seed)
                select_list = np.random.permutation(self.node_list.shape[0])
                for node in self.node_list[select_list]:
                    check += self.move_node(node)

                if check == False:
                    self.node_edge_updata()
                    if self.before_cluster_list.shape[0] == self.cluster_list.shape[0]:
                        break

                    else:
                        self.before_cluster_list = self.cluster_list

        else:
            while True:
                check = False #ノードの移動を確認する変数
                for node in self.node_list:
                    check += self.move_node(node)

                if check == False:
                    self.node_edge_updata()
                    if self.before_cluster_list.shape[0] == self.cluster_list.shape[0]:
                        break

                    else:
                        self.before_cluster_list = self.cluster_list


    def move_node(self, node):
        node_cluster = node.get_af_cluster() #ノードが所属しているクラスタ
        k_i = node.get_k_i() #ノードのk_i
        #ノードに隣接しているクラスタと，エッジの重みを取得
        k_i_in_dict = {}
        self_loop = False #自己ループの有無を管理する
        for ad_node, ad_weight in zip(node.get_ad_node_list(), node.get_edge_weight_list()):
            ad_node_obj = self.node_list[ad_node]

            #自己ループがあるかを確認
            if ad_node_obj == node:
                self_loop = True
                self_loop_weight = ad_weight

            ad_cluster = ad_node_obj.get_af_cluster()
            if ad_cluster in k_i_in_dict:
                k_i_in_dict[ad_cluster] += ad_weight

            else:
                k_i_in_dict[ad_cluster] = ad_weight

        #現在のクラスタから離れた場合のModularityの減少量を計算
        if node_cluster.get_node_list().shape[0] == 1:
            minus_delta_q = 0
            k_i_in_dict.pop(node_cluster, None)

        else:
            sigma_tot = node_cluster.get_sigma_tot() - k_i
            if node_cluster in k_i_in_dict:
                if self_loop == False:
                    k_i_in = k_i_in_dict.pop(node_cluster)

                else:
                    k_i_in = k_i_in_dict.pop(node_cluster) - self_loop_weight

            else:
                k_i_in = 0

            minus_delta_q = (k_i_in / self.m) - ((sigma_tot * k_i) / (2 * (self.m ** 2)))

        #ノードに隣接しているクラスタへ移動した際のModualrityの増加量を計算
        delta_q_dict = {}
        for ad_cluster, k_i_in in k_i_in_dict.items():
            sigma_tot = ad_cluster.get_sigma_tot()
            plus_delta_q = (k_i_in / self.m) - ((sigma_tot * k_i) / (2 * (self.m ** 2)))
            delta_q_dict[ad_cluster] = plus_delta_q - minus_delta_q

        #ノードの移動処理
        if len(delta_q_dict) == 0:
            return False

        elif max(delta_q_dict.values()) > 0:
            move_cluster = max(delta_q_dict, key = delta_q_dict.get)
            if node_cluster.get_node_list().shape[0] == 1:
                self.cluster_list = np.delete(self.cluster_list, np.where(self.cluster_list == node_cluster)[0][0], 0)
            
            else:
                node_cluster.remove_node_list(node)

            move_cluster.add_node_list(node)
            node.set_af_cluster(move_cluster)
            return True

        else:
            return False


    def node_edge_updata(self):
        #新しいリストの作成
        new_node_list = np.array([])
        new_cluster_list = np.array([])

        #クラスタが集約されるノードの作成
        for cluster in self.cluster_list:
            ad_cluster_dict = {}
            new_data_list = np.array([])
            for node in cluster.get_node_list():
                new_data_list = np.append(new_data_list, node.get_data_list())
                for ad_node, ad_weight in zip(node.get_ad_node_list(), node.get_edge_weight_list()):
                    ad_cluster = self.node_list[ad_node].get_af_cluster()
                    if ad_cluster in ad_cluster_dict:
                        ad_cluster_dict[ad_cluster] += ad_weight

                    else:
                        ad_cluster_dict[ad_cluster] = ad_weight

            new_ad_node_list = np.array([], dtype = int)
            for ad_cluster in ad_cluster_dict.keys():
                new_ad_node_list = np.append(new_ad_node_list, np.where(self.cluster_list == ad_cluster)[0][0])
            
            weight_list = np.array(list(ad_cluster_dict.values()))
            k_i = weight_list.sum()
            node_obj = Node(data_list = new_data_list, ad_node_list = new_ad_node_list, edge_weight_list = weight_list, k_i = k_i)
            cluster_obj = Cluster(node_list = np.array([node_obj]), sigma_tot = k_i)
            node_obj.set_af_cluster(cluster_obj)
            new_node_list = np.append(new_node_list, node_obj)
            new_cluster_list = np.append(new_cluster_list, cluster_obj)

        self.node_list = new_node_list.copy()
        self.cluster_list = new_cluster_list.copy()
                

    def show(self):
        for node in self.node_list:
            print(node.get_data_list())

    def get_label_list(self):
        label_list = np.zeros((self.data_list.shape[0]))
        count = 0
        for node in self.node_list:
            for data in node.get_data_list():
                label_list[int(data)] = count

            count += 1

        return label_list

    def cal_modularity(self):
        temp_sum = 0
        for node_i in self.node_list:
            k_i = node_i.get_k_i()
            for node_j in self.node_list:
                if node_i.get_af_cluster() == node_j.get_af_cluster():
                    temp_index = np.where(self.node_list[node_i.get_ad_node_list()] == node_j)[0]
                    if temp_index.shape[0] != 0:
                        A_ij = node_i.get_edge_weight_list()[temp_index[0]]

                    else:
                        A_ij = 0

                    k_j = node_j.get_k_i()
                    temp_sum += A_ij - ((k_i * k_j) / (2 * self.m))

        return temp_sum / (2 * self.m)