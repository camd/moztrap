# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Tests for Result admin.

"""
from tests import case



class ResultAdminTest(case.admin.AdminTestCase):
    app_label = "execution"
    model_name = "result"


    def test_changelist(self):
        """Result changelist page loads without error, contains name."""
        self.F.ResultFactory.create(tester__username="sometester")

        self.get(self.changelist_url).mustcontain("sometester")


    def test_change_page(self):
        """Result change page loads without error, contains name."""
        r = self.F.ResultFactory.create(tester__username="sometester")

        self.get(self.change_url(r)).mustcontain("sometester")


    def test_change_page_stepresult(self):
        """Result change page includes StepResult inline."""
        sr = self.F.StepResultFactory.create(
            status="failed", result__status="started")

        self.get(self.change_url(sr.result)).mustcontain("failed")
