from argparse import ArgumentParser
from typing import NewType,Iterable,Any
import yaml
import sys
from pathlib import Path
from dataclasses import field,dataclass
import dataclasses

DataClass=NewType("DataClass",Any)
DataClassType=NewType("DataClassType",Any)

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
    input_fields:list=field(metadata={"help":"indicates input value in data, to replace input article in input prompt"})
    output_dirname:str=field(metadata={"help":"output dirname"})


class CusArgumentParser(ArgumentParser):
    def __init__(self, dataclass_types: DataClassType | Iterable[DataClassType], **kwargs):
        super().__init__(**kwargs)
        if dataclasses.is_dataclass(dataclass_types):
            dataclass_types=[dataclass_types]
        self.dataclass_types=list(dataclass_types)
        for dtype in self.dataclass_types:
            self._add_dataclass_arguments(dtype)

    @staticmethod
    def _parse_dataclass_field(parser: ArgumentParser, field: dataclasses.Field):
        field_name=f"--{field.name}"
        kwargs=field.metadata.copy()
        aliases=kwargs.pop("aliases",[])
        aliases = [aliases] if isinstance(aliases,str) else []
        parser.add_argument(field_name,*aliases,**kwargs)
        
    def _add_dataclass_arguments(self,dtype:DataClassType):
        parser = self
        for field in dataclasses.fields(dtype):
            self._parse_dataclass_field(parser,field)

    def parse_args_into_dataclasses(
            self,
    ) -> tuple[DataClass, ...]:
        "Parse command-line args into instances of the specified dataclass types."
        if any(sys.argv):
            args=sys.argv[1:]
        namespace,remaining_args=self.parse_known_args(args=args)
        outputs=[]
        for dtype in self.dataclass_types:
            keys={f.name for f in dataclasses.fields(dtype) if f.init}
            inputs={k:v for k,v in vars(namespace).items() if k in keys}
            for k in keys:
                delattr(namespace, k)
            obj=dtype(**inputs)
            outputs.append(obj)
        if len(namespace.__dict__)>0:
            outputs.append(namespace)
        if remaining_args:
            raise ValueError(f"Some specified arguments are not used by the CusArgumentParser: {remaining_args}")
        return (*outputs,)

    def parse_dict(self, args: dict[str, Any], allow_extra_keys: bool = False) -> tuple[DataClass, ...]:
        """
        Alternative helper method that does not use `argparse` at all, instead uses a dict and populating the dataclass
        types.

        Args:
            args (`dict`):
                dict containing config values
            allow_extra_keys (`bool`, *optional*, defaults to `False`):
                Defaults to False. If False, will raise an exception if the dict contains keys that are not parsed.

        Returns:
            Tuple consisting of:

                - the dataclass instances in the same order as they were passed to the initializer.
        """
        unused_keys = set(args.keys())
        outputs = []
        for dtype in self.dataclass_types:
            keys = {f.name for f in dataclasses.fields(dtype) if f.init}
            inputs = {k: v for k, v in args.items() if k in keys}
            unused_keys.difference_update(inputs.keys())
            obj = dtype(**inputs)
            outputs.append(obj)
        if not allow_extra_keys and unused_keys:
            raise ValueError(f"Some keys are not used by the HfArgumentParser: {sorted(unused_keys)}")
        return tuple(outputs)

    def parse_yaml_file(self, yaml_file: str, allow_extra_keys: bool = False) -> tuple[DataClass, ...]:
        """
        Alternative helper method that does not use `argparse` at all, instead loading a yaml file and populating the
        dataclass types.

        Args:
            yaml_file (`str` or `os.PathLike`):
                File name of the yaml file to parse
            allow_extra_keys (`bool`, *optional*, defaults to `False`):
                Defaults to False. If False, will raise an exception if the json file contains keys that are not
                parsed.

        Returns:
            Tuple consisting of:

                - the dataclass instances in the same order as they were passed to the initializer.
        """
        outputs = self.parse_dict(yaml.safe_load(Path(yaml_file).read_text()), allow_extra_keys=allow_extra_keys)
        return tuple(outputs)
    


