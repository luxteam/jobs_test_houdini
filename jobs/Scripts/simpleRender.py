import argparse

def create_parser():
    p = argparse.ArgumentParser()


    p.add_argument('file_filter')
    p.add_argument('test_filter')

    p.add_argument('--resolution_x', required=True)
    p.add_argument('--resolution_y', required=True)
    p.add_argument('--pass_limit', required=True)
    p.add_argument('--update_refs', required=True)
    p.add_argument('--tool', required=True, metavar='<path>')
    p.add_argument('--res_path', required=True)
    p.add_argument('--output', required=True, metavar='<path>')

    return p

if __name__ == '__main__':
    print('work')