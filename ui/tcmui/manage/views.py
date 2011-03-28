from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..core import sort
from ..products.models import ProductList
from ..testexecution.models import TestCycleList, TestRunList
from ..testcases.models import TestCaseVersionList
from ..users.decorators import login_redirect
from ..users.models import UserList

from . import decorators as dec
from .forms import TestCycleForm, TestCaseForm



def home(request):
    return redirect("manage_testcycles")



@login_redirect
@dec.actions(TestCycleList, ["activate", "deactivate", "delete", "clone"])
@dec.filter("cycles")
@dec.paginate("cycles")
@dec.sort("cycles")
def testcycles(request):
    return TemplateResponse(
        request,
        "manage/testcycle/cycles.html",
        {"cycles": TestCycleList.ours(auth=request.auth)}
        )



@login_redirect
def add_testcycle(request):
    form = TestCycleForm(
        request.POST or None,
        product_choices=ProductList.ours(auth=request.auth),
        team_choices=UserList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        cycle = form.save()
        messages.success(
            request,
            "The test cycle '%s' has been created."  % cycle.name)
        return redirect("manage_testcycles")
    return TemplateResponse(
        request,
        "manage/testcycle/add_cycle.html",
        {"form": form}
        )



@login_redirect
@dec.actions(TestRunList, ["delete"])
def edit_testcycle(request, cycle_id):
    cycle = TestCycleList.get_by_id(cycle_id, auth=request.auth)
    form = TestCycleForm(
        request.POST or None,
        instance=cycle,
        product_choices=ProductList.ours(auth=request.auth),
        team_choices=UserList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        cycle = form.save()
        messages.success(
            request,
            "The test cycle '%s' has been saved."  % cycle.name)
        return redirect("manage_testcycles")

    testruns = TestRunList.ours(auth=request.auth).filter(
        testCycle=cycle.id).sort(
        *sort.from_request(request))

    return TemplateResponse(
        request,
        "manage/testcycle/edit_cycle.html",
        {
            "form": form,
            "cycle": cycle,
            "testruns": testruns,
            }
        )



@login_redirect
@dec.actions(
    TestCaseVersionList,
    ["approve", "reject", "activate", "deactivate", "delete", "clone"])
@dec.filter("cases")
@dec.paginate("cases")
@dec.sort("cases")
def testcases(request):
    return TemplateResponse(
        request,
        "manage/testcase/cases.html",
        {"cases": TestCaseVersionList.ours(
                url="testcases/latestversions", auth=request.auth)}
        )



@login_redirect
def add_testcase(request):
    form = TestCaseForm(
        request.POST or None,
        product_choices=ProductList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST":
        if form.is_valid():
            testcase = form.save()
            messages.success(
                request,
                "The test case '%s' has been created."  % testcase.name)
            return redirect("manage_testcases")

    return TemplateResponse(
        request,
        "manage/testcase/add_case.html",
        {"form": form })



@login_redirect
def edit_testcase(request, case_id):
    case = TestCaseVersionList.get_by_id(case_id, auth=request.auth)
    form = TestCaseForm(
        request.POST or None,
        instance=case,
        product_choices=ProductList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        case = form.save()
        messages.success(
            request,
            "The test case '%s' has been saved."  % case.name)
        return redirect("manage_testcases")

    return TemplateResponse(
        request,
        "manage/testcase/edit_case.html",
        {
            "form": form,
            "case": case,
            }
        )