import sys
import argparse

from .apply_config import main as apply_config
from .metrics_exporter import main as metrics_exporter


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='wrtmgr')
    subparsers = parser.add_subparsers()

    p = subparsers.add_parser('apply_config')
    p.set_defaults(func=apply_config)

    p = subparsers.add_parser('metrics_exporter')
    p.add_argument('--port', type=int, default=9890)
    p.set_defaults(func=metrics_exporter)

    args = parser.parse_args(sys.argv[1:])
    if not hasattr(args, 'func'):
        parser.error('choose a command')

    args.func(args)
