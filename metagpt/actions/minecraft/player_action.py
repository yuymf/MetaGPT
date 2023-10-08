# -*- coding: utf-8 -*-
# @Date    : 2023/9/23 17:06
# @Author  : stellahong (stellahong@fuzhi.ai)
# @Desc    :
from metagpt.actions import Action
from metagpt.logs import logger
class PlayerActions(Action):
    def __init__(self, name="", context=None, llm=None):
        super().__init__(name, context, llm)
        self.qa_cache = {}
        self.retrieval_top_k = 5
        self.vectordb = None
        self.qa_cache_questions_vectordb = None

    def set_vectordb(self, vectordb):
        logger.debug("vectordb init")
        self.vectordb = vectordb

    def set_qa_cache(self, qa_cache):
        logger.debug("set_qa_cache init")
        self.qa_cache = qa_cache

    def set_qa_cache_questions_vectordb(self, qa_cache_questions_vectordb):
        logger.debug("set_qa_cache_questions_vectordb init")
        self.qa_cache_questions_vectordb = qa_cache_questions_vectordb

    """Minecraft player info without any implementation details"""
    async def run(self, *args, **kwargs):
        raise NotImplementedError