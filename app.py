import tkinter as tk
from enum import Enum
from converterToCpp import Converter
import os
import subprocess

RECTANGLE_BLOCKS = []
RECTANGLE_CONNECTIONS = []
BLOCKS = []

TEXT_X_BIAS = 75
TEXT_Y_BIAS = 25
ENTRY_X_BIAS = 75
ENTRY_Y_BIAS = 50
RECTANGLE_X_BIAS = 150
RECTANGLE_Y_BIAS = 75


class Color(Enum):
    green="lightgreen"
    red ="red"
    blue ="blue"

class Buttons(Enum):
    dgitalWrite="digitalWrite"
    analogWrite="analogWrite"
    digitalRead="digitalRead"
    analogRead="analogRead"
    delay="delay"
    pinMode="pinMode"

    freeze="build"
    run="run"


def RECTANGLE_CONNECTIONS_init(arr):
    global RECTANGLE_CONNECTIONS
    RECTANGLE_CONNECTIONS = [[arr[i-1], arr[i]] for i in range(1, len(arr))]

def draw_connections(id_1, id_2, app):
    def _get_center(item_id):
        coords = app.canvas.coords(item_id)
        
        if len(coords) == 4:  # Для прямоугольника (x1, y1, x2, y2)
            center_x = (coords[0] + coords[2]) / 2
            center_y = (coords[1] + coords[3]) / 2
        elif len(coords) == 6:  # Для овала (x1, y1, x2, y2, x3, y3)
            center_x = (coords[0] + coords[2]) / 2
            center_y = (coords[1] + coords[3]) / 2
        else:
            center_x = None
            center_y = None

        return [center_x, center_y]

    center_1 = _get_center(id_1)
    center_2 = _get_center(id_2)
    app.canvas.create_line(center_1[0], center_1[1],
                           center_2[0], center_2[1],
                           fill="black",
                           tags="line")
    app.canvas.tag_lower("line")

class Block:
    def __init__(self, canvas, x, y, text, color, root):
        self.canvas = canvas
        self.color = color
        self.rect = canvas.create_rectangle(x, y, x + RECTANGLE_X_BIAS, y + RECTANGLE_Y_BIAS, fill=color)
        self.text = text
        self.text_id = canvas.create_text(x + TEXT_X_BIAS, y + TEXT_Y_BIAS, text=f"{self.text}", font=("Arial", 12))
        RECTANGLE_BLOCKS.append(self.rect) 
        self.entry = tk.Entry(root) 
        self.entry_1_id = self.canvas.create_window(x+ENTRY_X_BIAS, y+ENTRY_Y_BIAS, window=self.entry)

        
        # Привязываем события к блоку
        self.canvas.tag_bind(self.rect, "<Double-1>", self.change_color)
        self.canvas.tag_bind(self.rect, "<Button-3>", self.delete_block)
        self.canvas.tag_bind(self.rect, "<Button-1>", self.start_move)

        self.is_moving = False
        self.offset_x = 0
        self.offset_y = 0

        #
        # Block.block_info = {"type":"digitalWrite | analogWrite | pinMode",
        #                     "pin":int(),
        #                     "state" 1/0 или input output для pinMode}
        # Block.block_info = {"type":"digitalRead | analogRead | delay",
        #                    "pin | timedelay":int()}

    def change_color(self, event):
        current_color = self.canvas.itemcget(self.rect, "fill")
        new_color = "lightgreen" if current_color == "lightblue" else "lightblue"
        self.canvas.itemconfig(self.rect, fill=new_color)
        self.color = new_color

    def delete_block(self, event):
        app.canvas.tag_lower("line")
        RECTANGLE_BLOCKS.remove(self.rect)
        RECTANGLE_CONNECTIONS_init(RECTANGLE_BLOCKS)
        self.canvas.delete(self.rect)
        self.canvas.delete(self.text_id)
        BLOCKS.remove(self)
        print(RECTANGLE_CONNECTIONS) 
        self.canvas.delete("line")
        self.canvas.delete(self.entry_1_id)
        for cons in RECTANGLE_CONNECTIONS:
            draw_connections(cons[0], cons[1], self)
        print(BLOCKS)

    def start_move(self, event):
        self.is_moving = True
        self.offset_x = event.x - self.canvas.coords(self.rect)[0]
        self.offset_y = event.y - self.canvas.coords(self.rect)[1]
        self.canvas.bind("<B1-Motion>", self.move_block)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)

    def move_block(self, event):
        self.canvas.delete("line")
        if self.is_moving:
            new_x = event.x - self.offset_x
            new_y = event.y - self.offset_y
            self.canvas.coords(self.rect, new_x, new_y, new_x + RECTANGLE_X_BIAS, new_y + RECTANGLE_Y_BIAS)
            self.canvas.coords(self.text_id, new_x + TEXT_X_BIAS, new_y + TEXT_Y_BIAS)
            self.canvas.coords(self.entry_1_id, new_x + ENTRY_X_BIAS, new_y + ENTRY_Y_BIAS)
            for cons in RECTANGLE_CONNECTIONS:
                draw_connections(cons[0], cons[1], self)
            #self.canvas.create_text(50, 50, text=f"{new_x}, {new_y}", font=("Arial", 12))

    def stop_move(self, event):
        self.is_moving = False
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Block Creator")
        self.geometry("800x600")
        
        self.canvas = tk.Canvas(self, bg="lightpink")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Меню
        menu = tk.Menu(self)
        self.config(menu=menu)

        block_menu = tk.Menu(menu, tearoff=0)
        #settings_menu = tk.Menu(menu, tearoff=0)
        terminal_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Блоки", menu=block_menu)
        #menu.add_cascade(label="Сценарии", menu=settings_menu)
        menu.add_cascade(label="Терминал", menu=terminal_menu)

        block_menu.add_command(label=Buttons.dgitalWrite.value, command= lambda: self.create_block(btn_type=Buttons.dgitalWrite.value))
        block_menu.add_command(label=Buttons.analogWrite.value, command= lambda: self.create_block(btn_type=Buttons.analogWrite.value))
        block_menu.add_command(label=Buttons.digitalRead.value, command= lambda: self.create_block(btn_type=Buttons.digitalRead.value))
        block_menu.add_command(label=Buttons.analogRead.value, command= lambda: self.create_block(btn_type=Buttons.analogRead.value))
        block_menu.add_command(label=Buttons.delay.value, command= lambda: self.create_block(btn_type=Buttons.delay.value))
        block_menu.add_command(label=Buttons.pinMode.value, command= lambda: self.create_block(btn_type=Buttons.pinMode.value))

        terminal_menu.add_command(label=Buttons.freeze.value, command= self.freeze)
        terminal_menu.add_command(label=Buttons.run.value, command= self.run)

    def freeze(self):
        class BlockConverter():
            def __init__(self, command, text, color):
                self.block_info = {}
                self.block_info["type"] = command
                self.block_info["text"] = text
                self.block_info["color"] = color

            def __str__(self):
                return f"{self.block_info["type"]}:{self.block_info["text"]}"
    
        arrBlocks = [BlockConverter(BLOCKS[i].text, BLOCKS[i].entry.get(), BLOCKS[i].color) for i in range(len(BLOCKS))]
        # arrBlocks = [BlockConverter(BLOCKS[i].text, BLOCKS[i].entry.get()) for i in range(len(BLOCKS))]
        # print(*arrBlocks, sep='\n')
        
        converter = Converter(arrBlocks)
        cppCode = converter.generate_code()
        # print(cppCode)

        with open("basic.cpp", "w") as inputFile:
            for cppLine in cppCode:
                inputFile.write(cppLine)
        
    def run(self):
        if (os.path.exists("basic.cpp")):


            # Создание директории build
            os.makedirs('build', exist_ok=True)

            # Определение пути к cmake
            cmake_path = r"C:\Users\Chess\AppData\Local\Arduino15\packages\Rudiron\tools\cmake\default\bin\cmake.exe"

            # Команды для выполнения
            commands = [
                [cmake_path, "-DCMAKE_BUILD_TYPE=Release", "-G", "Ninja", "-S", ".", "-B", "build/"],
                [cmake_path, "--build", "build"],
                [cmake_path, "-DCMAKE_BUILD_TYPE=Release", "-G", "Ninja", "-S", ".", "-B", "build/"],
                [cmake_path, "--build", "build"],
                [r"C:\Users\Chess\AppData\Local\Arduino15\packages\Rudiron\tools\Rudiron Programmer\default\Rudiron Programmer.exe",
                r"C:\Users\Chess\AppData\Local\Arduino15\packages\Rudiron\tools\bootloaders\default\MDR32F9Qx_default.hex",
                r"c:\cs_hack\basic_led\build\Sketch.hex",
                "--port", "COM5", "--speed", "0", "--erase", "--load", "--run", "--english"]
            ]

            # Выполнение команд
            for command in commands:
                try:
                    subprocess.run(command, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Ошибка при выполнении команды: {e.cmd}")
                    print(f"Код возврата: {e.returncode}")

    def create_block(self, btn_type="meow", color="lightblue"):
        if len(RECTANGLE_BLOCKS) > 0:
            last_rect_coords = self.canvas.coords(RECTANGLE_BLOCKS[-1])
            last_x = last_rect_coords[0]
            last_y = last_rect_coords[3]
            new_block = Block(self.canvas, x=last_x, y=last_y+10, text=btn_type, color=color, root=self)
        else:
            new_block = Block(self.canvas, x=20, y=20, text=btn_type, color=color, root=self)
        RECTANGLE_CONNECTIONS_init(RECTANGLE_BLOCKS)
        BLOCKS.append(new_block)
            
        for cons in RECTANGLE_CONNECTIONS:
            draw_connections(cons[0], cons[1], self)
        print(BLOCKS)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
