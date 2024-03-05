from dataclasses import dataclass, field
import argparse
import os
from rich import print
import sys

from cusArgparser import OpenaiArguments,OtherArguments,CusArgumentParser

def _load_argparser():
    parser=CusArgumentParser((OpenaiArguments,OtherArguments))
    print(sys.argv)
    if sys.argv[-1].endswith(".yaml"):
        openai_args,others_args=parser.parse_yaml_file(yaml_file=os.path.abspath(sys.argv[-1]))
    else:
        openai_args,others_args=parser.parse_args_into_dataclasses()
    return openai_args,others_args

def load_argparser():
    parser=argparse.ArgumentParser(description="quick,stable and convenient to batch request openai")
    parser.add_argument(
        "-f", "--file", dest="filename",
        help="write something to $FILE",
        metavar="$FILE"
    )
    args=parser.parse_args()
    print(args)

if __name__=='__main__':
    _load_argparser()