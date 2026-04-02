"""Tests for the XAML binder."""

from pywinui_runtime.binder import ViewProxy, _extract_xnames, bind_xaml


class FakeElement:
    """Fake WinUI element for testing."""

    def __init__(self, name: str):
        self._name = name

    def FindName(self, name: str):
        if name == self._name:
            return self
        return None


def test_extract_xnames():
    xaml = '''
    <StackPanel>
        <Button x:Name="btn1" Content="OK"/>
        <TextBlock x:Name="label1" Text="Hello"/>
    </StackPanel>
    '''
    names = _extract_xnames(xaml)
    assert names == ["btn1", "label1"]


def test_extract_xnames_empty():
    xaml = "<StackPanel><Button Content='OK'/></StackPanel>"
    names = _extract_xnames(xaml)
    assert names == []


def test_view_proxy_attribute_access():
    root = object()
    el = FakeElement("myBtn")
    proxy = ViewProxy(root, {"myBtn": el})
    assert proxy.myBtn is el
    assert proxy.root is root


def test_view_proxy_missing_attr():
    proxy = ViewProxy(object(), {})
    try:
        _ = proxy.nonexistent
        assert False, "Should have raised"
    except AttributeError:
        pass


def test_bind_xaml():
    xaml = '<Window><Button x:Name="okBtn" /></Window>'

    class FakeRoot:
        def FindName(self, name):
            if name == "okBtn":
                return "the_button"
            return None

    view = bind_xaml(FakeRoot(), xaml)
    assert view.okBtn == "the_button"
