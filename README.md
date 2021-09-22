# Vidtoch

## 一个帮你将视频转为字符视频的模块。

------

### 用法1：vidtoch.makeVideo 函数

```python
# coding: utf-8

from vidtoch import *

# 确保你的程序运行入口在 if __name__ == "__main__" 分支下
# 因为 makeVideo 函数使用了多进程，在 windows 上，如果不做以上要求
# 则可能造成你的程序的递归调用从而造成灾难性后果
if __name__ == "__main__":
    # 用法1：
    # 生成后缀名仅支持 avi
    makeVideo(
        "原视频路径",
        "生成视频保存路径", # 包括文件名，用 .avi 后缀
        acqRate: float = 0.2, # 采集率，0 < acqRate <= 1，值越大越清晰生成越慢
        overwrite: bool = False, # 如果保存目录已有同名文件，此参数控制是否覆盖同名文件
    )
    # 此函数有不少缺点，生成的视频没有声音，码率无法控制导致文件体积非常大，只能用avi后缀
```

### 用法：vidtoch.vTools 类

```python
# coding: utf-8

from vidtoch import *

# 写法1
# 不要忘记将你的程序唯一运行入口置于 if __name__ == "__main__" 分支下
if __name__ == "__main__":
    vt = vTools()
    vt.open(r"C:\Users\hrpzcf\Desktop\1.mp4") # 路径自行替换，保存路径也一样
    if vt.isOpened():
        vt.save(r"C:\Users\hrpzcf\Desktop\f.mp4", 0.2, overwrite=1)
    vt.close()  # 使用完毕不要忘记调用close方法关闭vTools实例

# 写法2
# 不要忘记将你的程序唯一运行入口置于 if __name__ == "__main__" 分支下
if __name__ == "__main__":
    with vTools() as vt:
        vt.open(r"C:\Users\hrpzcf\Desktop\1.mp4")
        if vt.isOpened():
            vt.save(r"C:\Users\hrpzcf\Desktop\f.mp4", 0.2, overwrite=1)
    # with 代码块结束后会自动调用close方法关闭vTools实例

# vTools 类初始化参数详解
# vTools(
#     chars: str = None,  # 生成的视频要使用的字符，字符串中字符数应大于2个，字符串无需按等效灰度手动排序，可忽略
#     ffmpeg: str = None,   # ffmpeg可执行文件的路径，为 None 则在当前目录或环境变量中查找，找不到则生成的文件无声音，可忽略
#     procNum: int = None   # 转换成字符视频时使用的进程数，默认是 cpu数*2，可忽略
#     )

# 例：
if __name__ == "__main__":
    with vTools("@^&*.=+-#`", r"d:\ffmpeg\bin", 4) as vt:
    # with vTools("@^&*.=+-#`") as vt:
    # with vTools(ffmpeg=r"d:\ffmpeg\bin", procNum=4) as vt:
    # with vTools("@^&*.=+-#`", procNum=4) as vt:
    # vt = vTools(ffmpeg=r"d:\ffmpeg\bin")
        ...


# save 方法参数详解
# save(
#     savePath: str,    # 生成的视频的保存路径，包括文件名，后缀名不限
#     acqRate: float = 0.2, # 对原视频的采集率，0 < acqRate <= 1，值越大视频越清晰字体越小，可忽略
#     bitRate: int = None,  # 生成的视频的码率，默认单位为k，例如值为'1500'则代表生成的视频码率限制在1500k，可忽略
#     overwrite: bool = False,  #如果保存目录已有同名文件，此参数控制是否覆盖同名文件，可忽略
#     )

```

### 实例：
```python
# coding: utf-8

from vidtoch import makeVideo

# 确保你的程序运行入口在 if __name__ == "__main__" 分支下
# 因为 makeVideo 函数使用了多进程，在 windows 上，如果不做以上要求
# 则可能造成你的程序的递归调用从而造成灾难性后果
if __name__ == "__main__":
    # 尽量将 acqRate 设置的小些，否则生成视频会非常慢
    makeVideo("1.mp4", "new.avi", acqRate=0.1)  # 图片 1.mp4 已在当前目录中
```
