#!/usr/bin/env python
# coding: utf-8

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import os
import json

import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "setting.ini"))

post_url = config["DEFAULT"]["upload_url"]
headers = json.loads(config["DEFAULT"]["headers"])


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

    print("Processing", _path, response.text)
    if response.status_code == 200:
        if config["DEFAULT"]["remove_after_upload"] == "True":
            remove_file_2(_path)


# Watchdog
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        main_process(event.src_path)


if __name__ == "__main__":

    # Init file Observer
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler,
                      path=config["DEFAULT"]["observation_folder"],
                      recursive=config["DEFAULT"]["recursive"] == "True"
                      )
    observer.start()

    # Scan the folder before Run
    for path in os.listdir(config["DEFAULT"]["observation_folder"]):
        main_process(os.path.join(config["DEFAULT"]["observation_folder"], path))

    # Prevent Process end
    try:
        while True:
            time.sleep(60)
            print("Process running", time.strftime("%Y-%m-%d %H:%M:%S +08:00", time.localtime()))
    finally:
        observer.stop()
        observer.join()
