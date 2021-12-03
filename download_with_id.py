# -*- coding: utf8 -*-

import subprocess
import time


def main(): 
    continue_flag = 'y'
    while continue_flag in ['y', 'r']: 
        if continue_flag == 'y': 
            video_ids = input("Please enter video ID: \n").split(',')
        for video_id in video_ids: 
            video_url = 'https://www.youtube.com/watch?v='+video_id.strip()
            dlp_args = [
                            'yt-dlp', 
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