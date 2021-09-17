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

import cv2
from imgtoch import makeImage


def makeVideo(videoPath: str, savePath: str, acqRate: float = 0.2):
    """
    ### 将视频转换为字符视频

    参数 videoPath：str，源视频路径

    参数 savePath：str，生成的视频保存路径，包括文件名且需为 .avi 后缀

    参数 acqRate：float，0 < acqRate <= 1，越高越清晰，生成也越慢
    """
    if not isinstance(savePath, str):
        raise TypeError("保存路径参数值数据类型必须为字符串。")
    if os.path.splitext(savePath)[1] != ".avi":
        raise ValueError("文件保存路径中文件名需为'.avi'后缀。")
    videoCapt = cv2.VideoCapture(videoPath)
    if not videoCapt.isOpened():
        return print("源视频文件无法打开，请检查路径是否正确或其他问题。")
    width = int(videoCapt.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(videoCapt.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = videoCapt.get(cv2.CAP_PROP_FPS)
    imgTemp = tempfile.mkdtemp()
    charTemp = tempfile.mkdtemp()
    baseName = os.path.basename(videoPath)
    prefix = os.path.splitext(baseName)[0]
    imgNameList = list()
    frameNum = 0
    while True:
        boolResult, frame = videoCapt.read()
        if not boolResult:
            break
        name = f"{prefix}_{frameNum}.jpg"
        print(f"分解：{name}")
        imgNameList.append(name)
        cv2.imwrite(os.path.join(imgTemp, name), frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
        frameNum += 1
    videoCapt.release()
    for imgName in imgNameList:
        imgPath = os.path.join(imgTemp, imgName)
        imgSave = os.path.join(charTemp, imgName)
        print(f"转换：{imgName}")
        makeImage(imgPath, imgSave, scale=acqRate, keepSize=1)
    shutil.rmtree(imgTemp)
    fourcc = cv2.VideoWriter_fourcc(*"MP42")
    videoWrt = cv2.VideoWriter(savePath, fourcc, fps, (width, height), True)
    for imgName in imgNameList:
        print(f"生成：{imgName}")
        videoWrt.write(cv2.imread(os.path.join(charTemp, imgName)))
    videoWrt.release()
    shutil.rmtree(charTemp)
