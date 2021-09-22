# coding: utf-8

################################################################################
# MIT License

# Copyright (c) 2021 hrp/hrpzcf <hrpzcf@foxmail.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
################################################################################
# Formatted with black 20.8b1.
################################################################################

import os
import shutil
import tempfile
from multiprocessing import Pool
from subprocess import STARTUPINFO, run
from time import localtime, strftime

from cv2 import (
    CAP_PROP_FPS,
    CAP_PROP_FRAME_COUNT,
    CAP_PROP_FRAME_HEIGHT,
    CAP_PROP_FRAME_WIDTH,
    CAP_PROP_POS_FRAMES,
    IMWRITE_JPEG_QUALITY,
    VIDEOWRITER_PROP_QUALITY,
)
from cv2 import VideoCapture as vcapt
from cv2 import VideoWriter, VideoWriter_fourcc, imread, imwrite
from imgtoch import makeImage

NONETYPE = type(None)


def makeVideo(
    videoPath: str,
    savePath: str,
    acqRate: float = 0.2,
    chars=None,
    overwrite: bool = False,
):
    """
    ### 将视频转换为字符视频

    注意事项：

    因 makeVideo 函数使用了多进程工作方式，且因 windows 平台新进程创建机制问题

    请确保你的程序运行入口唯一且处于 __name__ == '__main__' 分支下，否则会造成递归调用而发生不可预知的后果

    ```
    参数 videoPath：str，源视频文件路径
    参数 savePath：str，生成的视频文件保存路径，包括文件名且需为 .avi 后缀
    参数 acqRate: float，对原视频的采集率，0 < acqRate <= 1，值越大视频越清晰字体越小，可忽略
    参数 chars: str，视频中使用的字符，无需排序，但为了效果建议使用多些字符
    且使字符的等效灰度值分布尽量均匀，单字符的等效灰度值可以使用 imgtoch 模块的 grayscaleOf 函数查询

    参数 overwrite: bool，如果保存目录已有同名文件，此参数控制是否覆盖同名文件，可忽略
    ```
    """
    if not isinstance(savePath, str):
        raise TypeError("保存路径参数值数据类型必须为字符串。")
    if os.path.splitext(savePath)[1] != ".avi":
        raise ValueError("文件保存路径中文件名需为'.avi'后缀。")
    if os.path.exists(savePath):
        if not overwrite:
            print("已有同名文件或目录且参数overwrite值为'False'，生成中断。")
            return False
        else:
            _clearObstacle(savePath)
    try:
        videoCapt = vcapt(videoPath)
    except Exception:
        print("参数videoPath的值数据类型不正确，仅接受字符串。")
    if not videoCapt.isOpened():
        return print("源视频文件无法打开，请检查路径是否正确或其他问题。")
    fps = videoCapt.get(CAP_PROP_FPS)
    width = int(videoCapt.get(CAP_PROP_FRAME_WIDTH))
    height = int(videoCapt.get(CAP_PROP_FRAME_HEIGHT))
    imgTemp, charImgTemp = tempfile.mkdtemp(), tempfile.mkdtemp()
    baseName = os.path.basename(videoPath)
    prefix = os.path.splitext(baseName)[0]
    frameNum, imgNameList = 0, list()
    print("开始分解视频...")
    while True:
        boolResult, frame = videoCapt.read()
        if not boolResult:
            break
        name = f"{prefix}_{frameNum}.jpg"
        imgNameList.append(name)
        imwrite(os.path.join(imgTemp, name), frame, [IMWRITE_JPEG_QUALITY, 80])
        frameNum += 1
    videoCapt.release()
    makeImageProcessPool = Pool(os.cpu_count() * 2)
    kwdargs = dict(scale=acqRate, keepSize=1, chars=chars)
    print("开始转换图像...")
    for imgName in imgNameList:
        imgPath = os.path.join(imgTemp, imgName)
        imgSave = os.path.join(charImgTemp, imgName)
        makeImageProcessPool.apply_async(makeImage, (imgPath, imgSave), kwdargs)
    makeImageProcessPool.close()
    makeImageProcessPool.join()  # 等待进程全部结束
    shutil.rmtree(imgTemp)
    fourcc = VideoWriter_fourcc(*"MP42")
    try:
        videoWrt = VideoWriter(savePath, fourcc, fps, (width, height), True)
    except Exception:
        print("视频写入失败，检查保存位置是否有写入权限。")
        return False
    videoWrt.set(VIDEOWRITER_PROP_QUALITY, 50)
    print("开始合成视频...")
    for imgName in imgNameList:
        videoWrt.write(imread(os.path.join(charImgTemp, imgName)))
    videoWrt.release()
    shutil.rmtree(charImgTemp)
    return True


def _clearObstacle(path):
    """检查路径是否存在并尝试删除文件或非空文件夹"""
    if os.path.exists(path):
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception:
                print("已存在同名文件且无法删除，生成中断。")
                return False
        else:
            try:
                os.rmdir(path)
            except Exception:
                print("已存在同名非空文件夹无法删除，生成中断。")
                return False
    return True


class FFCmdUtils:
    STARTUP = STARTUPINFO(dwFlags=1, wShowWindow=0)

    def __init__(self, ffmpeg: str = None):
        if ffmpeg is None:
            self.__fm = self.detExecutable()
        elif isinstance(ffmpeg, str):
            ffmpeg = os.path.abspath(ffmpeg)
            if os.path.isfile(ffmpeg) and os.access(ffmpeg, 1):
                self.__fm = ffmpeg
            else:
                self.__fm = self.detExecutable()
                print("参数 ffmpegPath 的值是无效路径，使用自动检测值。")
        else:
            self.__fm = self.detExecutable()
            print("参数 ffmpegPath 值的数据类型不正确，使用自动检测值。")
        self.__cmd = self.__fm, "-nostats", "-loglevel", "quiet"

    @staticmethod
    def detExecutable():
        """
        ### 探测 ffmpeg 可执行文件位置

        首先会在当前目录寻找，找不到则在系统环境变量中寻找，再找不到则返回 None。
        """
        osName = os.name == "nt"
        ffexecutable = ("ffmpeg", "ffmpeg.exe")[osName]
        cuiDir = os.path.abspath(os.getcwd())
        try:
            fileList = os.listdir(cuiDir)
            execPath = os.path.join(cuiDir, ffexecutable)
            if (
                ffexecutable in fileList
                and os.path.isfile(execPath)
                and os.access(execPath, 1)
            ):
                return execPath
        except Exception:
            pass
        separator = (":", ";")[osName]
        pathsInPATH = os.getenv("PATH", "").split(separator)
        for path in pathsInPATH:
            execPath = os.path.join(path, ffexecutable)
            if os.path.isfile(execPath) and os.access(execPath, 1):
                return execPath
        print("找不到任何ffmpeg可执行文件。")
        return None

    def isReady(self) -> bool:
        """返回 FFCmdUtils 是否可用"""
        return self.__fm is not None

    @staticmethod
    def executeCmd(cmd):
        try:
            result = run(cmd, startupinfo=FFCmdUtils.STARTUP)
        except Exception:
            return False
        return not result.returncode

    def mux(
        self,
        videoPath: str,
        audioPath: str,
        savePath: str = None,
        overwrite: bool = False,
    ):
        """
        ### 封装音频及视频

        ```
        参数 videoPath: str，要封装的视频文件路径
        参数 audioPath: str，要封装的音频文件路径
        参数 savePath: str，封装后的视频文件保存路径，包括文件名，忽略则保存到源视频目录，并以'[时间]源视频文件名.原后缀名'作文件名
        参数 overwrite: bool，如果保存目录已有同名文件，此参数控制是否覆盖同名文件，可忽略
        ```
        """
        if not self.isReady():
            return False
        if not isinstance(videoPath, str):
            raise TypeError("参数videoPath的值数据类型必须是字符串。")
        if not isinstance(audioPath, str):
            raise TypeError("参数audioPath的值数据类型必须是字符串。")
        dirPath, basename = os.path.split(videoPath)
        if savePath is None:
            prefix = strftime("[%Y-%m-%d_%H-%M-%S]", localtime())
            savePath = os.path.join(dirPath, f"{prefix}{basename}")
        elif not isinstance(savePath, str):
            raise TypeError("参数savePath的值数据类型必须是字符串。")
        command = [
            *self.__cmd,
            "-i",
            audioPath,
            "-i",
            videoPath,
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            savePath,
        ]
        if overwrite:
            command.append("-y")
        else:
            command.append("-n")
        return FFCmdUtils.executeCmd(command)

    def demux(
        self,
        videoPath: str,
        saveDir=None,
        option: str = "audio",
        overwrite: bool = False,
    ):
        """
        ### 拆分音频及视频

        ```
        参数 videoPath: str，要拆分的视频的文件路径
        参数 option: str，可用值：'audio'，仅拆分音频；'video'，仅拆分视频；'both'，拆分音频和视频
        参数 saveDir: str，拆分后文件的保存目录
        参数 overwrite: bool，如果保存目录已有同名文件，此参数控制是否覆盖同名文件，可忽略
        ```
        """
        if not self.isReady():
            return False
        if not isinstance(videoPath, str):
            raise TypeError("参数videoPath的值数据类型必须是字符串。")
        OPTS = "audio", "video", "both"
        if option not in OPTS:
            raise ValueError(f"参数 option 的值无效，可用值为：{OPTS}。")
        dirPath, basename = os.path.split(videoPath)
        if saveDir is None:
            saveDir = dirPath
        elif not isinstance(saveDir, str):
            raise TypeError("参数savePath的值数据类型必须是字符串。")
        if not os.path.isdir(saveDir):
            raise ValueError("参数saveDir的值所指的目录不存在或无法访问。")
        prefix = strftime("[%Y-%m-%d_%H-%M-%S]", localtime())
        fileName = os.path.splitext(basename)[0]
        audioSavePath = os.path.join(saveDir, f"{prefix}{fileName}.aac")
        videoSavePath = os.path.join(saveDir, f"{prefix}{fileName}.mp4")
        command = [*self.__cmd, "-i", videoPath]
        if overwrite:
            command.append("-y")
        else:
            command.append("-n")
        if option == "both":
            command.extend(
                (
                    "-an",
                    "-c:v",
                    "copy",
                    videoSavePath,
                    "-vn",
                    "-c:a",
                    "copy",
                    audioSavePath,
                )
            )
        elif option == "audio":
            command.extend(("-vn", "-c:a", "copy", audioSavePath))
        elif option == "video":
            command.extend(("-an", "-c:v", "copy", videoSavePath))
        else:
            return False
        return FFCmdUtils.executeCmd(command)

    def convert(
        self,
        videoPath: str,
        savePath: str = None,
        fps: float = None,
        bitRate: int = None,
        codec: str = None,
        overwrite: bool = False,
    ):
        """
        ### 转换视频格式

        ```
        参数 videoPath: str，要转换的源视频路径
        参数 savePath: str，转换后的视频的保存路径，包括文件名，忽略则保存到源视频目录，并以'[时间]源视频文件名.mp4'作文件名
        参数 fps: int or float，转换后的视频的帧率，可忽略
        参数 bitRate: int，转换后的视频的码率，默认单位为k，例如此参数值为'1500'则代表转换后视频限制其码率在1500k左右，可忽略
        参数 codec: str，指定转换使用的编码器名，建议使用'h264'(要求ffmpeg是完整版，否则转换会出错)，可忽略
        参数 overwrite: bool，如果保存目录已有同名文件，此参数控制是否覆盖同名文件，可忽略
        ```
        """
        if not self.isReady():
            return False
        if not isinstance(videoPath, str):
            raise TypeError("参数videoPath的值数据类型必须是字符串。")
        dirPath, basename = os.path.split(videoPath)
        if savePath is None:
            prefix = strftime("[%Y-%m-%d_%H-%M-%S]", localtime())
            savePath = os.path.join(
                dirPath, f"{prefix}{os.path.splitext(basename)[0]}.mp4"
            )
        elif not isinstance(savePath, str):
            raise TypeError("参数savePath的值数据类型必须是字符串。")
        if not isinstance(fps, (int, (float, NONETYPE))):
            raise TypeError("参数fps的值数据类型必须是整型或者浮点型。")
        if not isinstance(bitRate, (int, NONETYPE)):
            raise TypeError("参数bitRate的值数据类型必须是整型。")
        if not isinstance(codec, (str, NONETYPE)):
            raise TypeError("参数codec的值数据类型必须是字符串类型。")
        command = [*self.__cmd, "-i", videoPath]
        if codec is not None:
            command.extend(("-c:v", f"{codec}"))
        if fps is not None:
            command.extend(("-r", f"{fps}"))
        if bitRate is not None:
            command.extend(("-b:v", f"{bitRate}k"))
        if overwrite:
            command.append("-y")
        else:
            command.append("-n")
        command.append(savePath)
        return FFCmdUtils.executeCmd(command)

    def combine(
        self,
        imageDir: str,
        savePath: str = None,
        fps: float = None,
        bitRate: int = None,
        codec: str = None,
        overwrite: bool = None,
    ):
        """
        ### 将图片封装为视频

        要求图片的分辨率要相同，后缀名要一样
        图片的命名要求是 'name_%d.ext'，例如 img_0.jpg, img_1.jpg ...

        ```
        参数 imageDir: str，存放图片的目录路径
        参数 savePath: str，生成的视频的保存路径，包括文件名，忽略则保存到图片目录，并以'vid_{时间}.mp4'作文件名
        参数 fps: int or float，转换后的视频的帧率，可忽略
        参数 bitRate: int，转换后的视频的码率，默认单位为k，例如此参数值为'1500'则代表转换后视频限制其码率在1500k左右，可忽略
        参数 codec: str，指定转换使用的编码器名，建议使用'h264'(要求ffmpeg是完整版，否则转换会出错)，可忽略
        参数 overwrite: bool，如果保存目录已有同名文件，此参数控制是否覆盖同名文件，可忽略
        ```
        """
        if not self.isReady():
            return False
        if not isinstance(imageDir, str):
            raise TypeError("参数imageDir的值数据类型必须是字符串。")
        if not isinstance(bitRate, (int, NONETYPE)):
            raise TypeError("参数bitRate的值数据类型必须是整型。")
        if not isinstance(fps, (int, (float, NONETYPE))):
            raise TypeError("参数fps的值数据类型必须是整型或者浮点型。")
        if savePath is None:
            saveName = strftime("%Y-%m-%d_%H-%M-%S", localtime())
            savePath = os.path.join(imageDir, f"vid_{saveName}.mp4")
        elif not isinstance(savePath, str):
            raise TypeError("参数savePath的值数据类型必须是字符串。")
        try:
            imageNameList = os.listdir(imageDir)
        except Exception as err:
            print(f"图片目录读取失败：{err}。")
            return False
        if not imageNameList:
            return False
        fileName, ext = os.path.splitext(imageNameList[0])
        pathWithName = os.path.join(imageDir, fileName.rsplit("_", 1)[0])
        command = [*self.__cmd, "-i", f"{pathWithName}_%d{ext}"]
        if codec is not None:
            command.extend(("-c:v", codec))
        if fps is not None:
            command.extend(("-r", f"{fps}"))
        if bitRate is not None:
            command.extend(("-b:v", f"{bitRate}k"))
        if overwrite:
            command.extend(("-y", savePath))
        else:
            command.extend(("-n", savePath))
        return FFCmdUtils.executeCmd(command)


class vTools:
    def __init__(self, chars: str = None, ffmpeg: str = None, procNum: int = None):
        """
        ### vTools 类，包含 open, save, close, isOpened 四个公共方法

        请确保你的程序运行入口唯一且处于 __name__ == '__main__' 分支下，否则会造成递归调用而发生不可预知的后果

        ```
        参数 chars: str，生成的视频要使用的字符，字符串中字符数应大于2个，字符串无需按等效灰度手动排序，可忽略
        参数 ffmpeg: str，ffmpeg可执行文件的路径，为 None 则在当前目录或环境变量中查找，找不到则生成的文件无声音，可忽略
        参数 procNum: int，转换成字符视频时使用的进程数，默认是 cpu数*2，可忽略
        ```
        """
        if chars is None:
            chars = "HdRQA#PXCFJIv?!+^-:. "
        if not isinstance(chars, str):
            raise TypeError("参数chars的值必须是字符串类型。")
        if len(chars) < 2:
            raise ValueError("参数chars的值字符个数不能少于2个。")
        self.__charMap = chars
        if not isinstance(ffmpeg, (str, NONETYPE)):
            raise TypeError("参数ffmpeg的值必须是字符串类型。")
        if procNum is None:
            procNum = os.cpu_count() * 2
        if not isinstance(procNum, int):
            raise TypeError("参数procNum的值必须是整型数据。")
        if procNum > 32:
            raise ValueError("参数procNum的值过大，即进程数过多。")
        self.__ffutils = FFCmdUtils(ffmpeg)
        self.__procNum = procNum
        self.__vPath = None
        self.__vCapt = None
        self.__audioTmp = tempfile.mkdtemp()
        self.__videoTmp = tempfile.mkdtemp()
        self.__imgTmp = tempfile.mkdtemp()
        self.__gImgTmp = tempfile.mkdtemp()

    def __enter__(self):
        return self

    def __exit__(self, excType, excValue, excTB):
        self.close()

    def __del__(self):
        self.close()

    def open(self, videoPath: str):
        if not isinstance(videoPath, str):
            raise TypeError("参数videoPath的值数据类型必须是字符串。")
        if not os.path.isfile(videoPath):
            raise ValueError("参数videoPath的值所指的视频文件不存在。")
        try:
            self.__vCapt = vcapt(videoPath)
            self.__vPath = videoPath
        except Exception:
            print(f"参数videoPath的值数据类型不正确，仅接受字符串。")
        return self

    def save(
        self,
        savePath: str,
        acqRate: float = 0.2,
        bitRate: int = None,
        overwrite: bool = False,
    ):
        """
        ### 保存为字符视频

        ```
        参数 savePath：str，生成的视频的保存路径，包括文件名
        参数 acqRate: float，对原视频的采集率，0 < acqRate <= 1，值越大视频越清晰字体越小，可忽略
        参数 bitRate: int，生成的视频的码率，默认单位为k，例如值为'1500'则代表生成的视频码率限制在1500k，可忽略
        参数 overwrite: bool，如果保存目录已有同名文件，此参数控制是否覆盖同名文件，可忽略
        ```
        """
        if not isinstance(savePath, str):
            raise TypeError("参数savePath的值必须是字符串类型。")
        if not isinstance(acqRate, (int, float)):
            raise TypeError("参数acqRate的值必须是整型或浮点型。")
        if not (0 < acqRate <= 1):
            raise ValueError("参数acqRate的值必须大于0小于等于1。")
        if not isinstance(bitRate, (int, NONETYPE)):
            raise TypeError("参数bitRate的值必须是整型数据。")
        if self.__ffutils.isReady():
            return self.__GenByFFm(savePath, acqRate, bitRate, overwrite)
        else:
            return self.__GenByCV2(savePath, acqRate, overwrite)

    def close(self):
        self.__vPath = None
        if hasattr(self, "__vCapt") and isinstance(self.__vCapt, vcapt):
            self.__vCapt.release()
        try:
            if hasattr(self, "__audioTmp"):
                shutil.rmtree(self.__audioTmp)
            if hasattr(self, "__videoTmp"):
                shutil.rmtree(self.__videoTmp)
            if hasattr(self, "__imgTmp"):
                shutil.rmtree(self.__imgTmp)
            if hasattr(self, "__gImgTmp"):
                shutil.rmtree(self.__gImgTmp)
        except Exception as err:
            print(f"临时文件清除失败：{err}。")

    @staticmethod
    def __clearD(dirPath):
        try:
            fileNames = os.listdir(dirPath)
        except Exception:
            return False
        for fileN in fileNames:
            fullPath = os.path.join(dirPath, fileN)
            if os.path.isfile(fullPath):
                try:
                    os.remove(fullPath)
                except:
                    continue
            else:
                shutil.rmtree(fullPath)
        return True

    def isOpened(self) -> bool:
        return (
            self.__vPath and isinstance(self.__vCapt, vcapt) and self.__vCapt.isOpened()
        )

    def __mkGrayImgs(self, acqRate: float = 0.2):
        """拆分音频文件及生成字符图片"""
        if not self.isOpened():
            return print("视频文件没有被打开，请检查路径是否正确或其他问题。")
        vTools.__clearD(self.__imgTmp)
        vTools.__clearD(self.__audioTmp)
        if self.__ffutils.isReady():
            self.__ffutils.demux(self.__vPath, self.__audioTmp)
        prefix = os.path.splitext(os.path.basename(self.__vPath))[0]
        frameNum, imgNameList = 0, list()
        print("开始分解视频...")
        while True:
            boolResult, frame = self.__vCapt.read()
            if not boolResult:
                break
            name = f"{prefix}_{frameNum}.jpg"
            imgNameList.append(name)
            imwrite(
                os.path.join(self.__imgTmp, name), frame, [IMWRITE_JPEG_QUALITY, 80]
            )
            frameNum += 1
        self.__vCapt.set(CAP_PROP_POS_FRAMES, 0)
        makeImageProcessPool = Pool(self.__procNum)
        kwdargs = dict(scale=acqRate, keepSize=1, chars=self.__charMap)
        print("开始转换图像...")
        for imgName in imgNameList:
            imgPath = os.path.join(self.__imgTmp, imgName)
            imgSave = os.path.join(self.__gImgTmp, imgName)
            makeImageProcessPool.apply_async(makeImage, (imgPath, imgSave), kwdargs)
        makeImageProcessPool.close()
        makeImageProcessPool.join()  # 等待进程全部结束
        return (
            imgNameList,
            int(self.__vCapt.get(CAP_PROP_FRAME_WIDTH)),
            int(self.__vCapt.get(CAP_PROP_FRAME_HEIGHT)),
            self.__vCapt.get(CAP_PROP_FPS),
        )

    def __GenByFFm(self, savePath: str, acqRate: float, bitRate: int, overwrite):
        if os.path.exists(savePath):
            if not overwrite:
                print("已有同名文件或目录且参数overwrite值为'False'，生成中断。")
                return False
            else:
                _clearObstacle(savePath)
        vTools.__clearD(self.__gImgTmp)
        vTools.__clearD(self.__videoTmp)
        *_, fps = self.__mkGrayImgs(acqRate)
        if bitRate is None:
            try:
                fileSize = os.path.getsize(self.__vPath)
                bitRate = int(
                    (fileSize * 8 / 1024)
                    / (self.__vCapt.get(CAP_PROP_FRAME_COUNT) / fps)
                )
            except Exception:
                bitRate = None
        ext = os.path.splitext(savePath)[1]
        vidTmpFileName = f"{strftime('%Y-%m-%d_%H-%M-%S', localtime())}{ext}"
        tmpFullPath = os.path.join(self.__videoTmp, vidTmpFileName)
        print("开始使用ffmpeg合成...")
        if not self.__ffutils.combine(
            self.__gImgTmp, tmpFullPath, fps, bitRate, "h264", overwrite
        ):
            return False
        try:
            audio = os.listdir(self.__audioTmp)
        except Exception:
            audio = None
        if audio:
            audioFullPath = os.path.join(self.__audioTmp, audio[0])
            self.__ffutils.mux(tmpFullPath, audioFullPath, savePath)
        else:
            print("音频缓存文件读取失败，无法添加音频。")
            shutil.move(tmpFullPath, savePath)

    def __GenByCV2(self, savePath: str, acqRate: float, overwrite: bool):
        if os.path.exists(savePath):
            if not overwrite:
                print("已有同名文件或目录且参数overwrite值为'False'，生成中断。")
                return False
            else:
                _clearObstacle(savePath)
        vTools.__clearD(self.__gImgTmp)
        imgNameList, width, height, fps = self.__mkGrayImgs(acqRate)
        fourcc = VideoWriter_fourcc(*"MP42")
        try:
            videoWrt = VideoWriter(savePath, fourcc, fps, (width, height), True)
        except Exception:
            print("视频写入失败，检查保存位置是否有写入权限。")
            return False
        print("开始使用OpenCV合成(无音频)...")
        for imgName in imgNameList:
            videoWrt.write(imread(os.path.join(self.__gImgTmp, imgName)))
        videoWrt.release()
        return True
