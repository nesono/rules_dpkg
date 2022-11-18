#!/usr/bin/env python3
import os
import click
import sys
import subprocess
import re
from typing import Dict, Final, TextIO
import json

STARTS_WITH_WORD_CHAR: Final = re.compile(r'\w+')
APT_CACHE_KEY: Final = re.compile(r'^[a-zA-Z0-9-]+:\s', flags=re.MULTILINE)

def package_meta_info(package_spec: str) -> Dict[str,str]:
    apt_cache_output= subprocess.check_output(['apt-cache', 'show', package_spec]).decode('utf-8')
    keys = [key[:-2].lower() for key in APT_CACHE_KEY.findall(apt_cache_output)]
    values = [value.strip() for value in re.split(APT_CACHE_KEY, apt_cache_output)[1:]]

    return dict(zip(keys, values))
    

def resolve_package_spec_to_print_uris(package_spec: str) -> Dict[str,Dict[str,str]]:
    # pack into dict to ensure no duplicates
    result: Dict[str,Dict[str,str]] = dict()
    apt_cache_output = subprocess.check_output(['apt-cache', 'depends',
        '--recurse', '--no-recommends', '--no-suggests', '--no-conflicts',
        '--no-breaks', '--no-replaces', '--no-enhances', '--no-pre-depends',
        package_spec]).decode('utf-8')
    for package in apt_cache_output.split('\n'):
        if STARTS_WITH_WORD_CHAR.match(package):
            print(f'Found dependency {package}')
            pkg_dict: Dict[str,str] = dict()
            apt_get_download_output = subprocess.check_output(['apt-get', 'download', '--print-uris', package]).decode('utf-8').strip().split(' ')
            pkg_dict['name'] = package
            pkg_dict['url'] = apt_get_download_output[0].strip("'\"")
            pkg_meta_info = package_meta_info(package)
            pkg_dict['sha256'] = pkg_meta_info['sha256']
            result[package] = pkg_dict
    return result


@click.command()
@click.option('-i', '--infile', required=True, type=click.File('r'))
@click.option('-o', '--outfile', required=True, type=click.File('w'))
def cli(infile: TextIO, outfile: TextIO) -> None:
    """Command line tool to turn a package listing into a JSON document, which is to be consumed by the dpgk_repository rule"""
    result = []
    with infile as f:
        deduped_pkgs: Dict[str,Dict[str,str]] = dict()
        for package in f:
            package = package.strip()
            print(f'Resolving package: {package}')
            pkg_dict = resolve_package_spec_to_print_uris(package)
            # dedupe keys
            for key in pkg_dict:
                deduped_pkgs[key] = pkg_dict[key]
        for key in deduped_pkgs:
            result.append(deduped_pkgs[key])
                
    # write dict to JSON output
    with outfile as f:
        f.write(json.dumps(result, indent = 4))

if __name__ == '__main__':
    print(f'Python version: {sys.version}')
    os.chdir(os.environ.get("BUILD_WORKSPACE_DIRECTORY", os.getcwd()))
    cli()
