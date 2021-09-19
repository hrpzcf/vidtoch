# Vidtoch

## 一个帮你将视频转为字符视频的模块。

------

### 用法：

```python
# coding: utf-8

from vidtoch import makeVideo

# 确保你的程序运行入口在 if __name__ == "__main__" 分支下
# 因为 makeVideo 函数使用了多进程，在 windows 上，如果不做以上要求
# 则可能造成你的程序的递归调用从而造成灾难性后果
if __name__ == "__main__":
    makeVideo(
        "源视频路径",
        "生成视频保存路径", # 包括文件名，建议用 .avi 后缀
        acqRate: float = 0.2, # 采集率，0 < acqRate <= 1，值越大越清晰生成越慢
    )
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
