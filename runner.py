from pathlib import Path
from rich import print
import json

from args import _load_argparser
from src.cusSplitter import CusSplitter
from utils import give_uuids,construct_prompts

root_dir=Path(__file__).parent

class QBARunner:
    
    def __init__(self) -> None:
        self.openai_args,self.others_args=_load_argparser()
        self.input_filename=self.others_args.input_filename
        input_filepath=root_dir.joinpath(self.input_filename)
        with input_filepath.open('r',encoding='utf8') as read_jsn:
            self.data=json.load(read_jsn)
        
    
    @staticmethod
    def main():
        openai_args,others_args=_load_argparser()
        print("openai_args:\n",openai_args)
        print("others_args:\n",others_args)

        input_filename=others_args.input_filename
        input_filepath=root_dir.joinpath(input_filename)
        with input_filepath.open('r',encoding='utf8') as read_jsn:
            data=json.load(read_jsn)
        data=give_uuids(data)
    


if __name__=='__main__':
    QBARunner.main()

