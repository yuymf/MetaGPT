# -*- coding: utf-8 -*-
# @Date    : 2023/7/15 16:40
# @Author  : stellahong (stellahong@fuzhi.ai)
# @Desc    :
from functools import wraps
from importlib import import_module

from metagpt.actions import WritePRD
from metagpt.logs import logger
from metagpt.roles import Role
from tests.metagpt.actions.test_ui_design import UIDesign


def load_engine(func):
    """Decorator to load an engine by file name and engine name."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        file_name, engine_name = func(*args, **kwargs)
        engine_file = import_module(file_name, package="metagpt")
        ip_module_cls = getattr(engine_file, engine_name)
        try:
            engine = ip_module_cls()
        except:
            engine = None

        return engine

    return wrapper


class UI(Role):
    """Class representing the UI Role."""

    def __init__(
        self,
        name="Catherine",
        profile="UI Design",
        goal="Finish a workable and good User Interface design based on a product design",
        constraints="Give clear layout description and use standard icons to finish the design",
        skills=["SD"],
    ):
        super().__init__(name, profile, goal, constraints)
        self.load_skills(skills)
        self._init_actions([UIDesign])
        self._watch([WritePRD])

    @load_engine
    def load_sd_engine(self):
        """Load the SDEngine."""
        file_name = ".tools.sd_engine"
        engine_name = "SDEngine"
        return file_name, engine_name

    def load_skills(self, skills):
        """Load skills for the UI Role."""
        # todo: 添加其他出图engine
        for skill in skills:
            if skill == "SD":
                self.sd_engine = self.load_sd_engine()
                logger.info(f"load skill engine {self.sd_engine}")
