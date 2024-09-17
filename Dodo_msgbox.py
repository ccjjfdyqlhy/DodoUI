import customtkinter
import time
import pywinstyles
import sys
import tkinter as tk
import wave
import pyaudio
import threading

# 设置 CustomTkinter 主题
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# 全局变量，用于跟踪当前显示的句子索引和窗口列表
current_index = 0
window_list = []

# 初始化 PyAudio
p = pyaudio.PyAudio()


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


def create_styled_window(title="Styled Window", content="This is the window content.", audio_file=None):
    """
    创建一个风格化的窗口，根据传入的参数显示内容，并在音频播放完成后销毁。
    将 [[...]] 标识符框起来的部分文本放大显示。
    添加一个方形小按钮，按下后停止定时销毁，并将按钮文本改为 "Pinned" 并禁用按钮。
    窗口大小会根据内容自动调整。
    添加 "Proceed" 按钮，用于显示下一条句子并播放对应的音频。

    Args:
        title (str): 窗口标题。
        content (str): 窗口显示的内容。
        audio_file (str): 对应的音频文件路径。
    """

    global current_index

    root = customtkinter.CTk()
    root.title(title)

    # 应用透明样式
    pywinstyles.apply_style(root, "acrylic")

    #  分割文本，提取需要放大的部分
    parts = content.split("[[")
    if len(parts) > 1:
        normal_text = parts[0]
        highlighted_parts = []
        for part in parts[1:]:
            highlighted_text, remaining_text = part.split("]]", 1)
            highlighted_parts.append(highlighted_text)
            highlighted_text = highlighted_parts[0]
            normal_text += remaining_text
    else:
        normal_text = content
        highlighted_text = ""

    # 创建标签显示普通文本
    content_label = customtkinter.CTkLabel(root, text=normal_text,
                                           text_color="white", font=("Microsoft YaHei", 18),
                                           wraplength=480)  # 自动换行

    highlighted_label = customtkinter.CTkLabel(root, text=highlighted_text,
                                               text_color="lightblue", font=("Microsoft YaHei", 30, "bold"))

    if highlighted_text != '':
        content_label.place(x=10, y=80)
        highlighted_label.place(x=20, y=20)
    else:
        content_label.place(x=10, y=10)

    # 获取标签的所需大小
    content_label.update_idletasks()  # 确保标签已计算大小
    label_width = content_label.winfo_reqwidth()
    label_height = content_label.winfo_reqheight()

    # 计算窗口大小
    window_width = min(label_width + 40, 500)  # 最大宽度为 500
    window_height = label_height + 100 if highlighted_text != '' else label_height + 60

    # 设置窗口大小
    root.geometry(f"{window_width}x{window_height}")

    # 获取音频时长（如果存在）
    audio_duration = 0
    if audio_file:
        try:
            with wave.open(audio_file, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                audio_duration = frames / float(rate)
        except Exception as e:
            print(f"获取音频文件 {audio_file} 时长出错: {e}")

    # 定时销毁窗口的函数，并在销毁后显示下一条句子
    def destroy_window():
        root.destroy()
        show_next_sentence()  # 在销毁后显示下一条句子并播放音频

    def cancel_destroy():
        root.after_cancel(destroy_timer)
        cancel_button.configure(text="已固定", state="disabled")
        proceed_button.place(x=window_width - 140, y=window_height - 45)  # 显示 "Proceed" 按钮

    # 创建 "Proceed" 按钮，用于显示下一条句子并播放音频
    def show_next_sentence():
        global current_index
        current_index += 1
        if current_index < len(contents):
            create_styled_window(title='Reply ' + str(current_index + 1) + '/' + str(len(contents)),
                                 content=contents[current_index],
                                 audio_file=audio_files[current_index] if current_index < len(audio_files) else None)

    # 根据音频时长设置销毁时间
    destroy_time = audio_duration + 1 if audio_file else 3  # 音频播放完成后等待 3 秒

    destroy_timer = root.after(int(destroy_time * 1000), destroy_window)

    cancel_button = customtkinter.CTkButton(root, text="固定", command=cancel_destroy,
                                            width=40, height=25, corner_radius=5)  # 设置按钮大小和圆角
    cancel_button.place(x=window_width - 60, y=window_height - 45)  # 将按钮放置在右下角

    proceed_button = customtkinter.CTkButton(root, text="切下条", command=show_next_sentence,
                                             width=60, height=25, corner_radius=5)

    # 在新线程中播放音频（如果存在）
    if audio_file:
        threading.Thread(target=play_audio, args=(audio_file,)).start()

    # 将窗口添加到窗口列表
    window_list.append(root)

    root.mainloop()


if __name__ == "__main__":
    src_file = sys.argv[1]
    audio_files = sys.argv[2:]  # 获取音频文件列表

    with open(src_file, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    contents = content.split('\n')

    create_styled_window(title='响应 ' + str(current_index + 1) + '/' + str(len(contents)),
                         content=contents[current_index],
                         audio_file=audio_files[current_index] if current_index < len(audio_files) else None)

    # 终止 PyAudio
    p.terminate()