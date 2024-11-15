
import pyaudio
import wave
import os
import pywintypes
from wxauto import *
import psutil
import re
import subprocess
from Dodo_config import *

cwd = os.getcwd()
p = pyaudio.PyAudio()
recording = False
audio_frames = []

try:
    wx = WeChat()
    wx.GetSessionList()
    wechat_useable = True
except pywintypes.error:
    print("未登录微信。部分功能将不可用。")
    wechat_useable = False

def list():
    return wx.GetAllFriends()

def send_msg(msg, who):
    wx.SendMsg(msg, who)

def get_msg():
    msgs = wx.Ge

def play_audio(file_path):
    """播放音频文件"""
    try:
        wf = wave.open(file_path, 'rb')
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)

        stream.stop_stream()
        stream.close()

    except Exception as e:
        print(f"播放音频文件 {file_path} 出错: {e}")

def extract_code(output):
    """提取代码块中的代码"""
    match = re.search(r"```python(.*?)```", output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def remove_extra_newlines(text):
    """
    去掉字符串中多余的换行符，只保留一个换行符。
    """
    return re.sub(r"\n+", "\n", text).strip()

def is_code_response(output):
    """判断回复是否包含代码"""
    return output.startswith('cmd /c') or output.startswith('```python') or output.startswith('[SFBYNAME]') or output.startswith('[SFBYKIND]') or output.startswith('[SFBYKEY]') or output.startswith('[WXGET]') or output.startswith('[WXSEND]') or output.startswith('[WXLIST]')

def check_process(process_name):
    for process in psutil.process_iter(['name']):
        if process.info['name'] == process_name:
            return True
    return False

def start_everything():
    # 启动 Everything.exe
    try:
        subprocess.Popen(cwd+'\\binaries\\Everything.exe', shell=True)
    except FileNotFoundError:
        print('INIT: 未安装 Everything，请前往安装')
        exit()

def remove_extension(filename):
    if '.' in filename:
        return filename.split('.')[0]
    else:
        return filename

def search_file_by_name(file_name):
    search_result = str(os.popen(cwd+'\\binaries\\search_everything.exe wfn:'+file_name+' 2>&1').readlines())
    if len(search_result) > 0:
        return search_result
    else:
        return 'No result found'

def search_file_by_kind(file_kind, keyword):
    search_result = []
    file_kinds = ['audio','zip','doc','exe','pic','video']
    audio = ['mp3','wav','aac','flac','wma','ogg']
    zipname = ['zip','rar','7z','iso']
    doc = ['doc','docx','ppt','pptx','xls','xlsx','pdf']
    exe = ['exe','msi','bat','cmd']
    pic = ['jpg','jpeg','png','gif','bmp','tiff']
    video = ['mp4','avi','mov','wmv','flv','mkv']
    i = 0
    keyword = remove_extension(keyword)
    if file_kind == 'audio':
        for name in audio:
            search_result.append('extension: .'+name+', result: '+str(os.popen(cwd+'\\binaries\\search_everything.exe '+keyword+'.'+name+' 2>&1').readlines()))
    elif file_kind == 'zip':
        for name in zipname:
            search_result.append('extension: .'+name+', result: '+str(os.popen(cwd+'\\binaries\\search_everything.exe '+keyword+'.'+name+' 2>&1').readlines()))
    elif file_kind == 'doc':
        for name in doc:
            search_result.append('extension: .'+name+', result: '+str(os.popen(cwd+'\\binaries\\search_everything.exe '+keyword+'.'+name+' 2>&1').readlines()))
    elif file_kind == 'exe':
        for name in exe:
            search_result.append('extension: .'+name+', result: '+str(os.popen(cwd+'\\binaries\\search_everything.exe '+keyword+'.'+name+' 2>&1').readlines()))
    elif file_kind == 'pic':
        for name in pic:
            search_result.append('extension: .'+name+', result: '+str(os.popen(cwd+'\\binaries\\search_everything.exe '+keyword+'.'+name+' 2>&1').readlines()))
    elif file_kind == 'video':
        for name in video:
            search_result.append('extension: .'+name+', result: '+str(os.popen(cwd+'\\binaries\\search_everything.exe '+keyword+'.'+name+' 2>&1').readlines()))
    else:
        return 'Invalid file kind, please choose one: '+str(file_kinds)
    if len(search_result) > 0:
        return str(search_result)
    else:
        return 'No result found'
    
def search_file_by_keyword(keyword):
    search_result = str(os.popen(cwd+'\\binaries\\search_everything.exe '+keyword+' 2>&1').readlines())
    if len(search_result) > 0:
        return search_result
    else:
        return 'No result found'