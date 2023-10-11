# -*- coding: utf-8 -*-
# @Date    : 2023/9/23 12:46
# @Author  : stellahong (stellahong@fuzhi.ai)
# @Desc    :
from metagpt.logs import logger
from metagpt.roles.minecraft.minecraft_base import Minecraft as Base
from metagpt.roles.minecraft.minecraft_base import agent_registry
from metagpt.schema import Message, HumanMessage, SystemMessage
from metagpt.actions.minecraft.manage_skills import (
    GenerateSkillDescription,
    RetrieveSkills,
    AddNewSkills,
)
from metagpt.actions.minecraft import GenerateActionCode
from metagpt.actions.minecraft.design_curriculumn import DesignCurriculum
from metagpt.utils.minecraft import load_prompt


@agent_registry.register("skill_manager")
class SkillManager(Base):
    def __init__(
        self,
        name: str = "John",
        profile: str = "Skills Management Specialist",
        goal: str = "To oversee and optimize the acquisition, development, and utilization of skills within the organization, ensuring workforce competence and efficiency.",
        constraints: str = "Resource allocation, training budgets, and alignment with organizational goals.",
    ) -> None:
        super().__init__(name, profile, goal, constraints)

        # Initialize actions specific to the SkillManager role
        self._init_actions([RetrieveSkills, GenerateSkillDescription, AddNewSkills])

        # Set events or actions the SkillManager should watch or be aware of
        self._watch(
            [DesignCurriculum, GenerateActionCode, RetrieveSkills, GenerateSkillDescription]
        )
        
        self.finish_state = len(self._actions)

    def encapsule_message(self, program_code, program_name, *args, **kwargs):
        system_msg = self.render_system_message(load_prompt("skill"))
        human_msg = self.render_human_message(
            program_code + "\n\n" + f"The main function is `{program_name}`."
        )
        return {"system_msg": [system_msg.content], "human_msg": human_msg.content}

    async def retrieve_skills(self, query, skills, *args, **kwargs):
        vectordb = self.game_memory.vectordb
        retrieve_skills = await RetrieveSkills().run(query, skills, vectordb)
        logger.info(f"Render Action Agent system message with {len(retrieve_skills)} skills")
        self.perform_game_info_callback(retrieve_skills, self.game_memory.update_retrieve_skills)
        return Message(content=f"{retrieve_skills}", instruct_content="retrieve_skills", 
                       role=self.profile, send_to=agent_registry.entries["action_developer"]()._setting.name)
        # return Message(
        #     content=f"{skills}", instruct_content="retrieve_skills", role=self.profile
        # )  # Unit test only

    async def generate_skill_descp(self, human_msg, system_msg, *args, **kwargs):
        program_name = self.game_memory.program_name
        desp = await GenerateSkillDescription().run(program_name, human_msg, system_msg)
        self.perform_game_info_callback(desp, self.game_memory.update_skill_desp)
        return Message(
            content=f"{desp}",
            instruct_content="generate_skill_descp",
            role=self.profile,
        )

    async def handle_add_new_skills(
        self, task, program_name, program_code, skills, *args, **kwargs
    ):
        if not self.game_memory.runtime_status:
            return Message(
            content="",
            instruct_content="handle_add_new_skills",
            role=self.profile,
        )
        
        skill_desp = self.game_memory.skill_desp
        vectordb = self.game_memory.vectordb
        new_skills_info = await AddNewSkills().run(
            task, program_name, program_code, skills, skill_desp, vectordb
        )
        self.perform_game_info_callback(new_skills_info, self.game_memory.append_skill)
        return Message(
            content=f"{new_skills_info}",
            instruct_content="handle_add_new_skills",
            role=self.profile,
        )

    async def _act(self) -> Message:
        todo = self._rc.todo
        logger.debug(f"Todo is {todo}")
        self.maintain_actions(todo)

        # 获取最新的游戏周边信息
        context = self.game_memory.context
        task = self.game_memory.current_task
        
        code = self.game_memory.code
        self.perform_game_info_callback(self.game_memory.event, self.game_memory.summarize_chatlog)
        event_summary = self.game_memory.event_summary
        program_code = self.game_memory.program_code

        program_name = self.game_memory.program_name
        skills = self.game_memory.skills

        # msg = self._rc.memory.get(k=1)[0]

        retrieve_skills_message_step1 = {"query": context, "skills": skills}
        logger.info(f"check query {context}")
        logger.info(f"check event summary {event_summary}")
        
        retrieve_skills_message_step2 = {"query": context + "\n\n" + event_summary, "skills": skills}

        generate_skill_message = self.encapsule_message(program_code, program_name)

        add_new_skills_message = {
            "task": task,
            "program_name": program_name,
            "program_code": program_code,
            "skills": skills,
        }

        handler_map = {
            DesignCurriculum: self.retrieve_skills,
            RetrieveSkills: self.retrieve_skills,
            GenerateSkillDescription: self.generate_skill_descp,
            AddNewSkills: self.handle_add_new_skills,
        }
        handler = handler_map.get(type(todo))
        if handler:
            if type(todo) == DesignCurriculum:
                logger.info(retrieve_skills_message_step1)
                msg = await handler(**retrieve_skills_message_step1)
            elif type(todo) == RetrieveSkills:
                logger.info(retrieve_skills_message_step2)
                msg = await handler(**retrieve_skills_message_step2)
            elif type(todo) == GenerateSkillDescription:
                msg = await handler(**generate_skill_message)
            else:
                msg = await handler(**add_new_skills_message)

            msg.cause_by = type(todo)
            msg.round_id = self.round_id
            self._publish_message(msg)
            return msg

        raise ValueError(f"Unknown todo type: {type(todo)}")
