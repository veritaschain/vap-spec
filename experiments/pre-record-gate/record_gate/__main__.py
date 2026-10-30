import argparse
import json
from scope_verifier.crypto import strict_json


def main():
    parser = argparse.ArgumentParser(description='Unadopted local-only execution gate experiment')
    parser.add_argument('command', choices=['service', 'worker', 'run-suite', 'verify-exports'])
    parser.add_argument('--config')
    parser.add_argument('--request')
    parser.add_argument('--fault', choices=['crash-after-prepare', 'crash-after-claim'])
    parser.add_argument('--output', default='generated')
    args = parser.parse_args()
    if args.command == 'service':
        from .services import serve
        serve(strict_json(args.config))
    elif args.command == 'worker':
        from .gate import execute
        print(json.dumps(execute(strict_json(args.config), strict_json(args.request), fault=args.fault)))
    elif args.command == 'verify-exports':
        from .suite import verify_exports
        verify_exports(args.output)
    else:
        from .suite import run_suite
        raise SystemExit(0 if run_suite(args.output) else 1)


if __name__ == '__main__':
    main()
