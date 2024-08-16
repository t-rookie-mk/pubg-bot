import os
# 本项目名称
project_name = 'pubg-bot'


def get_src_directory(find_path=project_name):
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    
    # 获取当前文件所在的目录
    current_dir = os.path.dirname(current_file_path)
    
    # 循环向上查找直到找到 find_path 目录
    while True:
        src_dir = os.path.join(current_dir, find_path)
        if os.path.exists(src_dir) and os.path.isdir(src_dir):
            return os.path.abspath(src_dir)
        
        # 获取上一级目录
        parent_dir = os.path.dirname(current_dir)
        
        # 如果当前目录已经是根目录，则停止搜索
        if parent_dir == current_dir:
            break
        
        current_dir = parent_dir
    
    return None  # 如果没有找到 src 目录

def get_images_map():
        root_path = get_src_directory()
        at_lobby = os.path.join(root_path, 'resources\\lobby\\at_lobby.bmp')
        start_match = os.path.join(root_path, 'resources\\lobby\\start_match.bmp')
        loading = os.path.join(root_path, 'resources\\loading\\loading.bmp')

        plane = os.path.join(root_path, 'resources\\plane\\plane.bmp')
        map_ok = os.path.join(root_path, 'resources\\plane\\map.bmp')

        ground = os.path.join(root_path, 'resources\\ground\\ground.bmp')
        bp_start = os.path.join(root_path, 'resources\\ground\\bp_start.bmp')

        error = os.path.join(root_path, 'resources\\error\\error.bmp')
        error1 = os.path.join(root_path, 'resources\\error\\error1.bmp')
        error2 = os.path.join(root_path, 'resources\\error\\error2.bmp')
        error3 = os.path.join(root_path, 'resources\\error\\error3.bmp')
        refresh = os.path.join(root_path, 'resources\\error\\refresh.bmp') 
        
        return1 = os.path.join(root_path, 'resources\\return\\return1.bmp')
        return2 = os.path.join(root_path, 'resources\\return\\return2.bmp')
        return3 = os.path.join(root_path, 'resources\\return\\return3.bmp')

        return {
             'at_lobby': at_lobby,
             'start_match': start_match,
             'loading': loading,
             'plane': plane,
             'map_ok': map_ok,
             'ground': ground,
             'bp_start': bp_start,
             
             'error': error,
             'error1': error1,
             'error2': error2,
             'error3': error3,
             'refresh': refresh,

             'return1': return1,
             'return2': return2,
             'return3': return3
        }