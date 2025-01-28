# DupLn

![DupLn Logo](dupln.png)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PyPI version fury.io](https://badge.fury.io/py/dupln.svg)](https://pypi.python.org/pypi/dupln/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/dupln.svg)](https://pypi.python.org/pypi/dupln/)
[![PyPI license](https://img.shields.io/pypi/l/dupln.svg)](https://pypi.python.org/pypi/dupln/)
![Python package](https://github.com/biojet1/dupln/workflows/Python%20package/badge.svg)
![Upload Python Package](https://github.com/biojet1/dupln/workflows/Upload%20Python%20Package/badge.svg)

[github.com/biojet1/dupln](https://github.com/biojet1/dupln)
[pypi.org/project/dupln](https://pypi.org/project/dupln/)

Hard link files with same content

# Install

```
> pip install dupln
```

# Usage

## hard link files with same content

```
> dupln link '/tmp/dupln'
INFO: Scanning: '/tmp/dupln'
INFO: ++ '/tmp/dupln/as/ci/i_letters' [2]
INFO:  - '/tmp/dupln/as/cii_letters' - '/tmp/dupln/as/tmp7uwq0r4l' [1]
INFO:  - '/tmp/dupln/as/ci/i_/letters' - '/tmp/dupln/as/ci/i_/tmp0beeaxht' [0]
INFO: ++ '/tmp/dupln/as/ci/i_uppercase' [2]
INFO:  - '/tmp/dupln/as/ci/i_/uppercase' - '/tmp/dupln/as/ci/i_/tmpcsykrlv5' [1]
INFO:  - '/tmp/dupln/as/cii_uppercase' - '/tmp/dupln/as/tmp5knmbazf' [0]
INFO: ++ '/tmp/dupln/as/ci/i_/lowercase' [2]
INFO:  - '/tmp/dupln/as/ci/i_lowercase' - '/tmp/dupln/as/ci/tmpxeegm9eu' [1]
INFO:  - '/tmp/dupln/as/cii_lowercase' - '/tmp/dupln/as/tmp8ra1cf6z' [0]
INFO: ++ '/tmp/dupln/di/gits' [1]
INFO:  - '/tmp/dupln/di/gi/ts' - '/tmp/dupln/di/gi/tmp80gznyej' [0]
INFO: ++ '/tmp/dupln/he/xd/ig/its' [2]
INFO:  - '/tmp/dupln/he/xd/igits' - '/tmp/dupln/he/xd/tmpg3jm_ttb' [1]
INFO:  - '/tmp/dupln/he/xdigits' - '/tmp/dupln/he/tmp2nqxy47g' [0]
INFO: ++ '/tmp/dupln/oc/td/igits' [2]
INFO:  - '/tmp/dupln/oc/tdigits' - '/tmp/dupln/oc/tmpodvxqodo' [1]
INFO:  - '/tmp/dupln/oc/td/ig/its' - '/tmp/dupln/oc/td/ig/tmp1um7nupk' [0]
INFO: ++ '/tmp/dupln/pr/intable' [2]
INFO:  - '/tmp/dupln/pr/in/ta/ble' - '/tmp/dupln/pr/in/ta/tmploz2qhry' [1]
INFO:  - '/tmp/dupln/pr/in/table' - '/tmp/dupln/pr/in/tmptf8egynt' [0]
INFO: ++ '/tmp/dupln/pu/nc/tu/ation' [2]
INFO:  - '/tmp/dupln/pu/nctuation' - '/tmp/dupln/pu/tmp4yjomdni' [1]
INFO:  - '/tmp/dupln/pu/nc/tuation' - '/tmp/dupln/pu/nc/tmpp0hsusw1' [0]
INFO: ++ '/tmp/dupln/wh/it/es/pace' [2]
INFO:  - '/tmp/dupln/wh/it/espace' - '/tmp/dupln/wh/it/tmpd2plpkm7' [1]
INFO:  - '/tmp/dupln/wh/itespace' - '/tmp/dupln/wh/tmpg7bw47b1' [0]
INFO: Total disk_size 564b; files 35; inodes 35; linked 17; same_hash 9; same_size 8; size 1.1k; uniq_hash 9;
```

## list unique file content

```
> dupln uniques '/tmp/dupln'
INFO: Scanning: '/tmp/dupln'
/tmp/dupln/as/ci/i_/letters
/tmp/dupln/ascii_letters
/tmp/dupln/as/cii_uppercase
/tmp/dupln/as/cii_lowercase
/tmp/dupln/ascii_lowercase
/tmp/dupln/ascii_uppercase
/tmp/dupln/di/gi/ts
/tmp/dupln/digits
/tmp/dupln/he/xd/igits
/tmp/dupln/hexdigits
/tmp/dupln/oc/td/igits
/tmp/dupln/octdigits
/tmp/dupln/pr/in/table
/tmp/dupln/printable
/tmp/dupln/pu/nctuation
/tmp/dupln/punctuation
/tmp/dupln/wh/itespace
/tmp/dupln/whitespace
INFO: Total devices 1; disk_size 564b; files 35; inodes 18; same_ino 9; size 1.1k; unique_size 8;
```

## show stats about duplicate files

```
> dupln stat '/tmp/dupln'
INFO: Scanning: '/tmp/dupln'
INFO: Total disk_size 564b; files 35; inodes 18; same_ino 9; same_size 8; size 1.1k;
```

## stats meaning

- disk_size - total size excluding duplicate files
- size - total size including duplicate files
- files - total files found
- inodes - total unique i-nodes found
- same_ino - total unique i-nodes found at least twice
- same_size - total unique size found at least twice
- same_hash - total unique hash found at least twice
- unique_size - total unique size found
- uniq_hash - total unique file hash found
