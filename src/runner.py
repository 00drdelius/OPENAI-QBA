from pathlib import Path
from rich import print
import json
import regex as re

from src.client import OpenaiClient

root_dir=Path(__file__).parent

class SingleRunner:
    """
    Addressing single json file.
    ## Args:
        openai_args,dict: openai arguments
        output_dirPath,Path object: saved json's directory path. To drop saved.
        filePathmPath object: json file path
    """
    def __init__(self,openai_args,client:OpenaiClient,output_dirPath:Path,filePath:Path) -> None:
        self.openai_args=openai_args
        self.client=client
        self.filePath=filePath
        self.fileId=self.filePath.name.rsplit(".",1)[0].rsplit("_",1)[-1]
        self.output_dirPath=output_dirPath
        
        with self.filePath.open('r',encoding='utf8') as jsn:
            self.datas:list=json.load(jsn)
        # drop saved by uuids
        self.datas=self.drop_saved(self.datas)

    def drop_saved(self,datas):
        saved_uuids=[i.name.rsplit(".",1)[0] for i in self.output_dirPath.glob("**/*.json")]
        new_datas=[]
        for d in datas:
            if d['uuid'] not in saved_uuids:
                new_datas.append(d)
        return new_datas
    
    def construct_prompt(self,data:dict) -> tuple[str,str]:
        """
        You may preprocess the json field here, to fit the input_fields in openai args so that passing fields into user_prompt
        ## Args:
        data,dict: single data in single file
        ## Return:
        Tuple( system prompt, user prompt )
        """
        input_dict={k:v for k,v in data.items() if k in self.openai_args.input_fields}
        sys_prompt=self.openai_args.sys_prompt
        user_prompt=self.openai_args.user_prompt.format(**input_dict)
        return sys_prompt,user_prompt

    def send(self):
        output={}
        for data in self.datas:
            sys_prompt,user_prompt=self.construct_prompt(data)
            gpt_outptu
    
    def regular_extract(self,gpt_output:str):
        """
        To extract the text gpt returned, ofter use regular expression.
        """


    @staticmethod
    def main():
        pass


if __name__=='__main__':
    SingleRunner.main()

