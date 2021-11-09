import os

music_root_dir = './OBM22/Musik/sorted'


def create_playlist_recursive(directory, name):
    dir_items = os.listdir(directory)
    sub_dirs = []
    music_files = []
    for dir_item in dir_items:
        full_path = os.path.join(directory, dir_item)

        if os.path.isdir(full_path):
            sub_dirs.append(dir_item)
            continue

        if not os.path.isfile(full_path):
            continue

        music_files.append(dir_item)

    if len(music_files) > 0:
        with open(os.path.join(directory, name + '.m3u'), 'w') as f:
            for music_file in sorted(music_files):
                if not music_file.startswith('.') and music_file.lower().endswith('mp3'):
                    f.writelines(music_file + '\n')
    
    for sub_dir in sub_dirs:
        if name:
            new_name = name + '-' + sub_dir
        else:
            new_name = sub_dir
        create_playlist_recursive(os.path.join(directory, sub_dir), new_name)


if __name__ == '__main__':
    create_playlist_recursive(music_root_dir, '')