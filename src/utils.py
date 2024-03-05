import shortuuid
import tiktoken

def generate_uuid(uuid_list):
    uuid=""
    while uuid in uuid_list or uuid=="":
        uuid=shortuuid.uuid()
    return uuid

def give_uuids(data:dict):
    uuids=[]
    for i in data:
        i['uuid']=generate_uuid(uuids)
        uuids.append(i['uuid'])
    return data

def construct_prompts(args,value:dict):
    sys_prompt:str=args.sys_prompt
    user_prompt:str=args.user_prompt
    user_prompt.format(**value)
    return sys_prompt,user_prompt

def statistics(args):
    pass

def estimator(args):
    pass

