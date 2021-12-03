# -*- coding: utf8 -*-

import subprocess
import time
import os
import json

from download_w_list import DirChain

def main(): 
    download_path = os.getcwd()
    while True: 
        new_path = input("Please enter a specified path or a channel ID: (leave blank to download in working path)\n")
        if new_path: 
            if os.path.isdir(new_path): 
                download_path = new_path
                break
            elif os.path.isfile(os.path.join("download_logs", "%s_checkpoint.json"%new_path)): 
                with open(os.path.join("download_logs", "%s_checkpoint.json"%new_path)) as f: 
                    download_checkpoint = json.load(f)
                project_path = download_checkpoint['download_path']
                download_path = DirChain(project_path).downloads(new_path).by_upload_date._path
                break
    continue_flag = 'y'
    while continue_flag in ['y', 'r']: 
        if continue_flag == 'y': 
            video_ids = input("Please enter video ID: \n").split(',')
        for video_id in video_ids: 
            video_url = 'https://www.youtube.com/watch?v='+video_id.strip()
            dlp_args = [
                            'yt-dlp', 
                            '--path', 
                            download_path, 
                            '-o', 
                            '%(upload_date>%Y-%m-%d)s/%(title)s [%(id)s].%(ext)s', 
                            video_url
                        ]
            subprocess.run(dlp_args)
            if len(video_ids) > 1: 
                time.sleep(60)
        continue_input = False
        while not continue_input: 
            continue_flag = input("Retry [r], Continue [y], Quit [n]\n")
            if continue_flag in ['y', 'n', 'r']: 
                continue_input = True
        
if __name__ == '__main__': 
    main()