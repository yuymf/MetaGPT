# -*- coding: utf-8 -*-
# @Date    : 2023/9/23 15:44
# @Author  : stellahong (stellahong@fuzhi.ai)
# @Desc    :
from metagpt.logs import logger
from metagpt.actions import Action
from metagpt.utils.minecraft import parse_action_response


class GenerateActionCode(Action):
    """
    Action class for generating action code.
    Refer to the code in the voyager/agents/action.py for implementation details.
    """

    def __init__(self, name="", context=None, llm=None):
        super().__init__(name, context, llm)
        self.llm.model = "gpt-4"

    async def generate_code(self, human_msg, system_msg=[]):
        """
        Generate action code logic.

        Implement the logic for generating action code here.
        """
        # logger.info(f"human_msg {human_msg}, system_msg {system_msg}")
        rsp = await self._aask(prompt=human_msg, system_msgs=system_msg)
        parsed_result = parse_action_response(rsp)
        # logger.info(f"parsed_result is HERE: {parsed_result}")

        try:
            return (
                parsed_result["program_code"],
                parsed_result["program_code"] + "\n" + parsed_result["exec_code"],
                parsed_result["program_name"],
            )
        except:
            logger.error(f"Failed to parse response: {parsed_result}")
            return None, None, None # TODO: midify to "", "", ""

    async def run(self, human_msg, system_msg, *args, **kwargs):
        logger.info(f"run {self.__repr__()}")
        # Generate action code.
        program_code, generated_code, program_name = await self.generate_code(
            human_msg=human_msg, system_msg=system_msg
        )

        # Return the generated code.
        return program_code, generated_code, program_name
