# Louvain_Method
Louvain法のライブラリです。

使用する際は，Louvainクラスのインスタンスを生成してください。その際に使用する引数は，解析するネットワークデータの隣接行列をndarrayの形式で用います．
以下のコードがインスタンスの生成例です。（np_listはndarray形式の隣接行列）

obj = Louvain_Method.Louvain(np_list)

このライブラリでは，Louvain法の実行，実行後のラベルの表示，実行後のModularityの計算が可能です．
以下は，使用例のコードです．

obj.fit(True)
obj.sohw()
obj.get_label_list()
obj.cal_modularity()

fit()によってLouvain法を実行します。引数は、Trueの場合は選択されるノードがランダムとなり、Falseの場合はデータの順となります。
show()によってコミュニティ後のとデータ番号を返します。
get_label_list()によってラベル付けされたリストを返します。
cal_modularity()によってModularityの値を返します。
