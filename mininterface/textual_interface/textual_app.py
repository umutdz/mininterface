from typing import TYPE_CHECKING
from textual import events
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import (
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    Static,
    Rule
)


from .widgets import Changeable

from ..form_dict import formdict_to_widgetdict

from ..auxiliary import flatten

if TYPE_CHECKING:
    from .textual_adaptor import TextualAdaptor

WidgetList = list[Widget | Changeable]


class TextualApp(App[bool | None]):
    # BINDINGS = [ These are being ignored in the input fields, hence we use on_key
    #     ("up", "go_up", "Go up"),
    #     ("down", "go_up", "Go down"),
    # ]

    DEFAULT_CSS = """
    ImageViewer {
        height: 20;
    }

    FilePickerInput {
        layout: horizontal;
        height: auto;
        margin: 1;
    }

    FilePickerInput Input {
        width: 80%;
    }

    FilePickerInput Button {
        width: 20%;
        margin-left: 1;
    }
    """
    """ Limit layout image size """

    def __init__(self, adaptor: "TextualAdaptor", submit: str | bool = True):
        super().__init__()
        self.title = adaptor.facet._title
        self.widgets: WidgetList = []
        self.focusable: WidgetList = []
        """ A subset of self.widgets"""
        self.focused_i: int = 0
        self.adaptor = adaptor
        self.output = Static("")
        self.submit = submit

        # Form confirmation
        # enter w/o priority is still consumed by input fields (and recaught by on_key)
        if submit:
            self.bind("Enter", "confirm", description=submit if isinstance(submit, str) else "Ok")
        self.bind("escape", "exit", description="Cancel")

    def compose(self) -> ComposeResult:
        # prepare widgets
        # since textual 1.0.0 we have to build widgets not earlier than the context app is ready
        self.widgets = list(flatten(formdict_to_widgetdict(
            self.adaptor.facet._form, self.adaptor.widgetize), include_keys=self.adaptor.header))

        # there are multiple sections in the list, <hr>ed by Rule elements. However, the first takes much space.
        if len(self.widgets) and isinstance(self.widgets[0], Rule):
            self.widgets.pop(0)

        # start yielding widgets
        if self.title:
            yield Header()
        yield self.output  # NOTE not used
        yield Footer()
        if text := self.adaptor.interface._redirected.join():
            yield Label(text, id="buffered_text")
        focus_set = False
        with VerticalScroll():
            yield from self.adaptor.layout_elements
            for i, fieldt in enumerate(self.widgets):
                if isinstance(fieldt, Input):
                    yield Label(fieldt.placeholder)
                yield fieldt
                if fieldt._arbitrary:
                    yield fieldt._arbitrary
                if isinstance(fieldt, Changeable) and fieldt._link.description:
                    if not focus_set:
                        focus_set = True
                        self.focused_i = i
                    yield Label(fieldt._link.description)
                yield Label("")
        self.focusable = [w for w in self.widgets if isinstance(w, (Input, Changeable))]

    def on_mount(self):
        self.widgets[self.focused_i].focus()

    def action_confirm(self):
        # next time, start on the same widget
        # NOTE the functionality is probably not used
        self.focused_i = next((i for i, inp in enumerate(self.focusable) if inp == self.focused), None)
        self.exit(True)

    def action_exit(self):
        self.exit()

    def on_key(self, event: events.Key) -> None:
        try:
            index = self.focusable.index(self.focused)
        except ValueError:  # probably some other element were focused
            return
        match event.key:
            case "down":
                self.focusable[(index + 1) % len(self.focusable)].focus()
            case "up":
                self.focusable[(index - 1) % len(self.focusable)].focus()
            case "enter":
                # NOTE a multiline input might be
                # isinstance(self.focused,
                if self.submit:
                    self.action_confirm()
            case letter if len(letter) == 1:  # navigate by letters
                for inp_ in self.focusable[index+1:] + self.focusable[:index]:
                    match inp_:
                        case Checkbox():
                            label = inp_.label
                        case Changeable():
                            label = inp_._link.name
                        case _:
                            label = ""
                    if str(label).casefold().startswith(letter):
                        inp_.focus()
                        break
