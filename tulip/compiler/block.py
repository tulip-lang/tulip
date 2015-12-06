def compile_block(expr, context):
    parts = []
    last_let_run = []
    lines = split_lines(expr)

    for (i, line) in enumerate(lines):
        assert len(line) > 0, u'empty line!'

        (equal_sign, before, after) = try_split(line, Token.EQ)
        is_let = equal_sign is not None

        if is_let and i == len(lines) - 1:
            context.error(equal_sign, u'block can\'t end with assignment!')
            return

        if is_let:
            last_let_run.append(before, after)
        else:
            if len(last_let_run) > 0:
                parts.extend(compile_let_run(last_let_run, context))
                last_let_run = []

            parts.append(compile_expr(line, context))

    if len(last_let_run) > 0:
        parts.extend(compile_let_run(last_let_run, context))

    if len(parts) == 1:
        return parts[0]
    else:
        return c.Block(parts)

def compile_let_run(let_run, context):
    # TODO: recursion
    assert False, u'TODO: compile let runs'

