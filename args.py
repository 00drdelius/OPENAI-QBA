from dataclasses import dataclass, field
import argparse
import os
from rich import print
import sys

from src._argparser import CusArgumentParser

@dataclass
class OpenaiArguments:
    api_key:str=field(metadata={"help":"openai api key"})
    api_base:str=field(metadata={"help":"base url for China mainland to request openai"})
    model:str=field(metadata={"help":"gpt model"})
    temperature:float=field(metadata={"help":"temperature"})
    timeout:float=field(metadata={'help':'timeout parameter'})

@dataclass
class OtherArguments:
    concurrent_num:int=field(metadata={"help":"concurrent num, aka num of data to split."})
    input_filename:str=field(metadata={"help":"input filename"})
    output_dirname:str=field(metadata={"help":"output dirname"})

def _load_argparser():
    parser=CusArgumentParser((OpenaiArguments,OtherArguments))
    if sys.argv[-1].endswith(".yaml"):
        openai_args,others_args=parser.parse_yaml_file(yaml_file=os.path.abspath(sys.argv[-1]))
    else:
        openai_args,others_args=parser.parse_args_into_dataclasses()
    print(openai_args)
    print(others_args)
    
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