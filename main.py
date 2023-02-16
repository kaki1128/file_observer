#!/usr/bin/env python
# coding: utf-8

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import os

folder_abs_path = "/Users/felixchau/PycharmProjects/untitled1/FileObserver/source"

headers = {
    # "Authorization": "Token 42ec9f0c763c330ef91f6a514ab6d182a78cbad2",
}
post_url = 'https://attendance-dev.cerebrohk.com/api/file/test'


def upload_image(_path):
    if os.path.basename(_path) == ".DS_Store":
        return False

    response = requests.post(
        post_url,
        files={'file': (os.path.basename(_path), open(_path, 'rb'), 'application/octet-stream')},
        headers=headers
    )
    return response


def remove_file_2(_path):
    if os.path.exists(_path):
        os.remove(_path)
        print(f"{_path} removed")
    else:
        print(f"not exist: {_path}")


def main_process(_path):
    response = upload_image(_path)
    if not response:
        return

    print("Processing", _path)
    if response.status_code == 200:
        remove_file_2(_path)


# Watchdog
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        main_process(event.src_path)


if __name__ == "__main__":

    # Init file Observer
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=folder_abs_path, recursive=False)
    observer.start()

    # Scan the folder before Run
    for path in os.listdir(folder_abs_path):
        main_process(os.path.join(folder_abs_path, path))

    # Prevent Process end
    try:
        while True:
            time.sleep(60)
            print("Process running")
    finally:
        observer.stop()
        observer.join()

