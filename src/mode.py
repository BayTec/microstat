AUTO_MODE = const("auto")
HEAT_MODE = const("heat")
OFF_MODE = const("off")

def next_mode(current_mode: str) -> str:
    if current_mode == AUTO_MODE:
        return HEAT_MODE
    elif current_mode == HEAT_MODE:
        return OFF_MODE
    else:
        return AUTO_MODE