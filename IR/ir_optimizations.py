from .ir import IRInstruction


LABEL_OPCODES_WITH_TARGET = {"JUMP", "JUMP_IF_FALSE", "CALL"}
PINNED_LABEL_PREFIXES = ("UNIT_",)


def optimize_ir(program):
    _remove_redundant_jumps(program)
    _remove_unused_labels(program)
    return program


def _remove_redundant_jumps(program):
    optimized = []
    instructions = program.instructions

    for index, instruction in enumerate(instructions):
        if instruction.opcode == "JUMP" and instruction.args:
            target_name = str(instruction.args[0])
            fallthrough_labels = _collect_fallthrough_labels(instructions, index + 1)
            if target_name in fallthrough_labels:
                continue

        optimized.append(instruction)

    program.instructions = optimized


def _remove_unused_labels(program):
    used_labels = set()

    for instruction in program.instructions:
        if instruction.opcode not in LABEL_OPCODES_WITH_TARGET:
            continue
        for argument in instruction.args:
            if hasattr(argument, "name"):
                used_labels.add(argument.name)

    optimized = []
    for instruction in program.instructions:
        if instruction.opcode == "LABEL" and instruction.args:
            label_name = str(instruction.args[0])
            if label_name.startswith(PINNED_LABEL_PREFIXES):
                optimized.append(instruction)
                continue
            if label_name not in used_labels:
                continue

        optimized.append(instruction)

    program.instructions = optimized


def _collect_fallthrough_labels(instructions, start_index):
    labels = set()
    index = start_index

    while index < len(instructions):
        instruction = instructions[index]
        if instruction.opcode != "LABEL" or not instruction.args:
            break
        labels.add(str(instruction.args[0]))
        index += 1

    return labels
