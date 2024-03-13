import sys
import os
import tiktoken
from .cusArgparser import CusArgumentParser,OpenaiArguments,OtherArguments

def construct_prompts(args,fields:dict):
    sys_prompt:str=args.sys_prompt
    user_prompt:str=args.user_prompt
    user_prompt.format(**fields)
    return sys_prompt,user_prompt

def load_argparser():
    parser=CusArgumentParser((OpenaiArguments,OtherArguments))
    print(sys.argv)
    if sys.argv[-1].endswith(".yaml"):
        openai_args,others_args=parser.parse_yaml_file(yaml_file=os.path.abspath(sys.argv[-1]))
    else:
        openai_args,others_args=parser.parse_args_into_dataclasses()
    return openai_args,others_args

def statistics(args):
    pass

def estimator(args):
    pass

if __name__=="__main__":
    load_argparser()