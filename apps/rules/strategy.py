# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class RuleStrategy():
    REQUIRED_DATA = {}  # DATA REQUERIDA PARA CREAR LAS REGLAS,
    # NAME, REQUIRED, TYPE, CHILDS (ITERA)

    def __init__(self, rule):
        self.rule = rule

    def check_rule(self, from_date):
        events = self.__get_events(from_date)
        for event in events:
            self.__apply_rule(event)

    def __get_events(self, from_date):
        # BUSCA LO QUE CORRESPONDA
        raise Exception("Not Implemented")

    def __apply_rule(self, event):
        # HACER LO QUE CORRESPONDA Y GENERAR RULE INSTANCE
        # GUARDAR EN DESCRIPTION LO QUE SE HIZO (COMO LOG)
        raise Exception("Not Implemented")


class RuleStrategyDefault(RuleStrategy):
    REQUIRED_DATA = {}

    def __get_events(selg, from_date):
        pass

    def __apply_rule(self, event):
        pass


STRATEGY_CLASS = {
    'DEF': RuleStrategyDefault
}
