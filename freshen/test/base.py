#-*- coding: utf8 -*-

import traceback
import sys

from freshen.context import ftc, scc
from freshen.stepregistry import UndefinedStepImpl

try:
    from django.test import TestCase
except ImportError:
    from unittest import TestCase


class ExceptionWrapper(Exception):

    def __init__(self, e, step, discard_frames=0):
        e = list(e)
        while discard_frames:
            e[2] = e[2].tb_next
            discard_frames -= 1
        self.e = e
        self.step = step

    def __str__(self):
        return "".join(traceback.format_exception(*self.e))


class FeatureSuite(object):

    def setUp(self):
        #log.debug("Clearing feature context")
        ftc.clear()


class FreshenTestCase(TestCase):

    def __init__(self, step_runner, step_registry, feature, scenario, feature_suite):
        self.feature = feature
        self.scenario = scenario
        self.context = feature_suite
        self.step_registry = step_registry
        self.step_runner = step_runner

        self.description = feature.name + ": " + scenario.name
        self._cleanups = []

    def setUp(self):
        #log.debug("Clearing scenario context")
        scc.clear()
        if scc.fixtures:
            self.fixtures = scc.fixtures
        if hasattr(self, '_pre_setup'):
            self._pre_setup()
        super(FreshenTestCase, self).setUp()

    def runAfterStepHooks(self):
        for hook_impl in reversed(self.step_registry.get_hooks('after_step', self.scenario.get_tags())):
            hook_impl.run(self.scenario)

    def runStep(self, step, discard_frames=0):
        try:
            self.last_step = step
            return self.step_runner.run_step(step)
        except (AssertionError, UndefinedStepImpl, ExceptionWrapper):
            raise
        except:
            raise ExceptionWrapper(sys.exc_info(), step, discard_frames)
        self.runAfterStepHooks()

    def runScenario(self):
        raise NotImplementedError('Must be implemented by subclasses')
        
    def tearDown(self):
        super(FreshenTestCase, self).tearDown()
        if hasattr(self, '_post_teardown'):
            self._post_teardown()
