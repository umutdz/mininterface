Via the [run][mininterface.run] function you get access to the CLI, possibly enriched from the config file. Then, you receive all data as [`m.env`][mininterface.Mininterface.env] object and dialog methods in a proper UI.

```mermaid
graph LR
    subgraph mininterface
        run --> GUI
        run --> TUI
        run --> WebUI
        run --> env
        CLI --> run
        id1[config file] --> CLI
    end
    program --> run
```

## Basic usage
Use a common [dataclass](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass), an argparse [`ArgumentParser`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser), a Pydantic [BaseModel](https://brentyi.github.io/tyro/examples/04_additional/08_pydantic/) or an [attrs](https://brentyi.github.io/tyro/examples/04_additional/09_attrs/) model to store the configuration. Wrap it to the [run][mininterface.run] function that returns an interface `m`. Access the configuration via [`m.env`][mininterface.Mininterface.env] or use it to prompt the user with methods like [`m.confirm("Is that alright?")`][mininterface.Mininterface.confirm].

There are a lot of supported [types](Supported-types.md) you can use, not only scalars and well-known objects (`Path`, `datetime`), but also functions, iterables (like `list[Path]`) and union types (like `int | None`). To do even more advanced things, stick the value to a powerful [`Tag`][mininterface.Tag] or its [subclasses](Supported-types.md#additional). Ex. for a validation only, use its [`Validation alias`][mininterface.tag.alias.Validation].

At last, use [`Facet`](Facet.md) to tackle the interface from the back-end (`m`) or the front-end (`Tag`) side.

## IDE suggestions

The immediate benefit is the type suggestions provided by your IDE.

### Dataclass showcase

Imagine following code:

```python
from dataclasses import dataclass
from mininterface import run

@dataclass
class Env:
    my_paths: list[Path]
    """ The user is forced to input Paths. """


@dataclass
class Dialog:
    my_number: int = 2
    """ A number """
```

Now, accessing the main [env][mininterface.Mininterface.env] will trigger the hint.
![Suggestion run](asset/suggestion_run.avif)

Calling the [form][mininterface.Mininterface.form] with an empty parameter will trigger editing the main [env][mininterface.Mininterface.env]

![Suggestion form](asset/suggestion_form_env.avif)

Putting there a dict will return the dict too.

![Suggestion form](asset/suggestion_dict.avif)

Putting there a dataclass type causes it to be resolved.

![Suggestion dataclass type](asset/suggestion_dataclass_type.avif)

Should you have a resolved dataclass instance, put it there.

![Suggestion dataclass instance](asset/suggestion_dataclass_instance.avif)

As you see, its attributes are hinted alongside their description.

![Suggestion dataclass expanded](asset/suggestion_dataclass_expanded.avif)


Should the dataclass cannot be easily investigated by the IDE (i.e. a required field), just annotate the output.

![Suggestion annotation possible](asset/suggestion_dataclass_annotated.avif)

### Select showcase

We push an intuitive type inference everywhere. Here is an example with the [`m.select`][mininterface.Mininterface.select] dialog.

```python
from mininterface import run

m = run()
# x = m.select([1, 2, 3], default=2)  # -> int
# x = m.select([1, 2, 3], multiple=True)  # -> list[int]
# x = m.select([1, 2, 3], default=[2])  # -> list[int]
```

By default, the inferred type is an `int`.

![Suggestion select](asset/suggestion_select1.avif)

When you flag the selection as multiple or when you submit multiple default values...

![Suggestion select](asset/suggestion_select2.avif)

that means your IDE sees a `list` instead of a single value and you can automatically append to it etc.

![Suggestion select](asset/suggestion_select3.avif)

## Nested configuration
You can easily nest the configuration. (See also [Tyro Hierarchical Configs](https://brentyi.github.io/tyro/examples/02_nesting/01_nesting/).)

Just put another dataclass inside the config file:

```python
@dataclass
class FurtherConfig:
    token: str
    host: str = "example.org"

@dataclass
class Env:
    further: FurtherConfig

...
m = run(Env)
print(m.env.further.host)  # example.org
```

The attributes can by defaulted by CLI:

```
$./program.py --further.host example.net
```

And in a YAML config file. Note that you are not obliged to define all the attributes, a subset will do.
(Ex. you do not need to specify `token` too.)

```yaml
further:
  host: example.com
```

## Bash completion

Run your program with a bundled `mininterface` executable to start a tutorial that will install bash completion.

`$ mininterface integrate ./program`

![Bash completion](asset/bash_completion_tutorial.avif)

## System dialog toolkit

Mininterface can be used as a standalone dialog layer for sh scripts. See `mininterface --help`.

```bash
$ mininterface select one two  # outputs a chosen item
```

![Select dialog](asset/choices_labels.avif)