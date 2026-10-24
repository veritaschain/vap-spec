import argparse
import json
import time


def main():
    parser = argparse.ArgumentParser(description='Unadopted OS-isolation mock experiment')
    parser.add_argument('command', choices=['init', 'serve', 'idle', 'probe', 'run-suite', 'verify-evidence'])
    parser.add_argument('arguments', nargs='*')
    parser.add_argument('--output', default='generated')
    args = parser.parse_args()
    if args.command == 'init':
        from .seed import initialize
        initialize(args.arguments[0])
    elif args.command == 'serve':
        from .runtime import serve
        serve(args.arguments[0])
    elif args.command == 'idle':
        while True:
            time.sleep(30)
    elif args.command == 'verify-evidence':
        from record_gate.suite import verify_bundle
        from scope_verifier.crypto import strict_json
        verify_bundle(strict_json(args.arguments[0]))
        print('Evidence signatures and both verifier reports rechecked; synthetic trust only; no OS re-execution.')
    elif args.command == 'run-suite':
        from .suite import run_suite
        raise SystemExit(0 if run_suite(args.output) else 1)
    else:
        from . import probe
        name, *values = args.arguments
        if name == 'identity':
            result = probe.identity()
        elif name == 'filesystem':
            result = probe.filesystem(values[0])
        elif name == 'network':
            result = probe.network(values[0], int(values[1]), *values[2:])
        elif name == 'execute':
            result = probe.execute_request(values[0])
        elif name == 'counts':
            result = probe.counts()
        elif name == 'export':
            result = probe.export_events()
        elif name == 'local-log':
            result = probe.local_log(values[0])
        elif name == 'health':
            from .transport import exchange
            status, result = exchange('127.0.0.1', 8080, '/health', method='GET')
            if status != 200:
                raise SystemExit(1)
        else:
            raise ValueError('unknown_probe')
        print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
