# -*- coding: utf8 -*-

'''
A tool to check whether local videoID's match video info list ID's
argument: channel ID
optional arguments after channel ID: 
    start index
    end index
'''

import os
import json
import sys

from download_w_list import DirChain


# a function convert str to num for better sorting
def str2num(input_str: str)->int: 
    return int(''.join([str(i) for i in list(input_str.encode('utf8'))]))

# a function to find out index of unique elements of two lists (May be clearer to use set? )
def compare_list(sorted_list_1: list, sorted_list_2: list)->tuple: 
    if not sorted_list_1: 
        return tuple(), tuple(sorted_list_2)
    elif not sorted_list_2: 
        return tuple(sorted_list_1), tuple()
    
    if len(sorted_list_1)<len(sorted_list_2): 
        short_list = sorted_list_1
        long_list = sorted_list_2
        switch_flag = True
    else: 
        long_list = sorted_list_1
        short_list = sorted_list_2
        switch_flag = False
    
    long_list_i = 0
    short_list_i = 0
    long_list_unique = []
    short_list_unique = []
    while True: 
        if long_list[long_list_i] == short_list[short_list_i]: 
            long_list_i += 1
            short_list_i += 1
        elif long_list[long_list_i] < short_list[short_list_i]: 
            long_list_unique.append(long_list_i)
            long_list_i += 1
        else: 
            short_list_unique.append(short_list_i)
            short_list_i += 1
        if long_list_i >= len(long_list) or short_list_i>=len(short_list): 
            break
    if long_list_i < len(long_list): 
        long_list_unique += list(range(long_list_i, len(long_list)))
    if short_list_i < len(short_list): 
        short_list_unique += list(range(short_list_i, len(short_list)))
    short_unique_itmes = [short_list[i] for i in short_list_unique]
    long_unique_items = [long_list[i] for i in long_list_unique]
    if switch_flag: 
        return tuple(short_unique_itmes), tuple(long_unique_items)
    else: 
        return tuple(long_unique_items), tuple(short_unique_itmes)

# get video id from local downloaded webm files
def get_downloaded_id(scan_path: str)->list: 
    fname_list = []
    for dirpath, dirname, fnames in os.walk(scan_path): 
        for fname in fnames: 
            if os.path.splitext(fname)[1] in ['.webm', '.mp4']:  
                fpath = os.path.join(dirpath, fname)
                hidden_flag = False
                test_path = fpath
                while True: 
                    former_part, latter_part = os.path.split(test_path)
                    test_path = former_part
                    if latter_part: 
                        if latter_part[0] == '.': 
                            hidden_flag = True
                            break
                    if former_part in ('/', '.', ''): 
                        break
                if not hidden_flag: 
                    fname_list.append(os.path.splitext(fname)[0])
    loc_id_list = [f[-12:-1] for f in fname_list]
    return tuple(loc_id_list)

def main(): 
    channel_id = sys.argv[1]
    start_index = 0
    end_index = 0
    if len(sys.argv) >= 3: 
        start_index = int(sys.argv[2])
    if len(sys.argv) >= 4: 
        end_index = int(sys.argv[3])
    
    # from checkpoint file get download path and current index
    with open(os.path.join('download_logs', '%s_checkpoint.json' % channel_id)) as f: 
        download_checkpoint = json.load(f)
    current_path = download_checkpoint['download_path']
    current_index = download_checkpoint['index']
    scan_path = DirChain(current_path).downloads(channel_id)._path
    # get local videoID's and sort
    loc_id_list = get_downloaded_id(scan_path)
    loc_id_list_sorted = sorted(loc_id_list, key=str2num)
    loc_id_num_list_sorted = [str2num(vid) for vid in loc_id_list_sorted]
    
    # get video info list ID's and sort
    with open(os.path.join('video_lists', '%s_list.json' % channel_id)) as f: 
        video_list = json.load(f)
    video_list.reverse()
    if not end_index: 
        end_index = current_index
    list_id_list = [single_video['videoId'] for single_video in video_list[start_index:end_index]]
    list_id_list_sorted = sorted(list_id_list, key=str2num)
    sort_info = lambda info_dict: str2num(info_dict['videoId'])
    list_info_sorted = sorted(video_list, key=sort_info)
    list_id_num_list_sorted = [str2num(vid) for vid in list_id_list_sorted]
    
    # get unique videoID's for local and info list respectively
    loc_unique_vid, list_unique_vid = compare_list(loc_id_num_list_sorted, list_id_num_list_sorted)

    with open(os.path.join('download_logs', '%s_diff.json'%channel_id), 'w') as f: 
        json.dump(list_unique_vid, f)
    
    # format output string
    list_unique_info = ['Date: %s, ID: %s'%(list_info_sorted[i]['date'], list_id_list_sorted[i]) for i in list_unique_i]
    list_unique_info_str = '\n'.join(list_unique_info)
    loc_unique_vid_str = '\n'.join(loc_unique_vid)

    log_str = 'List unique: \n'+list_unique_info_str+'\n\nLocal unique: \n'+loc_unique_vid_str

    with open(os.path.join('download_logs', '%s_diff.list'%channel_id), 'w') as f: 
        f.write(log_str)

    
if __name__ == "__main__": 
    main()
