import os
import sys
import json
import subprocess
import random
import time
import datetime

'''
Usage: first argument must be channel id, 
possible options: 
    --edit-checkpoint: manually move pointer of checkpoint to a certain video
    --init-checkpoint: pre-define a download path for a channel
    --log: save download errors in <channel_id>_download.log, parameter: append [not clear previous log]
    --slow: slow mode, stop around 10 min every video finished during automatic mode
    -q: quiet mode, do not ask about path at beginning
    -y: automatic mode, automatic go over the list without asking continue or not
'''

'''
checkpoint file: a pointer indicating which video should be download during next start, index counting from the end of video list (from old video to new), starting from 0. 
'''

# define download path with method chaining
class DirChain(object): 
    def __init__(self, path=os.getcwd()) -> None:
        super().__init__()
        self._path = path
    
    def __getattr__(self, path): 
        return DirChain(os.path.join(self._path, path))

    def __call__(self, upload_date: str):
        '''Enter date to create a path with name of the date'''
        return DirChain(os.path.join(self._path, upload_date))

# update existing check point
def new_checkpoint(current_index, video_info_list, old_check_point, channel_id): 
    download_check_point = old_check_point
    download_check_point['index'] = current_index
    if current_index>=len(video_info_list): 
        download_check_point['videoId'] = None
        download_check_point['videoTitle'] = 'Latest video has been downloaded!'
    else: 
        download_check_point['videoId'] = video_info_list[current_index]['videoId']
        download_check_point['videoTitle'] = video_info_list[current_index]['title']
    with open('%s_checkpoint.json' % channel_id, 'w') as f: 
        json.dump(download_check_point, f)

# ask whether continue download after a video has been finished
def ask_continue(current_video_title: str)->str:  
    continue_signal = input("Video %s has been finished, continue? [y]/n\n"%current_video_title)
    if continue_signal.lower() in ['', 'y', 'yes']: 
        return "Continue"
    elif continue_signal.lower() == 'n': 
        return "Break"
    else: 
        print('Invalid input!')
        return 'Invalid'

# manually change pointer of checkpoint, note the index in checkpoint file is count from the end of video list, starting at 0
def edit_checkpoint(channel_id: str): 
    with open("%s_list.json" % channel_id) as f: 
        video_info_list = json.load(f)
    if os.path.isfile('%s_checkpoint.json' % channel_id): 
        with open("%s_checkpoint.json" % channel_id) as f: 
            old_check_point = json.load(f)
    else: 
        raise NameError('No checkpoint file')
    video_info_list.reverse()
    video_title_list = [single_video['title'] for single_video in video_info_list]
    videoId_list = [single_video['videoId'] for single_video in video_info_list]
    # possible key type: index, videoID, title, step
    checkpoint_key = input("Please enter either index, videoId, title, or step(step in form __<step>):\n")
    
    try: 
        # if step
        if checkpoint_key[0:2] == '__': 
            change_step = checkpoint_key.strip('_')
            new_index = old_check_point['index']+int(change_step)
        # if not step, test if the key is index
        else: 
            new_index = int(checkpoint_key)
    except: 
        # check if the key is a known videoID or title
        if checkpoint_key in videoId_list: 
            new_index = videoId_list.index(checkpoint_key)
        elif checkpoint_key in video_title_list: 
            new_index = video_title_list.index(checkpoint_key)
        else: 
            # exit code 1: exit with error
            print('No video is found!')
            return 1
    new_checkpoint(new_index, video_info_list, old_check_point, channel_id)
    return 0
    
# predefine download path for a channel
def init_checkpoint(channel_id):
    download_path = input('Please enter download path: ')
    download_check_point = {
        'index': 0, 
        'videoId': '', 
        'videoTitle': '',
        'download_path': download_path
        }
    with open('%s_checkpoint.json' % channel_id, 'w') as f: 
        json.dump(download_check_point, f)


def main(): 
    channel_id = sys.argv[1]
    
    # predefine download path
    if '--init-checkpoint' in sys.argv: 
        init_checkpoint(channel_id)
    
    # manually edit checkpoint
    if '--edit-checkpoint' in sys.argv: 
        return_code = edit_checkpoint(channel_id)
        if return_code == 1: 
            print('Exit due to error')
            return 1
        if not return_code: 
            print('Success!')
            return 0
    
    # show info in slow mode
    if '--slow' in sys.argv: 
        print("In slow mode")
    
    # initialize download log
    if "--log" in sys.argv: 
        arg_index = sys.argv.index("--log")
        try: 
            log_append = (sys.argv[arg_index+1] == "append")
        except IndexError: 
            log_append = False
        if log_append: 
            with open('%s_download.log' % channel_id, "a") as f: 
                f.write(str(datetime.datetime.today())+' Process begin\n')
        else: 
            with open('%s_download.log' % channel_id, 'w') as f: 
                f.write(str(datetime.datetime.today())+' Process begin\n')
    
    with open('%s_list.json' % channel_id) as f: 
        video_info_list = json.load(f)
    
    # load checkpoint file, if none existing, create one using working path as download path
    if os.path.isfile('%s_checkpoint.json' % channel_id): 
        with open('%s_checkpoint.json' % channel_id) as f: 
            download_check_point = json.load(f)
    else: 
        download_check_point = {
            'index': 0, 
            'videoId': '', 
            'videoTitle': '',
            'download_path': os.getcwd()
        }
    
    # ask to change download path if not in quiet mode 
    while True: 
        print("Current download path: %s" % download_check_point['download_path'])
        if '-q' not in sys.argv: 
            new_path = input("If changing, enter new path: ")
            if new_path: 
                download_check_point['download_path'] = new_path
                break
            else: 
                break
        else: 
            break
    
    current_path = download_check_point['download_path']
    current_index = download_check_point['index']
    try: 
        while current_index<len(video_info_list): 
            try: 
                # get info of video to download
                current_video = video_info_list[-current_index-1]
                current_video_id = current_video["videoId"]
                current_video_title = current_video["title"]
                current_video_date = current_video["date"].strip('-')
                current_video_folder = DirChain(current_path).downloads(channel_id).by_upload_date(current_video_date)._path

                try: 
                    # construct argument for yt-dlp
                    current_video_url = 'https://www.youtube.com/watch?v='+current_video_id
                    if not os.path.isdir(current_video_folder): 
                        os.makedirs(current_video_folder)
                    dlp_args = [
                        'yt-dlp', 
                        '--quiet', 
                        '--path', current_video_folder, 
                        '--output', current_video_title.replace('/', '|')+' ['+current_video_id+']', 
                        current_video_url
                    ]
                    # run yt-dlp and display messages, save log if log option is on
                    completed_dlp = subprocess.run(dlp_args, capture_output=True)
                    print(completed_dlp.stdout.decode('utf-8'), completed_dlp.stderr.decode('utf-8'))
                    dlp_out = current_video_id+' on '+current_video_date+': '+''.join((completed_dlp.stdout.decode('utf-8'), completed_dlp.stderr.decode('utf-8'))).rstrip()+'\n'
                    if "--log" in sys.argv: 
                        with open('%s_download.log' % channel_id, 'a') as f: 
                            f.write(dlp_out)

                    # keep download if in automatic mode, or ask whether to continue if not automatic mode
                    if '-y' in sys.argv: 
                        print('Video %s, %s on %s has been finished. '%(current_video_id, current_video_title, current_video_date))
                        if '--slow' in sys.argv: 
                            # sleep in slow mode
                            sleep_length = random.randint(500, 700)
                            for i in range(sleep_length):
                                try: 
                                    time.sleep(1)
                                except KeyboardInterrupt: 
                                    # make checkpoint pointer proceed if interrupted by keyboard
                                    current_index += 1
                                    raise KeyboardInterrupt 
                        pass
                    else: 
                        continue_code = "Invalid"
                        while continue_code == "Invalid": 
                            continue_code = ask_continue(current_video_title)
                        if continue_code == "Continue": 
                            pass
                        elif continue_code == "Break": 
                            current_index += 1
                            break
                        else: 
                            break

                except: 
                    raise
                else: 
                    # if all steps finished successfully, make checkpoint proceed
                    current_index += 1

            except: 
                raise
        if current_index>=len(video_info_list): 
            print('All videos downloaded!')
    except KeyboardInterrupt: 
        print('Exit with keyboard.')
    finally: 
        # save checkpoint
        video_info_list_inv = video_info_list
        video_info_list_inv.reverse()
        new_checkpoint(current_index, video_info_list_inv, download_check_point, channel_id)






if __name__ == "__main__": 
    main()