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
Admin config for library models.

"""
from django.contrib import admin

from ..ccadmin import CCModelAdmin, CCTabularInline, CCStackedInline
from . import models



class CaseVersionInline(CCStackedInline):
    model = models.CaseVersion
    extra = 0
    fieldsets = [
        (
            None, {
                "fields": [
                    "productversion",
                    ("name", "status"),
                    "exists",
                    "description",
                    ]
                }
            )
        ]



class CaseAttachmentInline(CCTabularInline):
    model = models.CaseAttachment
    extra = 0



class CaseStepInline(CCTabularInline):
    model = models.CaseStep
    extra = 0



class CaseTagInline(admin.TabularInline):
    model = models.CaseVersion.tags.through
    extra = 0


class SuiteCaseInline(CCTabularInline):
    model = models.SuiteCase
    extra = 0



class CaseVersionAdmin(CCModelAdmin):
    list_display = ["__unicode__", "productversion", "deleted_on"]
    list_filter = ["productversion"]
    inlines = [CaseStepInline, CaseAttachmentInline, CaseTagInline]
    filter_horizontal = ["environments"]
    fieldsets = [
        (
            None, {
                "fields": [
                    "productversion",
                    ("case", "name", "status"),
                    "description",
                    "environments",
                    ]
                }
            )
        ]



admin.site.register(models.Suite, CCModelAdmin)
admin.site.register(
    models.Case, CCModelAdmin, inlines=[CaseVersionInline, SuiteCaseInline])
admin.site.register(models.CaseVersion, CaseVersionAdmin)
