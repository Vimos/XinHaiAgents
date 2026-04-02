"""
Copyright (c) CAS-SIAT-XinHai.
Licensed under the CC0-1.0 license.

XinHai stands for [Sea of Minds].

Authors: Vimos Tan
"""
from enum import Enum

from pydantic import BaseModel


class XinHaiArenaAgentTypes(str, Enum):
    SIMPLE = 'simple'
    PROXY = 'proxy'
    VERIFY_AGENT = 'verify_agent'
    OCR = 'ocr'
    MLLM = 'mllm'


class XinHaiArenaEnvironmentTypes(str, Enum):
    SIMPLE = 'simple'
    AGENCY = 'agency'
    OCRAGENCY = 'ocragency'


class XinHaiArenaLLMConfig(BaseModel):
    model: str
    api_key: str = "EMPTY"
    api_base: str = None
    do_sample: bool = False
    temperature: float = 1
    top_p: float = 1
    # max_new_tokens: int =
    # num_return_sequences: int = 1

    @classmethod
    def from_config(cls, llm_config, controller_address):
        from xinhai.config import args
        
        # 如果 llm_config 是字符串（如 'gpt-4o'），转换为字典
        if isinstance(llm_config, str):
            llm_config = {
                'model': llm_config,
                'api_base': getattr(args, 'api_base', f'{controller_address}/v1'),
                'api_key': getattr(args, 'api_key', 'EMPTY')
            }
        # 如果是字典，补充缺失的配置
        elif isinstance(llm_config, dict):
            if 'api_base' not in llm_config:
                llm_config['api_base'] = getattr(args, 'api_base', f'{controller_address}/v1')
            if 'api_key' not in llm_config:
                llm_config['api_key'] = getattr(args, 'api_key', 'EMPTY')
        
        return cls(**llm_config)
