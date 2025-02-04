class Main(object):
    def __getattr__(self, name: str):
        if not name.startswith("_get_"):
            f = getattr(self, f"_get_{name}", None)
            if f:
                setattr(self, name, None)
                v = f()
                setattr(self, name, v)
                return v
        try:
            m = super().__getattr__
        except AttributeError:
            raise AttributeError(
                f"{self.__class__.__name__} has no attribute {name}"
            ) from None
        else:
            return m(name)

    def main(
        self,
        args: "Sequence[str] | None" = None,
        argp: "argparse.ArgumentParser | None" = None,
    ):
        if argp is None:
            argp = self.new_argparse()
        self.init_argparse(argp)
        self.add_arguments(argp)
        self.parse_arguments(argp, args)
        self.ready()
        self.start()
        self.done()
        return self

    def new_argparse(self):
        from argparse import ArgumentParser

        return ArgumentParser()

    def init_argparse(self, argp):
        pass

    def add_arguments(self, argp: "argparse.ArgumentParser"):

        for k, v, t in _arg_fields(self):
            v._add(k, t, argp, self)

    def subparsers(self):
        pass

    def parse_arguments(
        self, argp: "argparse.ArgumentParser", args: "Sequence[str] | None"
    ):
        sp = None
        for s, k in self.sub_args():
            if s:
                if sp is None:
                    sp = argp.add_subparsers(required=True)
                    # sp.
                s._parent_arg = self
                p = sp.add_parser(k.pop("name"), *k)
                p.set_defaults(_sub_apps=s)
                s.init_argparse(p)
                s.add_arguments(p)

        if sp:
            ns = argp.parse_args(args)
            # print("A", ns.__class__.__name__, list(ns.__dict__.items()))

            try:
                s = self._sub_arg = ns._sub_apps
            except AttributeError:
                raise
            else:
                m = ns.__dict__
                while s:
                    for k, v, t in _arg_fields(s):
                        if k in m:
                            # print("setattr", s, k, m[k])
                            setattr(s, k, m[k])
                    p = getattr(s, "_parent_arg", None)
                    if p:
                        s.ready()
                        s.start()
                        s.done()
                    s = p
        else:
            ns = argp.parse_args(args, self)

    def ready(self):
        pass

    def done(self):
        pass

    def start(self):
        pass

    def sub_args(self):
        yield None, {}


from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    import argparse
    from typing import Sequence


_names = ("actions", "nargs", "const", "type", "choices", "required", "help", "metavar")

INVALID = object()


class Argument:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def _add(self, name, type, argp, that):
        # print("_add", name, type, that, self.args, self.kwargs)
        args = []
        kwargs = {**self.kwargs}

        action = kwargs.get("action")
        const = kwargs.get("const")
        d = kwargs.get("default", INVALID)
        if action is None:
            if const is not None:
                if type and issubclass(type, list):
                    kwargs["action"] = "append_const"
                else:
                    kwargs["action"] = "store_const"
            elif type is None:
                kwargs["action"] = "store"
            elif issubclass(type, bool):
                if d is None:
                    try:
                        from argparse import BooleanOptionalAction

                        kwargs["action"] = BooleanOptionalAction
                    except:
                        kwargs["action"] = "store_true"
                elif d is True:
                    kwargs["action"] = "store_false"
                else:
                    assert d is INVALID or d is False
                    kwargs["action"] = "store_true"
            elif issubclass(type, list):
                if "nargs" not in kwargs:
                    kwargs["action"] = "append"
                if "default" not in kwargs:
                    kwargs["default"] = []
            else:
                kwargs["action"] = "store"
        parser = kwargs.pop("parser", None)
        if parser:
            kwargs["type"] = parser

        if kwargs.pop("flag", None) is None:
            for x in self.args:
                if " " in x or "\t" in x:
                    kwargs["help"] = x
                else:
                    if "metavar" in kwargs:
                        pass
                    else:
                        kwargs["metavar"] = x
            if kwargs.pop("required", None) is False:
                kwargs["nargs"] = "?"
        else:

            def add_args(x):
                args.append(
                    x if x.startswith("-") else (f"--{x}" if len(x) > 1 else f"-{x}")
                )

            for x in self.args:
                if " " in x or "\t" in x:
                    kwargs["help"] = x
                else:
                    add_args(x)
            # print("add_args", args)
            if len(args) < 1:
                add_args(name)

        kwargs["dest"] = name
        setattr(that, name, kwargs.get("default"))

        # print("add_argument", (name, type), args, kwargs)
        argp.add_argument(*args, **kwargs)


def _arg_fields(inst):
    for c in inst.__class__.__mro__:
        for k, v in tuple(c.__dict__.items()):
            if isinstance(v, Argument):
                yield k, v, c.__annotations__.get(k)
            elif isinstance(v, (list, tuple)):
                if isinstance(v[0], Argument):
                    for x in v:
                        yield k, x, c.__annotations__.get(k)


def arg(*args: str, **kwargs):
    return Argument(*args, **kwargs)


def flag(*args: str, **kwargs):
    return Argument(*args, flag=True, **kwargs)
