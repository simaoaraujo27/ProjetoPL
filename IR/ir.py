from dataclasses import dataclass, field

# Estas classes usam @dataclass porque representam apenas dados do IR.
# O Python gera automaticamente metodos como __init__ e __repr__,
# o que reduz codigo repetido e deixa a estrutura mais clara.


@dataclass(frozen=True)
class IRValue:
    type: str | None = None


@dataclass(frozen=True)
class IRVariable(IRValue):
    name: str = ""

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class IRTemp(IRValue):
    name: str = ""

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class IRConstant(IRValue):
    value: object = None

    def __str__(self):
        return str(self.value)


@dataclass(frozen=True)
class IRLabelRef:
    name: str

    def __str__(self):
        return self.name


@dataclass
class IRInstruction:
    opcode: str
    args: list[object] = field(default_factory=list)
    result: object | None = None
    comment: str | None = None

    def render(self):
        if self.opcode == "LABEL" and self.args:
            body = f"{self.args[0]}:"
        else:
            prefix = f"{self.result} = " if self.result is not None else ""
            args = " ".join(str(arg) for arg in self.args)
            body = f"{prefix}{self.opcode}"
            if args:
                body = f"{body} {args}"

        if self.comment:
            body = f"{body} ; {self.comment}"

        return body

    def __str__(self):
        return self.render()


@dataclass
class IRProgram:
    name: str
    instructions: list[IRInstruction] = field(default_factory=list)

    def emit(self, opcode, *args, result=None, comment=None):
        instruction = IRInstruction(
            opcode=opcode,
            args=list(args),
            result=result,
            comment=comment,
        )
        self.instructions.append(instruction)
        return instruction

    def extend(self, instructions):
        self.instructions.extend(instructions)

    def render(self):
        lines = [f"PROGRAM {self.name}"]

        for instruction in self.instructions:
            lines.append(instruction.render())

        return "\n".join(lines)

    def __str__(self):
        return self.render()
