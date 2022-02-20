from concurrent.futures import ThreadPoolExecutor
from io import TextIOWrapper
import os
import re
import sys
from typing import Any, List, Tuple

ptrn_cmps: List[Tuple[re.Pattern, Any]] = [
    # property getter
    (re.compile('(\w+)\.get([A-Z])(.*?)\(\)'),
     lambda p: f'{p.group(1)}.{p.group(2).lower()}{p.group(3)}'),
    # property getter
    (re.compile('(\w+)\.set([A-Z])(.*?)\((.*)\) *;'),
     lambda p: f'{p.group(1)}.{p.group(2).lower()}{p.group(3)} = {p.group(4)};'),
    # string
    (re.compile('String '), 'string '),
]


def prfm_files(root_dir: str, out_dir: str, tpe: ThreadPoolExecutor):
    [tpe.submit(
        prfm_file(os.path.join(r, f),
                  get_wrt_strm(root_dir, os.path.join(r, f), out_dir))
    )
        for r, _, fs in os.walk(root_dir)
        for f in fs]


def get_wrt_strm(rootdir: str, fl: str, out_dir: str) -> TextIOWrapper:
    out_fl_pth = os.path.join(
        out_dir, fl[len(rootdir.rstrip('\\').rstrip('/'))+1:])
    out_dir_pth = os.path.dirname(out_fl_pth)
    if not os.path.exists(out_dir_pth):
        os.makedirs(out_dir_pth)
    return open(out_fl_pth, 'w', encoding='utf8')


def prfm_file(fl: str, sw: TextIOWrapper):
    print(fl)
    with open(fl, 'r', encoding='shift_jis') as fr:
        [sw.write('{0}\n'.format(prfm(ln.rstrip('\n').rstrip('\r'), ptrn_cmps)))
         for ln in fr.readlines()]
    sw.close()


def prfm(ln: str, ptns: List[Tuple[re.Pattern, Any]]) -> str:
    subed = ptns[0][0].sub(ptns[0][1], ln)
    if (len(ptns) > 1):
        subed = prfm(subed, ptns[1:])
    return subed


def main():
    if len(sys.argv) != 3:
        print('Usage: ')
        print(' 1. input dir')
        print(' 2. output dir')
        return
    inptpth = sys.argv[1]
    outdir = sys.argv[2]
    if os.path.exists(inptpth) and os.path.isdir(inptpth):
        # target is directory
        tpe = ThreadPoolExecutor(max_workers=5)
        prfm_files(inptpth, outdir, tpe)
        tpe.shutdown()
    else:
        print('error! input path is not found!!')


if __name__ == '__main__':
    main()
