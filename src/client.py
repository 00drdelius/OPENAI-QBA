# necessary import
from pathlib import Path
root_dir=Path(__file__).parent.parent
import sys
sys.path.append(str(root_dir))
# print(sys.path)

# config import
parent_dir=Path(__file__).parent
# print(CONFIGS)

# third-party import
from typing import Union
from .datastructure import construct_gptDS
from functools import partial
from rich.console import Console
from openai import OpenAI
console=Console(style="#F7FF00") # bright yellow
error_console=Console(style="#FF0B03")

class BaseClient:
    """Base Client. To fit uncertain model apis required in the future."""
    def construct_msgs(self,prompts:Union[str,list]):
        """
        Construct msgs sent to gpt models.\n
        system prompt must be set if passed in a list[str]
        Multiround msgs construction is automatically supported.

        Args:
        ---
        prompts: format supported: pure string, list[str], list[dict{"role":"..","content":".."}]
        """
        msgs:list=[]
        def role():
            system=True
            li=["system","user","assistant"]
            for i in li:
                if i=="system":
                    if not system:
                        continue
                    system=False
                yield i
        gen_role=role()
        if isinstance(prompts,list):
            # generate prompts format: [{user},{assistant}]
            if isinstance(prompts[0],dict):
                assert "role" in prompts[-1].keys() and "content" in prompts[-1].keys(), "dict format in list prompts follows the dict in massages format in openai"
                assert prompts[-1]['role']=='user', "if you already have dicts in prompts list, role=user as key must be contained!"
                for prompt in prompts:
                    msgs.append(prompt)
            elif isinstance(prompts[0],str):
                for prompt in prompts:
                    msgs.append({"role":next(gen_role),"content":prompt})
            else:
                raise Exception("prompts passed in only supports format list[str] or pure str or list[dict[str,str]]")
        elif isinstance(prompts,str):
            # system must be True, so system prompt has to set a default.
            default_sys = {"role":"system","content":"You are a helpful assistant."}
            msgs.extend([default_sys,{"role":"user","content":prompts}])
        else:
            raise Exception("prompts passed in only supports format list[str] or pure str or list[dict[str,str]]")
        ### debug area
        # console.print("msgs to send:\n"+str(msgs))
        ### debug area
        return msgs

    def chatapi(self):
        "abstract method| Must to implemented by subclass| To "
    
    def embdapi(self):
        "abstract method| Must to implemented by subclass|"

class OpenaiClient(BaseClient):
    """
    Args:
    ---
    api_key: openai api key
    api_base: openai api base
    kwargs: extra kwargs used in OpenAI: timeout,max_retries,http_client,etc.
    """
    def __init__(self,api_key:str,api_base:str,**kwargs) -> None:
        self.client=OpenAI(
                api_key=api_key,
                base_url=api_base,
                # http_client=self.proxy_client,
                **kwargs
            )
    
    @property
    def models_available(self):
        ret_li={}
        li=self.client.models.list()
        for i in li:
            if i.owned_by not in ret_li.keys():
                ret_li[i.owned_by]=[]
            ret_li[i.owned_by].append(i.id)
        return ret_li

    def __sync_gpt_chatapi(
            self,
            prompt: str | list[str] | list[dict[str,str]],
            model="gpt-3.5-turbo-1106",
            temperature:int=0.3,
            json_mode:bool=False,
            stream:bool=True,
            **kwargs
    ):
        """
        gpt api function

        Args:
        ---
        prompts: format supported: pure string, list[str], list[dict{"role":"..","content":".."}],
        sys prompt is automatically added in the first place.
        retries: request retries time supported
        
        **others: please refer to openai api documentation: https://platform.openai.com/docs/api-reference/chat/create
        """
        retries=kwargs.pop("retries",0)
        response_format=(
            {"type":"json_object"}
            if json_mode else {"type":"text"}
        )
        chat_completion_freeze = partial(
            self.client.chat.completions.create,
            response_format=response_format,
            model=model,
            temperature=temperature,
            stream=stream,
            **kwargs
        )
        while retries>=0:
            msgs = self.construct_msgs(prompts=prompt)
            try:
                chat_completion=chat_completion_freeze(messages=msgs)
            except Exception as exc:
                error_console.print(f"openai requestError:{exc}. Retry...",style="#FF7F7F")
                if retries==0:
                    error_console.print(
                        "#**********BREAKING ERROR**************\n"
                        "#request reaches max retries.\n"
                       f"#Return gpt output: {exc}\n"
                        "#Auto breaking.."
                        "#**********BREAKING ERROR**************"
                    )
                    error_completion=construct_gptDS(stream=stream,response=str(exc),model=model)
                    if stream:
                        yield 
                    else:
                        yield error_completion
                retries-=1
                continue
            else:
                console.print("GPT return 200.")
                break
        if stream:
            for chunk in chat_completion:
                yield chunk.choices[0].delta.content
        else:
            yield chat_completion

    def chatapi(
            self,
            prompt: str | list[str] | list[dict[str,str]],
            count_tokens=False,
            **kwargs
    ):
        """
        Please check more args supported in function __sync_gpt_chatapi.
        
        Args:
        ---
        prompts: format supported: pure string, list[str], list[dict{"role":"..","content":".."}],
        sys prompt is automatically added in the first place.
        count_tokens: set to True if you want to count tokens consumed.
        Pls note openai does not return prompt_tokens consumed if stream=True
        
        Returns:
        ---
        output:{
            "content": text content,
            "usage": {
                "prompt_tokens": ...,
                "completion_tokens": ...,
                "total_tokens": ...
            } if count_tokens
        }
        """
        kwargs['timeout']=(
            300 if not "timeout" in kwargs.keys() else 
            kwargs['timeout']
        )
        output={}
        text_output=""
        if "stream" in kwargs.keys() and kwargs['stream']:
            usage=0
            for chunk in self.__sync_gpt_chatapi(prompt=prompt,**kwargs):
                if chunk:
                    usage+=1
                    text_output+=chunk
            if count_tokens:
                output['usage']={
                    "completion_tokens": usage,
                    "prompt_tokens": float("-inf"),
                    "total_tokens": float("-inf")
                }
        else:
            chat_completion=next(self.__sync_gpt_chatapi(prompt=prompt,**kwargs))
            text_output=chat_completion.choices[0].message.content
            if count_tokens:
                output['usage']=chat_completion.usage
        output['content']=text_output
        return output

    def embdapi(
            self,
            prompt:str,
            count_tokens=False,
            model="text-embedding-ada-002",
            encoding_format="float"
    ):
        """
        openai embedding api function
        """
        output={}
        resp = self.client.embeddings.create(
            input=prompt,
            model=model,
            encoding_format=encoding_format
        )
        output['embedding']=resp.data[0].embedding
        if count_tokens:output['usage']=resp.usage
        return output

    @staticmethod
    def main(args):
        api_key=args.api_key
        api_base=args.api_base
        client=OpenaiClient(
            api_key=api_key,
            api_base=api_base
        )
        prompt1="Hello GPT. How nice to see you today."
        prompt2="你说得对，但是原神是一款好游戏。"
        sys_p="You are a senior translator in Chinese-English translation. I now want you to translate what I give you."
        
        # test pure string, stream=True, count_tokens=True
        # output1=client.gpt_chatapi(prompt1,count_tokens=True,stream=True,json_mode=False)
        # print(f"output1: {output1}")

        # test list[str], stream=False, count_tokens=True
        # output2=client.gpt_chatapi([sys_p,prompt2],count_tokens=True,stream=False,json_mode=False)
        # print(f"output2: {output2}")

        # test embedding
        # embd = client.gpt_embdapi("Bonjour, il fait beau aujourd’hui",count_tokens=True)
        # print(f"embd length: {len(embd['embedding'])}")
        # print(f"embd cost: {embd['usage']}")

        console.print(f"models available:{client.models_available}")

if __name__=='__main__':
    OpenaiClient.main()