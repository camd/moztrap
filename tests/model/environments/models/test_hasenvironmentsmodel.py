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
Tests for ``HasEnvironmentsModel``.

"""
from tests import case



class HasEnvironmentsModelTest(case.TestCase):
    """Tests for HasEnvironmentsModel base class."""
    @property
    def model_class(self):
        """The abstract model class under test."""
        from cc.model.environments.models import HasEnvironmentsModel
        return HasEnvironmentsModel


    def test_parent(self):
        """parent property is None in base class."""
        t = self.model_class()
        self.assertIsNone(t.parent)


    def test_cascade_envs_to(self):
        """cascade_envs_to returns empty dict in base class."""
        self.assertEqual(self.model_class.cascade_envs_to([], True), {})
