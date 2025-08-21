import math
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import OrderedDict


def read_config_file(contents):
    """
    Reads a config file with 'key=value' pairs, where values can contain
    line breaks. Returns an OrderedDict to preserve key order.
    """
    pattern = re.compile(r'^(?P<key>[^=\s]+)=(?P<value>.*?)(?=\n[^=\s]+=|\Z)', re.S | re.M)

    data = OrderedDict()

    for match in pattern.finditer(contents):
        key = match.group('key').strip()
        value = match.group('value').strip()
        data[key] = value

    return data


def open_maidata_dialog():
    """Opens a file dialog and returns the selected file path."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Choose a file",
        filetypes=(("Text files", "maidata.txt"),)
    )
    root.destroy()
    return file_path


def pop_alert(title, message):
    """
    Displays a pop-up alert box with a title and a message.
    """
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()


def maidata_formatting(contents : str) -> str:
    """
    Formatting maidata text and returns it.
    :param contents:Simai chart data:
    :return: Formatted simai chart data:
    """
    content_data = read_config_file(contents)
    new_contents = ""
    for key, content in content_data.items():
        if not key.startswith("&inote"):
            new_contents += f"{key}={content}\n"
            continue

        bpm_blocks = re.split(r'(\([^)]*\))', content)
        modified_content = ""
        for i, block in enumerate(bpm_blocks):
            if i % 2 == 1 or i == 0:
                modified_content += block
                continue
            block = block.replace("\n", "")
            music_data = re.split(r'(\{[^}]*})', block)
            new_block = ""
            denominator = math.lcm(*(int(music_data[index][1:-1]) for index in range(1, len(music_data), 2)))

            for index in range(2, len(music_data), 2):
                multiplier = denominator // int(music_data[index - 1][1:-1])
                phrase = music_data[index].replace(',', ',' * multiplier)
                new_block += phrase

            new_data = new_block.split(",")[:-1]

            res = ""
            for index in range(0, len(new_data), denominator):
                if index + denominator < len(new_data):
                    data_window = new_data[index:index + denominator]
                else:
                    data_window = new_data[index:]

                res += reassemble_beats(data_window, denominator)

            modified_content += res

        new_contents += f"{key}={modified_content}\n"

    return new_contents


def reassemble_beats(data_window, denominator):
    nonempty_indexes = [j for j, data in enumerate(data_window) if data]
    multiplier = math.gcd(*nonempty_indexes, len(data_window))
    new_denominator = denominator // multiplier
    res = f"{{{new_denominator}}}"
    res += ",".join(data_window[::multiplier]) + ",\n"
    return res


# Main script
path = open_maidata_dialog()

try:
    with open(path, "r+t", encoding="utf-8") as f:
        f.seek(0)
        file_contents = f.read()
        f.truncate(0)

        formatted_contents = maidata_formatting(file_contents)

        f.seek(0)
        f.write(formatted_contents)

        pop_alert("Success", "已成功处理maidata文件。")

except Exception as e:
    pop_alert("Error", e)
