import json

def preprocess(brainfuck_code):
    stack = []
    pairs = {}

    for position, operation in enumerate(brainfuck_code):
        if operation == "[":
            stack.append(position)
        elif operation == "]":
            if not stack:
                raise ValueError(f"Umatched bracket at {position}")
            loop_start = stack.pop()
            pairs[loop_start] = position 
            pairs[position] = loop_start

    if stack:
        raise ValueError(f"Extra unclosed bracket {stack}")
    return pairs


def analyze(brainfuck_code, memory_scope=10, input_str="brainf"):
    tokens = brainfuck_code
    memory_pointer = 0
    memory = [0] * memory_scope
    position = 0
    loops = preprocess(brainfuck_code)
    input_index = 0
    output = []
    snapshots = {}
    op_count = 0

    while (position < len(tokens)):
        operation = tokens[position]

        if operation == ">":
            memory_pointer += 1
        elif operation == "<":
            memory_pointer -= 1 
        elif operation == "+":
            memory[memory_pointer] = (memory[memory_pointer] + 1) % 256
        elif operation == "-":
            memory[memory_pointer] = (memory[memory_pointer] - 1) % 256
        elif operation == "[":
            if memory[memory_pointer] == 0:
                position = loops[position]    
        elif operation == "]" and memory[memory_pointer] != 0:
            position = loops[position]
            continue
        elif operation == ",":
            if input_index < len(input_str):
                memory[memory_pointer] = ord(input_str[input_index])
                input_index += 1

                if input_index == 6:
                    snapshots[position] = memory.copy()
            else:
                memory[memory_pointer] = 0
        elif operation == ".":

            output.append(chr(memory[memory_pointer]))
            if "".join(output).endswith("Password: \n"):
                snapshots[position] = memory.copy()
        elif operation == "!":
            print("DEBUG:", memory[memory_pointer], memory_pointer)

        position += 1

    with open("snapshots.json", "w") as file:
        json.dump(snapshots, file, indent = 4)
    
    return memory, "".join(output), snapshots
