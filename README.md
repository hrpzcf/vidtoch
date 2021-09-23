# Vidtoch

## 一个帮你将视频转为字符视频的模块。

------

### 用法 1：使用 vidtoch.makeVideo 函数生成无声的字符视频

```python
# coding: utf-8

from vidtoch import *

# 确保你的程序运行入口在 if __name__ == "__main__" 分支下
# 因为 makeVideo 函数使用了多进程，在 windows 上，如果不做以上要求
# 则可能造成你的程序的递归调用从而造成灾难性后果
if __name__ == "__main__":
    # 用法1：
    # 生成的视频仅支持使用 avi 后缀名
    makeVideo(
        "原视频路径",
        "生成视频保存路径", # 包括文件名，用 .avi 后缀
        acqRate: float = 0.2, # 采集率，0 < acqRate <= 1，值越大越清晰生成越慢
        overwrite: bool = False, # 如果保存目录已有同名文件，此参数控制是否覆盖同名文件
    )
    # 此函数有不少缺点，生成的视频没有声音，码率无法控制导致文件体积非常大，只能用avi后缀

### 实例：
# coding: utf-8

from vidtoch import *

# 确保你的程序运行入口在 if __name__ == "__main__" 分支下
# 因为 makeVideo 函数使用了多进程，在 windows 上，如果不做以上要求
# 则可能造成你的程序的递归调用从而造成灾难性后果
if __name__ == "__main__":
    # 尽量将 acqRate 设置的小些，否则生成视频会非常慢
    makeVideo("1.mp4", "new.avi", acqRate=0.1)  # 视频文件 1.mp4 已在当前工作目录中
```

### 用法 2：使用 vidtoch.vTools 类生成有声音的字符视频，依赖[FFMPEG][1]

------

#### 点击 [ffmpeg][1] 下载，解压，将bin目录中的ffmpeg.exe放到当前工作目录，或放到任意目录并将bin文件夹路径添加到环境变量，或放到任意目录，在 vTools 类中指定路径，如 vt = vTools(ffmpeg=r"d:\ffmpeg\bin\ffmpeg.exe")

```python
# coding: utf-8

from vidtoch import *

# vTools 类初始化参数详解
# vTools(
#     chars: str = None,  # 生成的视频要使用的字符，字符串中字符数应大于2个，字符串无需按等效灰度手动排序，可忽略
#     ffmpeg: str = None,   # ffmpeg可执行文件的路径，为 None 则在当前目录或环境变量中查找，找不到则生成的文件无声音，可忽略
#     procNum: int = None   # 转换成字符视频时使用的进程数，默认是 cpu数*2，可忽略
#     )

# 例：
# if __name__ == "__main__":
    # with vTools("@^&*.=+-#`", r"d:\ffmpeg\bin\ffmpeg.exe", 4) as vt:
    # with vTools("@^&*.=+-#`") as vt:
    # with vTools(ffmpeg=r"d:\ffmpeg\bin\ffmpeg.exe", procNum=4) as vt:
    # with vTools("@^&*.=+-#`", procNum=4) as vt:
    # vt = vTools(ffmpeg=r"d:\ffmpeg\bin\ffmpeg.exe")
        ...

# save 方法参数详解
# save(
#     savePath: str,    # 生成的视频的保存路径，包括文件名，后缀名不限
#     acqRate: float = 0.2, # 对原视频的采集率，0 < acqRate <= 1，值越大视频越清晰字体越小，可忽略
#     bitRate: int = None,  # 生成的视频的码率，默认单位为k，例如值为'1500'则代表生成的视频码率限制在1500k，可忽略
#     overwrite: bool = False,  # 如果保存目录已有同名文件，此参数控制是否覆盖同名文件，可忽略
#     )

def main():
    # 写法 1 实例
    # 不要忘记将你的程序唯一运行入口置于 if __name__ == "__main__" 分支下
    # vt = vTools()
    # vt.open(r"C:\Users\hrpzcf\Desktop\1.mp4")   # 路径自行替换
    # if vt.isOpened():
    #     vt.save(r"C:\Users\hrpzcf\Desktop\f.mp4", 0.2, overwrite=1)   # # 保存路径自行替换
    # vt.close()  # 使用完毕不要忘记调用close方法关闭vTools实例

    # 写法 2 实例
    # 不要忘记将你的程序唯一运行入口置于 if __name__ == "__main__" 分支下
    with vTools() as vt:
        vt.open(r"C:\Users\hrpzcf\Desktop\1.mp4")   # 路径自行替换
        if vt.isOpened():
            vt.save(r"C:\Users\hrpzcf\Desktop\f.mp4", 0.2, overwrite=1) # 保存路径自行替换
    # with 代码块结束后会自动调用close方法关闭vTools实例

if __name__ == "__main__":
    main()

```

[1]: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z
