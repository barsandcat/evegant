#!/usr/bin/python3

import unittest

from LineScene import TestProductionLineScene
from Schemes import TestEveDB
from SchemesFilterModel import TestSchemesFilterModel
from Process import TestProcess
from Line import TestLine

from PyQt5.QtWidgets import QApplication
import sys
app = QApplication(sys.argv)

unittest.main()