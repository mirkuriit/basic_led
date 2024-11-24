# class Block:
#     def __init__(self, block_info: dict):
#         self.block_info = block_info

#     def get_block_info(self):
#         return self.block_info

# from main import Block

class Converter:
    def __init__(self, blocks):
        self.blocks = blocks
        self.default_values = {
            "digitalWrite": "LOW",
            "analogWrite": "0",
            "delay": "1000",
        }

    def generate_code(self):
        setup_code = []
        loop_code = []

        for block in self.blocks:
            block_info = block.block_info
            # print(block_info)
            command = block_info["type"]
            pars = block_info["text"].split()
            color = block_info["color"]
            print(command, pars, color)

            if color == "lightblue":
                setup_code.append(self._generate_command(command, pars))
            elif color == "lightgreen":
                loop_code.append(self._generate_command(command, pars))

        # Формируем итоговый код
        result = [
            "#include \"Arduino.h\"",
            "void setup() {",
        ]
        
        if setup_code:
            result.extend(["    " + line for line in setup_code])
        result.append("}")

        result.append("void loop() {")
        if loop_code:
            result.extend(["    " + line for line in loop_code])
        result.append("}")

        return "\n".join(result)

    def _generate_command(self, command: str, params: list):
        # params = []

        # if pin is not None:
        #     params.append(pin)
        # if state is not None:
        #     params.append(state)
        # elif pin is None and state is None:
        #     params.append(self.default_values.get(command, ""))

        # return f"{command}({', '.join(params)});"
        return f"{command}({', '.join(params)});"

# Пример использования
# blocks = [
#     Block({"type": "pinMode", "text": "13 OUTPUT"}),
#     Block({"type": "digitalWrite", "text": "13 HIGH"}),
#     Block({"type": "delay", "text": "1000"}),
#     Block({"type": "digitalWrite", "text": "13 LOW"}),
#     Block({"type": "delay", "text": "1000"}),
#     Block({"type": "pinMode", "text": "10 INPUT"})
# ]

# converter = Converter(blocks)
# cppCode = converter.generate_code()

# with open("convertCode.cpp", "w") as inputFile:
#     for cppLine in cppCode:
#         inputFile.write(cppLine)
