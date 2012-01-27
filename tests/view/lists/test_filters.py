# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
Tests for queryset-filtering.

"""
from mock import Mock

from django.template.response import TemplateResponse
from django.test import RequestFactory
from django.utils.datastructures import MultiValueDict
from django.utils.unittest import TestCase



class FiltersTestCase(TestCase):
    """A test case for testing classes in the cc.view.lists.filters module."""
    @property
    def filters(self):
        """The module under test."""
        from cc.view.lists import filters
        return filters



class DecoratorTest(FiltersTestCase):
    """Tests for ``filter`` decorator."""
    @property
    def filter(self):
        """The decorator factory under test."""
        return self.filters.filter


    def on_response(self, response, decorator=None, request=None):
        """Apply given decorator to dummy view, return given response."""
        decorator = decorator or self.filter("ctx_name")
        request = request or RequestFactory().get("/")

        @decorator
        def view(request):
            return response

        return view(request)


    def on_template_response(self, context, **kwargs):
        """Run TemplateResponse with given context through decorated view."""
        request = kwargs.setdefault("request", RequestFactory().get("/"))

        res = TemplateResponse(request, "some/template.html", context)

        return self.on_response(res, **kwargs)


    def test_returns_non_template_response(self):
        """Returns a non-TemplateResponse unmodified, without error."""
        res = self.on_response("blah")

        self.assertEqual(res, "blah")


    def test_uses_wraps(self):
        """Preserves docstring and name of original view func."""
        @self.filter("ctx_name")
        def myview(request, some_id):
            """docstring"""

        self.assertEqual(myview.func_name, "myview")
        self.assertEqual(myview.func_doc, "docstring")


    def test_passes_on_args(self):
        """Arguments are passed on to original view func."""
        record = []

        @self.filter("ctx_name")
        def myview(request, *args, **kwargs):
            record.extend([args, kwargs])

        myview(RequestFactory().get("/"), "a", b=2)

        self.assertEqual(record, [("a",), {"b": 2}])


    def test_filterset(self):
        """Constructs FilterSet instance and places it in template context."""
        response = self.on_template_response(
            {"ctx_name": Mock()},
            decorator=self.filter("ctx_name", [self.filters.Filter("name")]),
            )

        fs = response.context_data["filters"]
        self.assertIsInstance(fs, self.filters.FilterSet)
        self.assertEqual(list(fs)[0].name, "name")


    def test_filterset_subclass(self):
        """Accepts a FilterSet subclass to use in ``filterset`` argument."""
        class MyFilterSet(self.filters.FilterSet):
            filters = [self.filters.Filter("name")]

        response = self.on_template_response(
            {"ctx_name": Mock()},
            decorator=self.filter("ctx_name", filterset=MyFilterSet),
            )

        fs = response.context_data["filters"]
        self.assertIsInstance(fs, MyFilterSet)
        self.assertEqual(list(fs)[0].name, "name")


    def test_filters_qs(self):
        """Finds queryset in context; runs it through filterset ``filter``."""
        class MockFilterSet(self.filters.FilterSet):
            def filter(self, queryset):
                # simple annotation so we know it passed through here.
                queryset.filtered = True
                return queryset

        response = self.on_template_response({"ctx_name": Mock()})

        qs = response.context_data["ctx_name"]
        self.assertTrue(qs.filtered)



class FilterSetTest(FiltersTestCase):
    """Tests for FilterSet."""
    def test_data(self):
        """
        ``self.data`` is plain dict of lists from given MultiValueDict.

        Only keys beginning with the prefix "filter-" are included, and the
        prefix is stripped from the key.

        """
        fs = self.filters.FilterSet(
            MultiValueDict(
                {
                    "other": ["a", "b"],
                    "filter-one": ["foo"],
                    "filter-two": ["bar", "baz"]
                    }
                )
            )

        self.assertEqual(fs.data, {"one": ["foo"], "two": ["bar", "baz"]})


    def test_prefix_override(self):
        """'filter-' prefix can be changed via 'filter' kwarg."""
        fs = self.filters.FilterSet(
            MultiValueDict(
                {
                    "other": ["a", "b"],
                    "foo:one": ["foo"],
                    "foo:two": ["bar", "baz"]
                    }
                ),
            prefix="foo:"
            )

        self.assertEqual(fs.data, {"one": ["foo"], "two": ["bar", "baz"]})


    def test_boundfilters(self):
        """``self.boundfilters`` has a BoundFilter for each given Filter."""
        flt = self.filters.Filter("name")
        fs = self.filters.FilterSet(MultiValueDict(), [flt])

        self.assertEqual(len(fs.boundfilters), 1)
        self.assertIsInstance(fs.boundfilters[0], self.filters.BoundFilter)
        self.assertIs(fs.boundfilters[0].name, "name")


    def test_class_filters(self):
        """Subclasses can provide filters list as class attribute."""
        class MyFilterSet(self.filters.FilterSet):
            filters = [
                self.filters.Filter("name")
                ]

        fs = MyFilterSet(MultiValueDict())

        self.assertEqual(len(fs.boundfilters), 1)
        self.assertEqual(fs.boundfilters[0].name, "name")


    def test_instantiation_filters_extend_class_filters(self):
        """Filters given at instantiation extend class-attr filters."""
        class MyFilterSet(self.filters.FilterSet):
            filters = [
                self.filters.Filter("one")
                ]

        fs = MyFilterSet(MultiValueDict(), [self.filters.Filter("two")])

        self.assertEqual([bf.name for bf in fs.boundfilters], ["one", "two"])


    def test_extend_doesnt_alter_class_attr(self):
        """Providing filters at instantiation doesn't alter the class attr."""
        class MyFilterSet(self.filters.FilterSet):
            filters = [
                self.filters.Filter("one")
                ]

        MyFilterSet(MultiValueDict(), [self.filters.Filter("two")])
        fs = MyFilterSet(MultiValueDict())

        self.assertEqual(len(fs.boundfilters), 1)


    def test_iteration_yields_boundfilters(self):
        """Iterating over a FilterSet yields its BoundFilters."""
        fs = self.filters.FilterSet(
            MultiValueDict(), [self.filters.Filter("name")])

        self.assertEqual(list(fs), fs.boundfilters)


    def test_len_is_number_of_boundfilters(self):
        """Length of a FilterSet is its number of BoundFilters."""
        class MyFilterSet(self.filters.FilterSet):
            filters = [
                self.filters.Filter("one")
                ]

        fs = MyFilterSet(MultiValueDict(), [self.filters.Filter("two")])

        self.assertEqual(len(fs), 2)


    def test_filter(self):
        """filter method sends queryset through all filter's filter methods."""
        class MockFilter(self.filters.Filter):
            def filter(self, queryset, values):
                # simple annotation so we can test the qs passed through here
                setattr(queryset, self.name, values)
                return queryset

        fs = self.filters.FilterSet(
            MultiValueDict({"filter-one": ["1"], "filter-two": ["2", "3"]}),
            [MockFilter("one"), MockFilter("two")],
            )
        qs = Mock()

        qs = fs.filter(qs)

        self.assertEqual(qs.one, ["1"])
        self.assertEqual(qs.two, ["2", "3"])



class BoundFilterTest(FiltersTestCase):
    """Tests for BoundFilter."""
    def test_values(self):
        """values is list of valid values (as returned by Filter)."""
        bf = self.filters.BoundFilter(
            self.filters.ChoicesFilter(
                "name", choices=[("1", "one"), ("2", "two")]),
            {"name": ["1", "bad"], "other": ["irrelevant"]}
            )

        self.assertEqual(bf.values, ["1"])


    def test_iteration(self):
        """Iteration returns FilterOptions with value, label, selected attrs."""
        bf = self.filters.BoundFilter(
            self.filters.ChoicesFilter(
                "name", choices=[("1", "one"), ("2", "two")]),
            {"name": ["1", "bad"], "other": ["irrelevant"]}
            )

        self.assertEqual(
            [(o.value, o.label, o.selected) for o in bf],
            [("1", "one", True), ("2", "two", False)])


    def test_filter(self):
        """Filtering just passes through queryset and values to filter."""
        class MyChoicesFilter(self.filters.ChoicesFilter):
            def filter(self, queryset, values):
                # simple annotation so we can tell qs went through here
                queryset.values = values
                return queryset

        bf = self.filters.BoundFilter(
            MyChoicesFilter(
                "name", choices=[("1", "one"), ("2", "two")]),
            {"name": ["1", "bad"], "other": ["irrelevant"]}
            )

        qs = bf.filter(Mock())

        self.assertEqual(qs.values, ["1"])


    def test_passthrough(self):
        """cls, name, and key properties are just pass-through to filter."""
        flt = self.filters.Filter("name", key="key")
        flt.cls = "foobar"

        bf = self.filters.BoundFilter(flt, {})

        self.assertEqual(bf.cls, "foobar")
        self.assertEqual(bf.name, "name")
        self.assertEqual(bf.key, "key")


    def test_len(self):
        """Length is number of options."""
        bf = self.filters.BoundFilter(
            self.filters.ChoicesFilter(
                "name", choices=[("1", "one"), ("2", "two")]),
            {}
            )

        self.assertEqual(len(bf), 2)



class FilterTest(FiltersTestCase):
    """Tests for base Filter class."""
    def test_name(self):
        """Name attribute is from mandatory first instantiation argument."""
        f = self.filters.Filter("name")

        self.assertEqual(f.name, "name")


    def test_lookup(self):
        """Lookup attribute is optional keyword argument."""
        f = self.filters.Filter("name", lookup="lookup")

        self.assertEqual(f.lookup, "lookup")


    def test_lookup_defaults_to_name(self):
        """Lookup attribute defaults to name."""
        f = self.filters.Filter("name")

        self.assertEqual(f.lookup, "name")


    def test_key(self):
        """Key attribute is optional keyword argument."""
        f = self.filters.Filter("name", key="key")

        self.assertEqual(f.key, "key")


    def test_key_defaults_to_name(self):
        """Key attribute defaults to name."""
        f = self.filters.Filter("name")

        self.assertEqual(f.key, "name")


    def test_filter(self):
        """Filters queryset so ``self.lookup`` field value is in ``values``."""
        f = self.filters.Filter("name", lookup="lookup")

        qs = Mock()
        qs2 = f.filter(qs, ["1", "2"])

        qs.filter.assert_called_with(lookup__in=["1", "2"])
        qs.filter.return_value.distinct.assert_called_with()
        self.assertEqual(qs2, qs.filter.return_value.distinct.return_value)


    def test_options(self):
        """Base Filter has no options."""
        f = self.filters.Filter("name")

        self.assertEqual(f.options(["yo"]), [])


    def test_values(self):
        """Pulls ``self.key`` values from given data."""
        f = self.filters.Filter("name", key="key")

        self.assertEqual(f.values({"key": ["one"], "name": ["two"]}), ["one"])



class BaseChoicesFilterTest(FiltersTestCase):
    """Tests for BaseChoicesFilter."""
    def test_get_choices(self):
        """Default get_choices returns no choices; should be overridden."""
        f = self.filters.BaseChoicesFilter("name")

        self.assertEqual(f.get_choices(), [])


    def test_options(self):
        """Options are fixed to choices, regardless of current filter values."""
        f = self.filters.BaseChoicesFilter("name")
        f.get_choices = lambda: [("1", "one")]

        self.assertEqual(f.options(["values"]), [("1", "one")])


    def test_values(self):
        """Values are constrained to valid choices."""
        f = self.filters.BaseChoicesFilter("name")
        f.get_choices = lambda: [("1", "one")]

        self.assertEqual(f.values({"name": ["1", "2"]}), ["1"])



class ChoicesFilterTest(FiltersTestCase):
    """Tests for ChoicesFilter."""
    def test_choices(self):
        """Choices can be passed in as a keyword argument at instantiation."""
        f = self.filters.ChoicesFilter("name", choices=[("1", "one")])

        self.assertEqual(f.get_choices(), [("1", "one")])



class ModelFilterTest(FiltersTestCase):
    """Tests for ModelFilter."""
    @property
    def queryset(self):
        """Mock "queryset" of instances with numeric id and unicode repr."""
        o1 = Mock()
        o1.id = 1
        o1.__unicode__ = lambda self: "one"
        o2 = Mock()
        o2.id = 2
        o2.__unicode__ = lambda self: "two"
        qs = Mock()
        qs.__iter__ = lambda self: iter([o1, o2])
        qs.all.return_value = qs
        return qs


    def test_choices(self):
        """Choices are passed in as an iterable of model instances."""
        f = self.filters.ModelFilter("name", queryset=self.queryset)

        self.assertEqual(f.get_choices(), [(1, "one"), (2, "two")])


    def test_custom_labels(self):
        """Callable can be passed in to customize labeling of instances."""
        f = self.filters.ModelFilter(
            "name",
            queryset=self.queryset,
            label=lambda o: u"option {0}".format(o)
            )

        self.assertEqual(
            f.get_choices(), [(1, "option one"), (2, "option two")])


    def test_values_coerced(self):
        """
        Values are coerced to integers before being matched against options.

        If coercion fails, value is ignored.

        """
        f = self.filters.ModelFilter("name", queryset=self.queryset)

        self.assertEqual(f.values({"name": ["1", "foo", None]}), [1])



class KeywordExactFilterTest(FiltersTestCase):
    """Tests for KeywordExactFilter."""
    def test_options(self):
        """Available options are the current filter values."""
        f = self.filters.KeywordExactFilter("name")

        self.assertEqual(
            f.options(["one", "two"]), [("one", "one"), ("two", "two")])



class KeywordFilterTest(FiltersTestCase):
    """Tests for KeywordFilter."""
    def test_filter(self):
        """Filters queryset by 'contains' all values."""
        f = self.filters.KeywordFilter("name")

        qs = Mock()
        qs2 = f.filter(qs, ["one", "two"])

        qs.filter.assert_called_with(name__icontains="one")
        qs.filter.return_value.filter.assert_called_with(name__icontains="two")
        qs.filter.return_value.filter.return_value.distinct.assert_called_with()
        self.assertIs(
            qs2,
            qs.filter.return_value.filter.return_value.distinct.return_value)


    def test_filter_doesnt_touch_queryset_if_no_values(self):
        """Doesn't call .distinct() or .filter() unless actually filtered."""
        f = self.filters.KeywordFilter("name")

        qs = Mock()
        f.filter(qs, [])

        self.assertEqual(qs.filter.call_count, 0)
        self.assertEqual(qs.distinct.call_count, 0)