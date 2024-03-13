from pathlib import Path
import shutil
import json
import shortuuid
import warnings
import math
from .cusArgparser import DataClass

root_dir=Path(__file__).parent.parent


class Preprocessor:
    def __init__(self,other_args:DataClass) -> None:
        self.args=other_args
        self.split_dirname=self.args.split_dirname
        self.split_dir=root_dir.joinpath(self.split_dirname)
        if self.split_dir.exists():
            shutil.rmtree(self.split_dir)
        self.split_dir.mkdir()

    @staticmethod
    def generate_uuid(uuid_list):
        uuid=""
        while uuid in uuid_list or uuid=="":
            uuid=shortuuid.uuid()
        return uuid

    def give_uuids(self,data:dict):
        uuids=[]
        for i in data:
            i['uuid']=self.generate_uuid(uuids)
            uuids.append(i['uuid'])
        return data

    def split_file(self):
        filepath:Path=[i for i in root_dir.glob(self.args.filename)][0]
        splitted_files=[]
        concurrent_num:int=self.args.concurrent_num
        if concurrent_num>20:
            warnings.warn("WARNING! concurrent_num<=20 is recommended. Current setting: %s" % (concurrent_num))
        with filepath.open('r',encoding='utf8') as read_jsn:
            dataset=json.load(read_jsn)
        print("dataset total length:",len(dataset))
        split_chunk=math.ceil(len(dataset)/concurrent_num)
        print("splitted file contains data length:", len(split_chunk))
        for idx in range(1,concurrent_num+1):
            s_dataset=dataset[(idx-1)*split_chunk:idx*split_chunk]
            sfname=f"{self.args.input_filename.rsplit(".",0)}_{idx}.json"
            sfpath=self.split_dir.joinpath(sfname)
            with sfpath.open('w',encoding='utf8') as write_jsn:
                json.dump(s_dataset,write_jsn,ensure_ascii=False,indent=2)
            splitted_files.append(sfpath)
        print("file saved length: ",idx+1)
        return splitted_files

    

