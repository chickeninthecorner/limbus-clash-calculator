# Limbus Clash Calculator

This tool is used to calculate the win rates, tie rates, and lose rates of a clash in Limbus Company.

Access it [here](https://chickeninthecorner.github.io/limbus-clash-calculator/).

![](https://github.com/user-attachments/assets/10fd89b4-199b-45e3-aacd-848daf49bda9)

This project was originally built with Python and [Pyscript](https://github.com/pyscript/pyscript). AI was only used in translating this project to convert Python to C++ and Javacript to significantly improve performance. All changes after are not AI generated.

To compile the C++ code using [Emscripten](https://github.com/emscripten-core/emscripten):
```
em++ clash.cpp -o clash.js -lembind -s ALLOW_MEMORY_GROWTH=1 -s STACK_SIZE=10485760
```
