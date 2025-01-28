from dataclasses import MISSING, dataclass, field, fields


@dataclass
class CLApp(object):
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
        self.arguments(argp)
        self.parse_arguments(argp, args)
        self.ready()
        self.start()
        self.done()
        return self

    def new_argparse(self):
        from argparse import ArgumentParser

        return ArgumentParser()

    def arguments(self, argp: "argparse.ArgumentParser"):
        def arg(kw, x):
            kw["dest"] = x.name

            action = kw.get("action")
            const = kw.get("const")
            if action is None:
                if const is not None:
                    kw["action"] = "store_const"
                elif issubclass(x.type, bool):
                    if x.default is None:
                        try:
                            from argparse import BooleanOptionalAction

                            kw["action"] = BooleanOptionalAction
                        except:
                            kw["action"] = "store_true"
                    else:
                        if x.default:
                            kw["action"] = "store_false"
                        else:
                            kw["action"] = "store_true"
                elif issubclass(x.type, list):
                    if "nargs" not in kw:
                        kw["action"] = "append"
                else:
                    kw["action"] = "store"
            if x.type is bool:
                pass
            elif issubclass(x.type, (int, float)):
                kw["type"] = x.type

            name = kw.pop("name", None)
            flag = kw.pop("flag", None)
            if flag is None:
                if name is None:
                    pass
                elif isinstance(name, str):
                    kw["metavar"] = name
                else:
                    for x in name:
                        if " " in x or "\t" in x:
                            kw["help"] = x
                        else:
                            if "metavar" in kw:
                                pass
                            else:
                                kw["metavar"] = x
                name = ()
            else:
                assert name is None
                if isinstance(flag, str):
                    flag = (flag,)
                while 1:
                    name = []
                    # print("flag", flag)
                    for x in flag:
                        if " " in x or "\t" in x:
                            kw["help"] = x
                        else:
                            name.append(
                                x
                                if x.startswith("-")
                                else f"--{x}" if len(x) > 1 else f"-{x}"
                            )
                    if len(name) < 1:
                        flag = [kw["dest"]]
                    else:
                        break

            # print("ARG", name, kw)
            argp.add_argument(*name, **kw)

        for x in fields(self):
            m = x.metadata
            kw = m.get("argp")
            if kw is None:
                continue
            elif isinstance(kw, (list, tuple)):
                for v in kw:
                    arg({**v}, x)
            else:
                arg({**kw}, x)

    def subparsers(self):
        pass

    def parse_arguments(
        self, argp: "argparse.ArgumentParser", args: "Sequence[str] | None"
    ):
        sp = None
        for s, k in self.sub_apps():
            if s:
                if sp is None:
                    sp = argp.add_subparsers(required=True)
                    # sp.
                p = sp.add_parser(k.pop("name"), *k)
                p.set_defaults(_sub_apps=s)
                s.arguments(p)
        if sp:
            ns = argp.parse_args(args, namespace=NS())
            # print("A", ns.__class__.__name__, list(ns.__dict__.items()))

            try:
                s = ns._sub_apps
            except AttributeError:
                for k, v in ns.__dict__.items():
                    setattr(self, k, v)
            else:
                q = set(x.name for x in fields(s))
                s._parent_arg = self
                self._child_arg = s
                for k, v in ns.__dict__.items():
                    if k in q:
                        setattr(s, k, v)
                    else:
                        setattr(self, k, v)
                s.ready()
                s.start()
                s.done()
        else:
            ns = argp.parse_args(args, self)

    def ready(self):
        pass

    def done(self):
        pass

    def start(self):
        pass

    def sub_apps(self):
        yield None, {}


from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    import argparse
    from typing import Sequence


class NS(object):
    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        # print("SET", name, value)


_names = ("actions", "nargs", "const", "type", "choices", "required", "help", "metavar")


def arg(
    *args: str,
    default=MISSING,
    default_factory=MISSING,
    init: Union[bool, None] = None,
    repr=False,
    hash=None,
    compare=True,
    **kwargs,
):
    d: dict = {"name": args}
    for k in kwargs:
        if k in _names:
            d[k] = kwargs[k]

    metadata = {"argp": d}

    if default is MISSING:
        return field(
            default_factory=default_factory,
            init=init,
            repr=repr,
            hash=hash,
            compare=compare,
            metadata=metadata,
        )
    else:
        d["default"] = default

        return field(
            default=default,
            init=init,
            repr=repr,
            hash=hash,
            compare=compare,
            metadata=metadata,
        )


def flag(
    *args: str,
    default=MISSING,
    default_factory=MISSING,
    init: Union[bool, None] = None,
    repr=False,
    hash=None,
    compare=True,
    **kwargs,
):
    d: dict = {"flag": args}
    for k in kwargs:
        if k in _names:
            d[k] = kwargs[k]

    metadata = {"argp": d}

    if default is MISSING:
        return field(
            default_factory=default_factory,
            init=init,
            repr=repr,
            hash=hash,
            compare=compare,
            metadata=metadata,
        )
    else:
        d["default"] = default

        return field(
            default=default,
            init=init,
            repr=repr,
            hash=hash,
            compare=compare,
            metadata=metadata,
        )
