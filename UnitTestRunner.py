#!/usr/bin/python3

import unittest

from ProductionLineScene import TestProductionLineScene
from ProductionLine import TestProductionLine
from Processes import TestEveDB
from ProcessesFilterModel import TestProcessesFilterModel

from PyQt5.QtWidgets import QApplication
import sys
app = QApplication(sys.argv)

unittest.main()