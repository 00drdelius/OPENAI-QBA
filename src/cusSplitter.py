from pathlib import Path
import shutil
import json
import warnings
import math
from .cusArgparser import DataClass

root_dir=Path(__file__).parent.parent


class CusSplitter:
    def __init__(self,args:DataClass) -> None:
        self.args=args
        self.split_dirname="temp_split_dir"
        self.split_dir=root_dir.joinpath(self.split_dirname)
        if self.split_dir.exists():
            shutil.rmtree(self.split_dir)
        self.split_dir.mkdir()

    def split_file(self):
        filepath:Path=[i for i in root_dir.glob(self.args.filename)]
        concurrent_num:int=self.args.concurrent_num
        if concurrent_num>20:
            warnings.warn("WARNING! concurrent_num<=20 is recommended. Current setting: %s" % (concurrent_num))
        with filepath.open('r',encoding='utf8') as read_jsn:
            dataset=json.load(read_jsn)
        print("dataset total length:",len(dataset))
        split_chunk=math.ceil(len(dataset)/concurrent_num)
        for idx in range(1,concurrent_num+1):
            s_dataset=dataset[(idx-1)*split_chunk:idx*split_chunk]
            sfname=f"{self.args.input_filename.rsplit(".",0)}_{idx}.json"
            sfpath=self.split_dir.joinpath(sfname)
            with sfpath.open('w',encoding='utf8') as write_jsn:
                json.dump(s_dataset,write_jsn,ensure_ascii=False,indent=2)
            
            


    

