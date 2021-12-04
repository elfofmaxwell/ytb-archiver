# -*- coding:utf8 -*-

'''
separated initialization?
if no initialization, use cwd?
change download path? 
one-click start to run?
one-click init to initialize? 
one-click --change-path to change project download path?
one-click start --channel [ID] to start separated project? 
'''

## TODO: change name of secrete file? slow-mode time? 

import os
import json
import sys
import subprocess
import time

# manually change download path
def change_download_path(new_path, channel_id, auto_create=False): 
    checkpoint_path = os.path.join('downlaod_logs', '%s_checkpoint.json'%channel_id)
    if os.path.isfile(checkpoint_path): 
        with open(checkpoint_path) as f: 
            download_checkpoint = json.load(f)
        if not os.path.isdir(new_path): 
            # ask to create folder interactively
            if not auto_create: 
                while True: 
                    mk_dir = input("No such path! Create? [y]/n")
                    if mk_dir == "n": 
                        return 1
                    elif (not mk_dir) or mk_dir == 'y': 
                        os.makedirs(new_path)
                        break
                    else: 
                        print("Invalid input! Try again")
            else: 
                os.makedirs(new_path)
            download_checkpoint['download_path'] = new_path
            with open(checkpoint_path, 'w') as f: 
                json.dump(download_checkpoint, f)
            return 0
    else: 
        print("No existing config! Please initialize")
        return 1


def download_cycle(channel_id: str, project_config: dict): 
    checkpoint_path = os.path.join('download_logs', '%s_checkpoint.json'%channel_id)
    # prepare start index for competence check
    if os.path.isfile(checkpoint_path): 
        with open(checkpoint_path) as f: 
            start_index = json.load(f)['index']
    else: 
        start_index = 0
    
    # get video list
    get_video_args = [
        "python", 
        "get_video_list.py", 
        channel_id
    ]
    subprocess.run(get_video_args)
    time.sleep(5)

    # download video in the list
    download_args = [
        "python", 
        "download_w_list.py", 
        channel_id, 
        "--log", 
        "--slow", 
        str(project_config['slow_mode_time']), 
        "-q", 
        "-y"
    ]
    subprocess.run(download_args)
    time.sleep(5)

    # check competence
    check_args = [
        "python", 
        "completeness_check.py", 
        channel_id, 
        str(start_index)
    ]
    subprocess.run(check_args)
    time.sleep(project_config['slow_mode_time'])


def main(): 
    start_message = "Use init to initialize; \nUse start to start a task. "
    
    # print guidance if no arguments provided
    if len(sys.argv) == 1: 
        print(start_message)
        return 1

    # initialize 
    if sys.argv[1] == "init": 
        if len(sys.argv) >= 3: 
            # initialize with config file
            if sys.argv[2] == '--file': 
                if os.path.isfile("config.json"): 
                    with open("config.json") as f:
                        project_config = json.load(f)
                else: 
                    print("No config file! Please initialize manually")
                    return 1
        else: 
            # initialize interactively
            channel_ID_str = input("Please enter channel ID's, seperated by comma ',': \n")
            channel_ID = [i.strip() for i in channel_ID_str.split(",")]
            download_path = input("Please enter project download path: \n")
            while True: 
                slow_mode_str = input("Please enter wait time for slowmode in second (default 600): \n")
                try: 
                    if not slow_mode_str: 
                        slow_mode_time = 600
                    else: 
                        slow_mode_time = int(slow_mode_str)
                    break
                except ValueError: 
                    print('Invalid input! ')
            project_config = dict()
            project_config['channel_id'] = channel_ID
            project_config['download_path'] = download_path
            project_config['slow_mode_time'] = slow_mode_time
        print("Initializing...")
        while True: 
            # validate download path, if no such path, ask to create
            if not os.path.isdir(project_config['download_path']): 
                mk_dir = input("Download path does not exist. Create? [y]/n/quit\n")
                if mk_dir == 'quit': 
                    print("Quit. ")
                    return 1
                elif mk_dir == 'n': 
                    project_config['download_path'] = input("Please enter another path: \n")
                elif (not mk_dir) or mk_dir == 'y': 
                    os.makedirs(project_config['download_path'])
            else: 
                break
        for channel_id in project_config['channel_id']: 
            # initialize for each channel
            init_args = [
                'python', 
                'download_w_list.py', 
                channel_id, 
                '--init-checkpoint', 
                project_config['download_path']
            ]
            subprocess.run(init_args)
        # dump project config
        with open("config.json", "w") as f: 
            json.dump(project_config, f)
            print("Finished! ")
            return 0
    
    # start a download task
    if sys.argv[1] == "start": 
        with open('config.json') as f: 
            project_config = json.load(f)
        try: 
            if len(sys.argv) == 2: 
                # go over channels in the list defined in config
                for channel_id in project_config['channel_id']: 
                    download_cycle(channel_id, project_config)
                return 0
            if len(sys.argv) == 3: 
                # download contents of a single channel
                channel_id = sys.argv[2]
                download_cycle(channel_id, project_config)
                return 0
        except KeyboardInterrupt: 
            print("End with keyboard")
            return 1
    
    else: 
        print(start_message)
        return 1




if __name__ == '__main__': 
    main()
        

