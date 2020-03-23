import numpy as np
import matplotlib.pyplot as plt
import figpptx

# 円周率の略記
p = np.pi

# 0～2piまで0.1刻みの数値の配列を定義
x = np.arange(0, 2 * p, 0.1)

# グラフに描く関数
y = np.sin(x)

# FigureとAxesを作成
fig = plt.figure(figsize = (8, 6))
ax = fig.add_subplot(111)

# Axesのタイトル、グリッド、軸ラベル、軸範囲、目盛、目盛ラベルを設定
ax.set_title("$y=\sin x$", fontsize = 16)
ax.grid()
ax.set_xlabel("x", fontsize = 14)
ax.set_ylabel("y", fontsize = 14)
ax.set_xlim(0.0, 2 * p)
ax.set_ylim(-2.0, 2.0)
ax.set_xticks([0, p/2, p, 3*p/2, 2*p])
ax.set_xticklabels(["0", "$\pi/2$", "$\pi$", "$3\pi/2$", "$2\pi$"],
                   fontsize = 12)

# テキストボックスのプロパティを設定
text_dict = dict(boxstyle = "round", fc = "palegreen")

# 矢印のプロパティを設定
arrow_dict = dict(facecolor = "red", edgecolor = "red")

# 矢印とテキストを設定
ax.annotate("local maximun",
            xy = (p/2, 1), xytext = (2.5, 1.6),
            bbox = text_dict, 
            arrowprops = arrow_dict, size = 14)

ax.annotate("local minimun",
            bbox = text_dict,
            xy = (3*p/2, -1), xytext = (2.8, -1.4),
            arrowprops = arrow_dict, size = 14)

# Axesにグラフをプロット
ax.plot(x, y, color = "blue")
#fig.tight_layout()

figpptx.send(fig)
