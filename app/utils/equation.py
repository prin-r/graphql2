from decimal import Decimal

OPCODE_CONST = 0
OPCODE_VAR = 1
OPCODE_SQRT = 2
OPCODE_NOT = 3
OPCODE_ADD = 4
OPCODE_SUB = 5
OPCODE_MUL = 6
OPCODE_DIV = 7
OPCODE_EXP = 8
OPCODE_PCT = 9
OPCODE_EQ = 10
OPCODE_NE = 11
OPCODE_LT = 12
OPCODE_GT = 13
OPCODE_LE = 14
OPCODE_GE = 15
OPCODE_AND = 16
OPCODE_OR = 17
OPCODE_IF = 18
OPCODE_BANCOR_LOG = 19
OPCODE_BANCOR_POWER = 20


def calculate_price_at(self, value):
    x_value = Decimal(value)
    return calculate_collateral_at(self, x_value + 1) - calculate_collateral_at(
        self, x_value
    )


def calculate_collateral_at(self, value):
    x_value = Decimal(value)
    (end, val) = solve_math(self, 0, x_value)
    if end != (len(self) - 1):
        raise ValueError("Invalid equation")
    return val


def get_children_count(opcode):
    if opcode <= OPCODE_VAR:
        return 0
    elif opcode <= OPCODE_NOT:
        return 1
    elif opcode <= OPCODE_OR:
        return 2
    elif opcode <= OPCODE_BANCOR_LOG:
        return 3
    elif opcode <= OPCODE_BANCOR_POWER:
        return 4


def dry_run(self, start_index):
    if start_index >= len(self):
        raise IndexError("start_index must less than len(self)")
    opcode = Decimal(self[start_index])
    if opcode == OPCODE_CONST:
        return start_index + 1
    children_count = get_children_count(opcode)
    last_index = start_index
    for idx in range(children_count):
        last_index = dry_run(self, last_index + 1)

    return last_index


def solve_math(self, start_index, x_value):
    if start_index >= len(self):
        raise IndexError("start_index must less than len(self)")
    opcode = Decimal(self[start_index])

    if opcode == OPCODE_CONST:
        return (start_index + 1, Decimal(self[start_index + 1]))
    elif opcode == OPCODE_VAR:
        return (start_index, x_value)
    elif opcode == OPCODE_SQRT:
        (end_index, child_value) = solve_math(self, start_index + 1, x_value)
        return (end_index, child_value.sqrt())
    elif OPCODE_ADD <= opcode <= OPCODE_PCT:
        (left_end_index, left_value) = solve_math(
            self, start_index + 1, x_value
        )
        (end_index, right_value) = solve_math(self, left_end_index + 1, x_value)

        if opcode == OPCODE_ADD:
            return (end_index, left_value + right_value)
        elif opcode == OPCODE_SUB:
            return (end_index, left_value - right_value)
        elif opcode == OPCODE_MUL:
            return (end_index, left_value * right_value)
        elif opcode == OPCODE_DIV:
            return (end_index, left_value / right_value)
        elif opcode == OPCODE_EXP:
            return (end_index, left_value ** right_value)
        elif opcode == OPCODE_PCT:
            return (
                end_index,
                left_value * right_value / Decimal(1000000000000000000),
            )
    elif opcode == OPCODE_IF:
        (cond_end_index, cond_value) = solve_bool(
            self, start_index + 1, x_value
        )
        if cond_value:
            (then_end_index, then_value) = solve_math(
                self, cond_end_index + 1, x_value
            )
            return (dry_run(self, then_end_index + 1), then_value)
        else:
            then_end_index = dry_run(self, cond_end_index + 1)
            return solve_math(self, then_end_index + 1, x_value)
    elif opcode == OPCODE_BANCOR_LOG:
        (multiplier_end_index, multiplier) = solve_math(
            self, start_index + 1, x_value
        )
        (base_n_end_index, base_n) = solve_math(
            self, multiplier_end_index + 1, x_value
        )
        (base_d_end_index, base_d) = solve_math(
            self, base_n_end_index + 1, x_value
        )
        return (base_d_end_index, (base_n / base_d).ln() * multiplier)
    elif opcode == OPCODE_BANCOR_POWER:
        (multiplier_end_index, multiplier) = solve_math(
            self, start_index + 1, x_value
        )
        (base_n_end_index, base_n) = solve_math(
            self, multiplier_end_index + 1, x_value
        )
        (base_d_end_index, base_d) = solve_math(
            self, base_n_end_index + 1, x_value
        )
        (exp_v_end_index, exp_v) = solve_math(
            self, base_d_end_index + 1, x_value
        )
        if exp_v < Decimal(0):
            raise ValueError("exp should more than 0")
        exp_divided_by_m = exp_v / Decimal(1000000)  # dividedBy 10^6
        return (
            exp_v_end_index,
            ((base_n / base_d) ** exp_divided_by_m) * multiplier,
        )


def solve_bool(self, start_index, x_value):
    if start_index >= len(self):
        raise IndexError("start_index must less than len(self)")
    opcode = Decimal(self[start_index])

    if opcode == OPCODE_NOT:
        (end_index, value) = solve_bool(self, start_index + 1, x_value)
        return (end_index, not value)
    elif OPCODE_EQ <= opcode <= OPCODE_GE:
        (left_end_index, left_value) = solve_math(
            self, start_index + 1, x_value
        )
        (right_end_index, right_value) = solve_math(
            self, left_end_index + 1, x_value
        )

        if opcode == OPCODE_EQ:
            return (right_end_index, left_value == right_value)
        elif opcode == OPCODE_NE:
            return (right_end_index, left_value != right_value)
        elif opcode == OPCODE_LT:
            return (right_end_index, left_value < right_value)
        elif opcode == OPCODE_GT:
            return (right_end_index, left_value > right_value)
        elif opcode == OPCODE_LE:
            return (right_end_index, left_value <= right_value)
        elif opcode == OPCODE_GE:
            return (right_end_index, left_value >= right_value)
    elif OPCODE_AND <= opcode <= OPCODE_OR:
        (left_end_index, leftBool_value) = solve_bool(
            self, start_index + 1, x_value
        )
        if opcode == OPCODE_AND:
            if leftBool_value:
                return solve_bool(self, left_end_index + 1, x_value)
            else:
                return (dry_run(self, left_end_index + 1), False)
        elif opcode == OPCODE_OR:
            if leftBool_value:
                return [dry_run(self, left_end_index + 1), True]
            else:
                return solve_bool(self, left_end_index + 1, x_value)
    elif opcode == OPCODE_IF:
        (cond_end_index, cond_value) = solve_bool(
            self, start_index + 1, x_value
        )
        if cond_value:
            (then_end_index, then_value) = solve_bool(
                self, cond_end_index + 1, x_value
            )
            return (dry_run(self, then_end_index + 1), then_value)
        else:
            then_end_index = dry_run(self, cond_end_index + 1)
            return solve_bool(self, then_end_index + 1, x_value)
