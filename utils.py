def print_color(string, frame_name):
    if frame_name == "primary":
        color = "red"
    else:
        color = "green"
    print(format_color(string, color))


def format_color_name(string, frame_name):
    if frame_name == "primary":
        color = "red"
    else:
        color = "green"
    return format_color(string, color)


def format_color(string, color):
    cs = "\x1b[38;2;{};{};{}m{}\x1b[0m"

    # my colors
    if color == "red1":
        r, g, b = 215, 0, 0
    elif color == "green1":
        r, g, b = 0, 255, 0
    elif color == "blue1":
        r, g, b = 50, 50, 255

    # list from https://www.rapidtables.com/web/color/RGB_Color.html
    elif color == "Black":
        r, g, b = 0, 0, 0
    elif color == "White":
        r, g, b = 255, 255, 255
    elif color == "Red":
        r, g, b = 255, 0, 0
    elif color == "Lime":
        r, g, b = 0, 255, 0
    elif color == "Blue":
        r, g, b = 0, 0, 255
    elif color == "Yellow":
        r, g, b = 255, 255, 0
    elif color == "Cyan":
        r, g, b = 0, 255, 255
    elif color == "Magenta":
        r, g, b = 255, 0, 255
    elif color == "Silver":
        r, g, b = 192, 192, 192
    elif color == "Gray":
        r, g, b = 128, 128, 128
    elif color == "Maroon":
        r, g, b = 128, 0, 0
    elif color == "Olive":
        r, g, b = 128, 128, 0
    elif color == "Green":
        r, g, b = 0, 128, 0
    elif color == "Purple":
        r, g, b = 128, 0, 128
    elif color == "Teal":
        r, g, b = 0, 128, 128
    elif color == "Navy":
        r, g, b = 0, 0, 128
    elif color == "maroon":
        r, g, b = 128, 0, 0
    elif color == "dark red":
        r, g, b = 139, 0, 0
    elif color == "brown":
        r, g, b = 165, 42, 42
    elif color == "firebrick":
        r, g, b = 178, 34, 34
    elif color == "crimson":
        r, g, b = 220, 20, 60
    elif color == "red":
        r, g, b = 255, 0, 0
    elif color == "tomato":
        r, g, b = 255, 99, 71
    elif color == "coral":
        r, g, b = 255, 127, 80
    elif color == "indian red":
        r, g, b = 205, 92, 92
    elif color == "light coral":
        r, g, b = 240, 128, 128
    elif color == "dark salmon":
        r, g, b = 233, 150, 122
    elif color == "salmon":
        r, g, b = 250, 128, 114
    elif color == "light salmon":
        r, g, b = 255, 160, 122
    elif color == "orange red":
        r, g, b = 255, 69, 0
    elif color == "dark orange":
        r, g, b = 255, 140, 0
    elif color == "orange":
        r, g, b = 255, 165, 0
    elif color == "gold":
        r, g, b = 255, 215, 0
    elif color == "dark golden rod":
        r, g, b = 184, 134, 11
    elif color == "golden rod":
        r, g, b = 218, 165, 32
    elif color == "pale golden rod":
        r, g, b = 238, 232, 170
    elif color == "dark khaki":
        r, g, b = 189, 183, 107
    elif color == "khaki":
        r, g, b = 240, 230, 140
    elif color == "olive":
        r, g, b = 128, 128, 0
    elif color == "yellow":
        r, g, b = 255, 255, 0
    elif color == "yellow green":
        r, g, b = 154, 205, 50
    elif color == "dark olive green":
        r, g, b = 85, 107, 47
    elif color == "olive drab":
        r, g, b = 107, 142, 35
    elif color == "lawn green":
        r, g, b = 124, 252, 0
    elif color == "chart reuse":
        r, g, b = 127, 255, 0
    elif color == "green yellow":
        r, g, b = 173, 255, 47
    elif color == "dark green":
        r, g, b = 0, 100, 0
    elif color == "green":
        r, g, b = 0, 128, 0
    elif color == "forest green":
        r, g, b = 34, 139, 34
    elif color == "lime":
        r, g, b = 0, 255, 0
    elif color == "lime green":
        r, g, b = 50, 205, 50
    elif color == "light green":
        r, g, b = 144, 238, 144
    elif color == "pale green":
        r, g, b = 152, 251, 152
    elif color == "dark sea green":
        r, g, b = 143, 188, 143
    elif color == "medium spring green":
        r, g, b = 0, 250, 154
    elif color == "spring green":
        r, g, b = 0, 255, 127
    elif color == "sea green":
        r, g, b = 46, 139, 87
    elif color == "medium aqua marine":
        r, g, b = 102, 205, 170
    elif color == "medium sea green":
        r, g, b = 60, 179, 113
    elif color == "light sea green":
        r, g, b = 32, 178, 170
    elif color == "dark slate gray":
        r, g, b = 47, 79, 79
    elif color == "teal":
        r, g, b = 0, 128, 128
    elif color == "dark cyan":
        r, g, b = 0, 139, 139
    elif color == "aqua":
        r, g, b = 0, 255, 255
    elif color == "cyan":
        r, g, b = 0, 255, 255
    elif color == "light cyan":
        r, g, b = 224, 255, 255
    elif color == "dark turquoise":
        r, g, b = 0, 206, 209
    elif color == "turquoise":
        r, g, b = 64, 224, 208
    elif color == "medium turquoise":
        r, g, b = 72, 209, 204
    elif color == "pale turquoise":
        r, g, b = 175, 238, 238
    elif color == "aqua marine":
        r, g, b = 127, 255, 212
    elif color == "powder blue":
        r, g, b = 176, 224, 230
    elif color == "cadet blue":
        r, g, b = 95, 158, 160
    elif color == "steel blue":
        r, g, b = 70, 130, 180
    elif color == "corn flower blue":
        r, g, b = 100, 149, 237
    elif color == "deep sky blue":
        r, g, b = 0, 191, 255
    elif color == "dodger blue":
        r, g, b = 30, 144, 255
    elif color == "light blue":
        r, g, b = 173, 216, 230
    elif color == "sky blue":
        r, g, b = 135, 206, 235
    elif color == "light sky blue":
        r, g, b = 135, 206, 250
    elif color == "midnight blue":
        r, g, b = 25, 25, 112
    elif color == "navy":
        r, g, b = 0, 0, 128
    elif color == "dark blue":
        r, g, b = 0, 0, 139
    elif color == "medium blue":
        r, g, b = 0, 0, 205
    elif color == "blue":
        r, g, b = 0, 0, 255
    elif color == "royal blue":
        r, g, b = 65, 105, 225
    elif color == "blue violet":
        r, g, b = 138, 43, 226
    elif color == "indigo":
        r, g, b = 75, 0, 130
    elif color == "dark slate blue":
        r, g, b = 72, 61, 139
    elif color == "slate blue":
        r, g, b = 106, 90, 205
    elif color == "medium slate blue":
        r, g, b = 123, 104, 238
    elif color == "medium purple":
        r, g, b = 147, 112, 219
    elif color == "dark magenta":
        r, g, b = 139, 0, 139
    elif color == "dark violet":
        r, g, b = 148, 0, 211
    elif color == "dark orchid":
        r, g, b = 153, 50, 204
    elif color == "medium orchid":
        r, g, b = 186, 85, 211
    elif color == "purple":
        r, g, b = 128, 0, 128
    elif color == "thistle":
        r, g, b = 216, 191, 216
    elif color == "plum":
        r, g, b = 221, 160, 221
    elif color == "violet":
        r, g, b = 238, 130, 238
    elif color == "magenta":
        r, g, b = 255, 0, 255
    elif color == "orchid":
        r, g, b = 218, 112, 214
    elif color == "medium violet red":
        r, g, b = 199, 21, 133
    elif color == "pale violet red":
        r, g, b = 219, 112, 147
    elif color == "deep pink":
        r, g, b = 255, 20, 147
    elif color == "hot pink":
        r, g, b = 255, 105, 180
    elif color == "light pink":
        r, g, b = 255, 182, 193
    elif color == "pink":
        r, g, b = 255, 192, 203
    elif color == "antique white":
        r, g, b = 250, 235, 215
    elif color == "beige":
        r, g, b = 245, 245, 220
    elif color == "bisque":
        r, g, b = 255, 228, 196
    elif color == "blanched almond":
        r, g, b = 255, 235, 205
    elif color == "wheat":
        r, g, b = 245, 222, 179
    elif color == "corn silk":
        r, g, b = 255, 248, 220
    elif color == "lemon chiffon":
        r, g, b = 255, 250, 205
    elif color == "light golden rod yellow":
        r, g, b = 250, 250, 210
    elif color == "light yellow":
        r, g, b = 255, 255, 224
    elif color == "saddle brown":
        r, g, b = 139, 69, 19
    elif color == "sienna":
        r, g, b = 160, 82, 45
    elif color == "chocolate":
        r, g, b = 210, 105, 30
    elif color == "peru":
        r, g, b = 205, 133, 63
    elif color == "sandy brown":
        r, g, b = 244, 164, 96
    elif color == "burly wood":
        r, g, b = 222, 184, 135
    elif color == "tan":
        r, g, b = 210, 180, 140
    elif color == "rosy brown":
        r, g, b = 188, 143, 143
    elif color == "moccasin":
        r, g, b = 255, 228, 181
    elif color == "navajo white":
        r, g, b = 255, 222, 173
    elif color == "peach puff":
        r, g, b = 255, 218, 185
    elif color == "misty rose":
        r, g, b = 255, 228, 225
    elif color == "lavender blush":
        r, g, b = 255, 240, 245
    elif color == "linen":
        r, g, b = 250, 240, 230
    elif color == "old lace":
        r, g, b = 253, 245, 230
    elif color == "papaya whip":
        r, g, b = 255, 239, 213
    elif color == "sea shell":
        r, g, b = 255, 245, 238
    elif color == "mint cream":
        r, g, b = 245, 255, 250
    elif color == "slate gray":
        r, g, b = 112, 128, 144
    elif color == "light slate gray":
        r, g, b = 119, 136, 153
    elif color == "light steel blue":
        r, g, b = 176, 196, 222
    elif color == "lavender":
        r, g, b = 230, 230, 250
    elif color == "floral white":
        r, g, b = 255, 250, 240
    elif color == "alice blue":
        r, g, b = 240, 248, 255
    elif color == "ghost white":
        r, g, b = 248, 248, 255
    elif color == "honeydew":
        r, g, b = 240, 255, 240
    elif color == "ivory":
        r, g, b = 255, 255, 240
    elif color == "azure":
        r, g, b = 240, 255, 255
    elif color == "snow":
        r, g, b = 255, 250, 250
    elif color == "black":
        r, g, b = 0, 0, 0
    elif color == "dim gray":
        r, g, b = 105, 105, 105
    elif color == "gray":
        r, g, b = 128, 128, 128
    elif color == "dark gray":
        r, g, b = 169, 169, 169
    elif color == "silver":
        r, g, b = 192, 192, 192
    elif color == "light gray":
        r, g, b = 211, 211, 211
    elif color == "gainsboro":
        r, g, b = 220, 220, 220
    elif color == "white smoke":
        r, g, b = 245, 245, 245
    elif color == "white":
        r, g, b = 255, 255, 255
    else:
        r, g, b = 255, 255, 255

    return cs.format(r, g, b, string)
