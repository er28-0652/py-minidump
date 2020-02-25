from minidump import minidump


def main():
    import argparse
    
    p = argparse.ArgumentParser()
    p.add_argument('-p', '--pid', type=int, help='Process ID to dump')
    p.add_argument('-d', '--dest', type=str, help='Dest path to save dump file')
    p.add_argument('-s', '--snapshot', action='store_true', help='Enable if dump from snapshot')

    args = p.parse_args()
    if args.snapshot is True:
        minidump_func = minidump.create_minidump_from_snapshot
    else:
        minidump_func = minidump.create_minidump

    try:
        dump_path = minidump_func(args.pid, args.dest)
        print(f'[*] PID: {args.pid} -> {dump_path}')
    except Exception as e:
        print(f'[!] {e}')

if __name__ == '__main__':
    main()