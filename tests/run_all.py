#!/usr/bin/env python3
"""Runs every tests/e2e_*.py page test (Playwright, Bungie mocked, pages opened from file://).

Each test prints a final line `errors [...]`; a test fails when that list isn't empty, when it crashes
(Traceback) or when it times out. Failures are run once more on their own (busy machines make page tests
time out); only a test that fails twice fails the run. The tests were written against fixed paths, so on a fresh machine this
script links them to the repo first:
  /home/claude/godroll-checker -> the repo
  /home/claude/probe, /home/claude/wl -> tests/fixtures (trimmed god roll lists)
  /home/claude/tests -> tests/out (screenshots)
Usage: python tests/run_all.py [-j 4] [name_filter]
perf_*.py are speed benchmarks, run by hand (they compare against an older checkout)."""
import os, sys, glob, subprocess, concurrent.futures, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LINKS = {
    '/home/claude/godroll-checker': REPO,
    '/home/claude/probe': os.path.join(HERE, 'fixtures'),
    '/home/claude/wl': os.path.join(HERE, 'fixtures'),
    '/home/claude/tests': os.path.join(HERE, 'out'),
}

def link_paths():
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    for path, target in LINKS.items():
        if os.path.exists(path):
            continue
        parent = os.path.dirname(path)
        if not os.path.isdir(parent):
            subprocess.run(['sudo', 'mkdir', '-p', parent], check=True)
            subprocess.run(['sudo', 'chown', str(os.getuid()), parent], check=True)
        os.symlink(target, path)

def run(path, timeout=420):
    t0 = time.time()
    try:
        out = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=timeout, cwd=os.path.join(HERE, 'out'))
        text = out.stdout + out.stderr
    except subprocess.TimeoutExpired as e:
        return path, False, 'timed out after %ds' % timeout, time.time() - t0
    lines = [l for l in text.splitlines() if l.startswith('errors')]
    ok = 'Traceback' not in text and bool(lines) and lines[-1].strip() == 'errors []'
    # on failure keep the end of the output (Playwright call log, traceback), so CI logs show what went wrong
    tail = '\n'.join('        | ' + l for l in text.strip().splitlines()[-30:])
    why = '' if ok else ((lines[-1] if lines else 'crashed') + '\n' + tail)
    return path, ok, why, time.time() - t0

def main():
    args = sys.argv[1:]
    jobs = 4
    if '-j' in args:
        i = args.index('-j'); jobs = int(args[i + 1]); del args[i:i + 2]
    link_paths()
    tests = sorted(glob.glob(os.path.join(HERE, 'e2e_*.py')))
    if args:
        tests = [t for t in tests if any(a in os.path.basename(t) for a in args)]
    failed = []
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        for path, ok, why, secs in ex.map(run, tests):
            name = os.path.basename(path)
            print(('PASS ' if ok else 'FAIL ') + name.ljust(26) + ('%5.0fs' % secs) + ('' if ok else '  ' + why), flush=True)
            if not ok:
                failed.append(name)
    # a page test can time out when several browsers share a small machine: run failures again, one at a time
    flaky = []
    if failed:
        print('\nRunning %d failed test(s) again, one at a time...' % len(failed), flush=True)
        still = []
        for name in failed:
            path, ok, why, secs = run(os.path.join(HERE, name))
            print(('PASS ' if ok else 'FAIL ') + name.ljust(26) + ('%5.0fs' % secs) + ('  (flaky: passed on retry)' if ok else '  ' + why), flush=True)
            (flaky if ok else still).append(name)
        failed = still
    print('\n%d tests, %d failed%s%s' % (len(tests), len(failed), (': ' + ', '.join(failed)) if failed else '', ('; passed on retry: ' + ', '.join(flaky)) if flaky else ''))
    sys.exit(1 if failed else 0)

if __name__ == '__main__':
    main()
