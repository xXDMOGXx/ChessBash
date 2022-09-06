from tkinter import *
import random
random.seed()
# TO DO
# Fix Rook Bash with Malnutrition
# Finish Addons
# Make turn switching more obvious
width, height = 960, 540
size = 4
max_rounds = 15
rounds = 15
recruit_choices = 3
outline_tiles = False
menu_font = ('Helvetica', "20", 'bold')
turn_font = ('Helvetica', "30", 'bold')
announcement_font = ('Helvetica', "100", 'bold')
recruit_font = ('Helvetica', "50", 'bold')
paused = False
is_win = False
square_size = 0
offset = 0
left_bound = 0
top_bound = 0
current_player = 0
# Amnesia, Infiltration, Spring Cleaning, Brave Knight, Cowardly King, Malnutrition, Chivalry, Full Cast
modifiers = [False, False, False, False, False, False, False, False, False, False]
classic = False


class Player:
    def __init__(self, name, color, victory_speech="I Won!", defeat_speech="I Lost...", tie_speech="I Tied?", kill_animation=None):
        self.name = name
        self.color = color
        self.vs = victory_speech
        self.ds = defeat_speech
        self.ts = tie_speech
        self.ka = kill_animation
        self.recruit = None
        self.command = None


class Piece:
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.size = square_size
        self.body = None
        self.name_label = None
        self.owner_label = None
        if not name == "Empty":
            self.label_color = "#"+hex(from_hex("0xFFFFFF") - from_hex("0x"+owner.color[1:]))[2:]
            zero_add = 7 - len(self.label_color)
            self.label_color += "0"*zero_add

    def draw(self, canvas, location):
        xi = square_size/6
        yi = square_size/7
        x = left_bound + (square_size * location[0])
        y = top_bound + (square_size * location[1])
        xl = [x, x+xi, x+xi*2, x+xi*3, x+xi*4, x+xi*5, x+square_size]
        yl = [y, y+yi, y+yi*2, y+yi*3, y+yi*4, y+yi*5, y+yi*6, y+square_size]
        if self.name == "King":
            self.body = canvas.create_polygon(xl[0], yl[7], xl[2], yl[6], xl[0], yl[5], xl[2], yl[4], xl[1], yl[3], xl[3], yl[2], xl[2], yl[1],
                                              xl[3], yl[0], xl[4], yl[1], xl[3], yl[2], xl[5], yl[3], xl[4], yl[4], xl[6], yl[5], xl[4], yl[6], xl[6], yl[7], fill=self.owner.color)
        elif self.name == "Queen":
            self.body = canvas.create_polygon(xl[0], yl[7], xl[2], yl[6], xl[0], yl[5], xl[2], yl[4], xl[1], yl[3], xl[2], yl[2],
                                              xl[3], yl[1], xl[4], yl[2], xl[5], yl[3], xl[4], yl[4], xl[6], yl[5], xl[4], yl[6], xl[6], yl[7], fill=self.owner.color)
        elif self.name == "Bishop":
            self.body = canvas.create_polygon(xl[1], yl[7], xl[2], yl[6], xl[1], yl[5], xl[2], yl[4], xl[2], yl[2], xl[3], yl[3],
                                              xl[3], yl[1], xl[4], yl[3], xl[4], yl[4], xl[5], yl[5], xl[4], yl[6], xl[5], yl[7], fill=self.owner.color)
        elif self.name == "Knight":
            self.body = canvas.create_polygon(xl[1], yl[7], xl[1], yl[4], xl[3], yl[3], xl[1], yl[2],
                                              xl[5], yl[2], xl[6], yl[3], xl[4], yl[5], xl[5], yl[7], fill=self.owner.color)
        elif self.name == "Rook":
            self.body = canvas.create_polygon(xl[1], yl[7], xl[2], yl[3], xl[1], yl[2],
                                              xl[5], yl[2], xl[4], yl[3], xl[5], yl[7], fill=self.owner.color)
        elif self.name == "Pawn":
            self.body = canvas.create_polygon(xl[1], yl[7], xl[2], yl[6], xl[1], yl[5], xl[3], yl[4], xl[2], yl[3], xl[3], yl[2],
                                              xl[4], yl[3], xl[3], yl[4], xl[5], yl[5], xl[4], yl[6], xl[5], yl[7], fill=self.owner.color)
        self.name_label = canvas.create_text(x + self.size / 2, y + self.size*0.8, text=self.name, fill=self.label_color)
        self.owner_label = canvas.create_text(x + self.size / 2, y + self.size*0.95, text=self.owner.name, fill=self.label_color)

    def move(self, canvas, c_location, n_location):
        x0 = left_bound + (square_size * c_location[0])
        y0 = top_bound + (square_size * c_location[1])
        x1 = left_bound + (square_size * n_location[0])
        y1 = top_bound + (square_size * n_location[1])
        if self.body is not None:
            canvas.move(self.body, x1 - x0, y1 - y0)
            canvas.tag_raise(self.body)
        if self.name_label is not None:
            canvas.move(self.name_label, x1 - x0, y1 - y0)
            canvas.tag_raise(self.name_label)
        if self.owner_label is not None:
            canvas.move(self.owner_label, x1 - x0, y1 - y0)
            canvas.tag_raise(self.owner_label)

    def destroy(self, canvas):
        if self.owner_label is not None:
            canvas.delete(self.owner_label)
        if self.name_label is not None:
            canvas.delete(self.name_label)
        if self.body is not None:
            canvas.delete(self.body)


def from_hex(hexdigits):
    return int(hexdigits, 16)


def draw_piece(canvas, piece, location, draw_size, color="black", stipple="gray100"):
    xi = draw_size/6
    yi = draw_size/7
    x = location[0]
    y = location[1]
    xl = [x, x+xi, x+xi*2, x+xi*3, x+xi*4, x+xi*5, x+draw_size]
    yl = [y, y+yi, y+yi*2, y+yi*3, y+yi*4, y+yi*5, y+yi*6, y+draw_size]
    if piece == "King":
        return canvas.create_polygon(xl[0], yl[7], xl[2], yl[6], xl[0], yl[5], xl[2], yl[4], xl[1], yl[3], xl[3], yl[2], xl[2], yl[1],
                                     xl[3], yl[0], xl[4], yl[1], xl[3], yl[2], xl[5], yl[3], xl[4], yl[4], xl[6], yl[5], xl[4], yl[6], xl[6], yl[7], fill=color, stipple=stipple)
    elif piece == "Queen":
        return canvas.create_polygon(xl[0], yl[7], xl[2], yl[6], xl[0], yl[5], xl[2], yl[4], xl[1], yl[3], xl[2], yl[2],
                                     xl[3], yl[1], xl[4], yl[2], xl[5], yl[3], xl[4], yl[4], xl[6], yl[5], xl[4], yl[6], xl[6], yl[7], fill=color, stipple=stipple)
    elif piece == "Bishop":
        return canvas.create_polygon(xl[1], yl[7], xl[2], yl[6], xl[1], yl[5], xl[2], yl[4], xl[2], yl[2], xl[3], yl[3],
                                     xl[3], yl[1], xl[4], yl[3], xl[4], yl[4], xl[5], yl[5], xl[4], yl[6], xl[5], yl[7], fill=color, stipple=stipple)
    elif piece == "Knight":
        return canvas.create_polygon(xl[1], yl[7], xl[1], yl[4], xl[3], yl[3], xl[1], yl[2],
                                     xl[5], yl[2], xl[6], yl[3], xl[4], yl[5], xl[5], yl[7], fill=color, stipple=stipple)
    elif piece == "Rook":
        return canvas.create_polygon(xl[1], yl[7], xl[2], yl[3], xl[1], yl[2],
                                     xl[5], yl[2], xl[4], yl[3], xl[5], yl[7], fill=color, stipple=stipple)
    elif piece == "Pawn":
        return canvas.create_polygon(xl[1], yl[7], xl[2], yl[6], xl[1], yl[5], xl[3], yl[4], xl[2], yl[3], xl[3], yl[2],
                                     xl[4], yl[3], xl[3], yl[4], xl[5], yl[5], xl[4], yl[6], xl[5], yl[7], fill=color, stipple=stipple)


def animate_object(canvas, obj, path, function=None, frame_rate=24, fade=False, delayed=False, counter=-1, path_step=1, amount=(0.0, 0.0), rate=0, fade_screen=-1):
    if paused:
        canvas.master.after(round(path[4*path_step-2]*1000), lambda: animate_object(canvas, obj, path, function, frame_rate, fade, delayed, counter, path_step, amount, rate, fade_screen))
    else:
        c = canvas.coords(obj)
        if not c:
            return
        if fade:
            fade = False
            fade_screen = canvas.create_rectangle(0, 0, width, height, fill="black", stipple='gray50')
            canvas.tag_raise(obj)
        x = c[0]
        y = c[1]
        if not delayed:
            delayed = True
            canvas.master.after(round(path[4*path_step-2]*1000), lambda: animate_object(canvas, obj, path, function, frame_rate, fade, delayed, counter, path_step, amount, rate, fade_screen))
        else:
            if counter == -1:
                if path_step == 1:
                    canvas.move(obj, path[0] - x, path[1] - y)
                counter = round(frame_rate*path[4*path_step-1])
                if counter == 0:
                    counter = 1
                c = canvas.coords(obj)
                x = c[0]
                y = c[1]
                amount = ((path[4*path_step]-x)/counter, (path[4*path_step+1]-y)/counter)
                rate = round(1000/frame_rate)
                canvas.master.after(rate, lambda: animate_object(canvas, obj, path, function, counter=counter, amount=amount, rate=rate, path_step=path_step, delayed=delayed, fade_screen=fade_screen))
            else:
                counter -= 1
                canvas.move(obj, amount[0], amount[1])
                if counter <= 0:
                    if (len(path) - 2) / path_step == 4:
                        if not fade_screen == -1:
                            canvas.delete(fade_screen)
                        if function is not None:
                            function()
                    else:
                        path_step += 1
                        canvas.master.after(rate, lambda: animate_object(canvas, obj, path, function, amount=amount, rate=rate, path_step=path_step, fade_screen=fade_screen))
                else:
                    canvas.master.after(rate, lambda: animate_object(canvas, obj, path, function, counter=counter, amount=amount, rate=rate, path_step=path_step, delayed=delayed, fade_screen=fade_screen))


def recruit_round(canvas, field, pieces, player_list, text_list):
    for text in text_list:
        canvas.delete(text)
    for y in range(size):
        for x in range(size):
            if pieces[x][y].body is not None:
                canvas.tag_unbind(pieces[x][y].body, "<Button-1>")
    if modifiers[7]:
        path = [-400, height/2, 1, 0.5, width/2, height/2, 1, 0.1, width+400, height/2]
        round_text = canvas.create_text(0, -200, text="Command!", font=announcement_font, fill="red")
        animate_object(canvas, round_text, path, fade=True, function=lambda: command_round(canvas, field, pieces, player_list))
        return
    possible_pieces = ["Pawn", "Knight", "Rook", "Bishop"]
    random_set = []
    item_list = [canvas.create_rectangle(0, 0, width, height, fill="black", stipple='gray50')]
    mid = height / 2
    interval = width / (recruit_choices + 1)
    partial = interval / 3
    y0 = mid - partial
    y1 = mid + partial
    row_open_list = [False, False, False, False]
    for rx in range(size):
        if pieces[rx][0].name == "Empty":
            row_open_list[2] = True
        if pieces[rx][1].name == "Empty":
            row_open_list[3] = True
        if pieces[rx][size-1].name == "Empty":
            row_open_list[0] = True
        if pieces[rx][size-2].name == "Empty":
            row_open_list[1] = True
    random_pieces = []
    mod3 = False
    if row_open_list[0]:
        if modifiers[0]:
            random_pieces.append(possible_pieces[random.randrange(0, len(possible_pieces))])
        else:
            random_pieces.append(-1)
        item_list.append(canvas.create_text(width/2, 50, text=player_list[current_player].name+"'s Turn", fill="white", font=turn_font))
    elif row_open_list[1]:
        if modifiers[2]:
            mod3 = True
        random_pieces.append("Pawn")
        item_list.append(canvas.create_text(width/2, 50, text=player_list[1].name+"'s Turn", fill="white", font=turn_font))
    else:
        if modifiers[2]:
            mod3 = True
        random_pieces.append("None")
        item_list.append(canvas.create_text(width/2, 50, text=player_list[1].name+"'s Turn", fill="white", font=turn_font))
    if row_open_list[2]:
        if modifiers[0]:
            random_pieces.append(possible_pieces[random.randrange(0, len(possible_pieces))])
        else:
            random_pieces.append(-1)
    elif row_open_list[3]:
        if modifiers[2]:
            if mod3:
                end_game(canvas, player_list, None, text_list)
                return
            else:
                end_game(canvas, player_list, player_list[0], text_list)
                return
        else:
            random_pieces.append("Pawn")
    else:
        if modifiers[2]:
            if mod3:
                end_game(canvas, player_list, None, text_list)
                return
            else:
                end_game(canvas, player_list, player_list[0], text_list)
                return
        else:
            random_pieces.append("None")
    if mod3:
        end_game(canvas, player_list, player_list[1], text_list)
        return
    if ((random_pieces[0] == "Pawn" or random_pieces[0] == "None") and (random_pieces[1] == "Pawn" or random_pieces[1] == "None")) or modifiers[0]:
        recruit_piece(canvas, field, pieces, player_list, item_list, None, random_pieces)
    else:
        for i in range(recruit_choices):
            x = interval * (i + 1)
            x0 = x - partial
            x1 = x + partial
            random_piece = possible_pieces[random.randrange(0, len(possible_pieces))]
            if random_piece in random_set:
                random_piece = possible_pieces[random.randrange(0, len(possible_pieces))]
            random_set.append(random_piece)
            box = canvas.create_rectangle(x0, y0, x1, y1, fill="blue", stipple='gray75')
            model = draw_piece(canvas, random_piece, (x0, y0), x1-x0, "red", "gray75")
            recruit_text = canvas.create_text(x, mid, text=random_set[i], fill="white", font=recruit_font)
            item_list.append(box)
            item_list.append(model)
            item_list.append(recruit_text)
            canvas.tag_bind(box, "<Button-1>", lambda event, piece=random_piece: recruit_piece(canvas, field, pieces, player_list, item_list, piece, random_pieces))
            canvas.tag_bind(model, "<Button-1>", lambda event, piece=random_piece: recruit_piece(canvas, field, pieces, player_list, item_list, piece, random_pieces))
            canvas.tag_bind(recruit_text, "<Button-1>", lambda event, piece=random_piece: recruit_piece(canvas, field, pieces, player_list, item_list, piece, random_pieces))


def recruit_piece(canvas, field, pieces, player_list, item_list, piece, random_pieces):
    global current_player
    if random_pieces[0] == -1:
        if modifiers[1]:
            player_list[1].recruit = piece
        else:
            player_list[0].recruit = piece
        random_pieces[0] = -2
    elif not random_pieces[0] == -2:
        player_list[0].recruit = random_pieces[0]
        current_player += 1
    if random_pieces[1] == -1:
        if modifiers[1]:
            player_list[0].recruit = piece
        else:
            player_list[1].recruit = piece
    else:
        player_list[1].recruit = random_pieces[1]
        current_player += 1
    if current_player >= len(player_list)-1:
        current_player = 0
        canvas.delete(item_list[0])
        for item in item_list:
            canvas.delete(item)
        path = [-300, height/2, 1, 0.5, width/2, height/2, 1, 0.1, width+300, height/2]
        round_text = canvas.create_text(0, -200, text="Draft!", font=announcement_font, fill="red")
        animate_object(canvas, round_text, path, fade=True, function=lambda: draft_round(canvas, field, pieces, player_list))
    else:
        current_player += 1
        canvas.delete(item_list[1])
        turn_text = canvas.create_text(width/2, 50, text=player_list[current_player].name+"'s Turn", fill="white", font=turn_font)
        item_list.insert(1, turn_text)
        canvas.tag_raise(turn_text)


def draft_round(canvas, field, pieces, player_list, draft_list=None):
    global current_player
    if draft_list is None:
        draft_list = []
    recruit_display_list = []
    turn_text = 0
    if not current_player >= len(player_list):
        turn_text = canvas.create_text(width/2, 50, text=player_list[current_player].name+": Place "+player_list[current_player].recruit, fill="white", font=turn_font)
    if current_player == 1:
        if player_list[1].recruit == "None":
            canvas.delete(turn_text)
            current_player += 1
            draft_round(canvas, field, pieces, player_list, draft_list)
        else:
            for i in range(size):
                if pieces[i][0].name == "Empty":
                    dx = left_bound + (square_size * i)
                    dy = top_bound + (square_size * 0)
                    recruit_display = canvas.create_rectangle(dx, dy, dx + square_size, dy + square_size, fill="#0038a6", stipple="gray50")
                    recruit_display_list.append(recruit_display)
                    canvas.tag_bind(recruit_display, "<Button-1>", lambda event, x=i, y=0: draft_piece(canvas, field, pieces, player_list, turn_text, recruit_display_list, (x, y), draft_list))
            if player_list[1].recruit == "Pawn":
                for i in range(size):
                    if pieces[i][1].name == "Empty":
                        dx = left_bound + (square_size * i)
                        dy = top_bound + (square_size * 1)
                        recruit_display = canvas.create_rectangle(dx, dy, dx + square_size, dy + square_size, fill="#0038a6", stipple="gray50")
                        recruit_display_list.append(recruit_display)
                        canvas.tag_bind(recruit_display, "<Button-1>", lambda event, x=i, y=1: draft_piece(canvas, field, pieces, player_list, turn_text, recruit_display_list, (x, y), draft_list))
        canvas.tag_raise(turn_text)
    elif current_player == 0:
        if player_list[0].recruit == "None":
            canvas.delete(turn_text)
            current_player += 1
            draft_round(canvas, field, pieces, player_list, draft_list)
        else:
            for i in range(size):
                if pieces[i][size-1].name == "Empty":
                    dx = left_bound + (square_size * i)
                    dy = top_bound + (square_size * (size-1))
                    recruit_display = canvas.create_rectangle(dx, dy, dx + square_size, dy + square_size, fill="#0038a6", stipple="gray50")
                    recruit_display_list.append(recruit_display)
                    canvas.tag_bind(recruit_display, "<Button-1>", lambda event, x=i, y=size-1: draft_piece(canvas, field, pieces, player_list, turn_text, recruit_display_list, (x, y), draft_list))
            if player_list[0].recruit == "Pawn":
                for i in range(size):
                    if pieces[i][size-2].name == "Empty":
                        dx = left_bound + (square_size * i)
                        dy = top_bound + (square_size * (size-2))
                        recruit_display = canvas.create_rectangle(dx, dy, dx + square_size, dy + square_size, fill="#0038a6", stipple="gray50")
                        recruit_display_list.append(recruit_display)
                        canvas.tag_bind(recruit_display, "<Button-1>", lambda event, x=i, y=size-2: draft_piece(canvas, field, pieces, player_list, turn_text, recruit_display_list, (x, y), draft_list))
        canvas.tag_raise(turn_text)
    else:
        for draft in draft_list:
            draft[0].draw(canvas, (draft[1], draft[2]))
        current_player = 0
        path = [-400, height/2, 1, 0.5, width/2, height/2, 1, 0.1, width+400, height/2]
        round_text = canvas.create_text(0, -200, text="Command!", font=announcement_font, fill="red")
        animate_object(canvas, round_text, path, fade=True, function=lambda: command_round(canvas, field, pieces, player_list))


def draft_piece(canvas, field, pieces, player_list, turn_text, recruit_display, location, draft_list):
    global current_player
    canvas.delete(turn_text)
    for display in recruit_display:
        canvas.delete(display)
    pieces[location[0]][location[1]] = Piece(player_list[current_player].recruit, player_list[current_player])
    draft_list.append([pieces[location[0]][location[1]], location[0], location[1]])
    current_player += 1
    for y in range(size):
        for x in range(size):
            canvas.tag_unbind(field[x][y], "<Button-1>")
    draft_round(canvas, field, pieces, player_list, draft_list)


def command_round(canvas, field, pieces, player_list):
    global current_player
    if not current_player + 1 > len(player_list):
        turn_text = canvas.create_text(width/2, 50, text=player_list[current_player].name+"'s Turn ", fill="white", font=turn_font)
        for y in range(size):
            for x in range(size):
                if pieces[x][y].owner == player_list[current_player]:
                    canvas.tag_bind(pieces[x][y].body, "<Button-1>", lambda event, nx=x, ny=y: select_piece(canvas, field, pieces, player_list, turn_text, (nx, ny)))
                    canvas.tag_bind(pieces[x][y].name_label, "<Button-1>", lambda event, nx=x, ny=y: select_piece(canvas, field, pieces, player_list, turn_text, (nx, ny)))
                    canvas.tag_bind(pieces[x][y].owner_label, "<Button-1>", lambda event, nx=x, ny=y: select_piece(canvas, field, pieces, player_list, turn_text, (nx, ny)))
    else:
        current_player = 0
        path = [-400, height/2, 1, 0.5, width/2, height/2, 1, 0.1, width+400, height/2]
        round_text = canvas.create_text(0, -200, text="Battle!", font=announcement_font, fill="red")
        animate_object(canvas, round_text, path, fade=True, function=lambda: battle_round(canvas, field, pieces, player_list))


def calculate_possible_moves(pieces, player_list, location):
    possible_moves = []
    piece = pieces[location[0]][location[1]]
    if piece.name == "King":
        if not location[0] == 0:
            if modifiers[3] or not pieces[location[0]-1][location[1]].owner == player_list[current_player]:
                possible_moves.append((location[0]-1, location[1]))
            if modifiers[3] or not location[1] == 0:
                if not pieces[location[0]-1][location[1]-1].owner == player_list[current_player]:
                    possible_moves.append((location[0]-1, location[1]-1))
            if modifiers[3] or not location[1] == size-1:
                if not pieces[location[0]-1][location[1]+1].owner == player_list[current_player]:
                    possible_moves.append((location[0]-1, location[1]+1))
        if not location[0] == size-1:
            if modifiers[3] or not pieces[location[0]+1][location[1]].owner == player_list[current_player]:
                possible_moves.append((location[0]+1, location[1]))
            if modifiers[3] or not location[1] == 0:
                if not pieces[location[0]+1][location[1]-1].owner == player_list[current_player]:
                    possible_moves.append((location[0]+1, location[1]-1))
            if modifiers[3] or not location[1] == size-1:
                if not pieces[location[0]+1][location[1]+1].owner == player_list[current_player]:
                    possible_moves.append((location[0]+1, location[1]+1))
        if not location[1] == 0:
            if modifiers[3] or not pieces[location[0]][location[1]-1].owner == player_list[current_player]:
                possible_moves.append((location[0], location[1]-1))
        if not location[1] == size-1:
            if modifiers[3] or not pieces[location[0]][location[1]+1].owner == player_list[current_player]:
                possible_moves.append((location[0], location[1]+1))
    if piece.name == "Knight":
        if not location[1] <= 1:
            if not location[0] == 0:
                if modifiers[3] or not pieces[location[0]-1][location[1]-2].owner == player_list[current_player]:
                    possible_moves.append((location[0]-1, location[1]-2))
            if not location[0] == size-1:
                if modifiers[3] or not pieces[location[0]+1][location[1]-2].owner == player_list[current_player]:
                    possible_moves.append((location[0]+1, location[1]-2))
        if not location[1] >= size-2:
            if not location[0] == 0:
                if modifiers[3] or not pieces[location[0]-1][location[1]+2].owner == player_list[current_player]:
                    possible_moves.append((location[0]-1, location[1]+2))
            if not location[0] == size-1:
                if modifiers[3] or not pieces[location[0]+1][location[1]+2].owner == player_list[current_player]:
                    possible_moves.append((location[0]+1, location[1]+2))
        if not location[0] <= 1:
            if not location[1] == 0:
                if modifiers[3] or not pieces[location[0]-2][location[1]-1].owner == player_list[current_player]:
                    possible_moves.append((location[0]-2, location[1]-1))
            if not location[1] == size-1:
                if modifiers[3] or not pieces[location[0]-2][location[1]+1].owner == player_list[current_player]:
                    possible_moves.append((location[0]-2, location[1]+1))
        if not location[0] >= size-2:
            if not location[1] == 0:
                if modifiers[3] or not pieces[location[0]+2][location[1]-1].owner == player_list[current_player]:
                    possible_moves.append((location[0]+2, location[1]-1))
            if not location[1] == size-1:
                if modifiers[3] or not pieces[location[0]+2][location[1]+1].owner == player_list[current_player]:
                    possible_moves.append((location[0]+2, location[1]+1))
    if piece.name == "Pawn":
        if piece.owner == player_list[0]:
            if not location[1] == 0:
                if pieces[location[0]][location[1]-1].name == "Empty":
                    possible_moves.append((location[0], location[1]-1))
            if not location[0] == 0:
                if modifiers[3] or pieces[location[0]-1][location[1]-1].owner == player_list[1]:
                    possible_moves.append((location[0]-1, location[1]-1))
            if not location[0] == size-1:
                if modifiers[3] or pieces[location[0]+1][location[1]-1].owner == player_list[1]:
                    possible_moves.append((location[0]+1, location[1]-1))
        elif piece.owner == player_list[1]:
            if not location[1] == size-1:
                if pieces[location[0]][location[1]+1].name == "Empty":
                    possible_moves.append((location[0], location[1]+1))
            if not location[0] == 0:
                if modifiers[3] or pieces[location[0]-1][location[1]+1].owner == player_list[0]:
                    possible_moves.append((location[0]-1, location[1]+1))
            if not location[0] == size-1:
                if modifiers[3] or pieces[location[0]+1][location[1]+1].owner == player_list[0]:
                    possible_moves.append((location[0]+1, location[1]+1))
    if piece.name == "Rook" or piece.name == "Queen":
        for i in range(location[1]):
            if modifiers[3] or not pieces[location[0]][location[1]-(i+1)].owner == player_list[current_player]:
                possible_moves.append((location[0], location[1]-(i+1)))
            if not pieces[location[0]][location[1]-(i+1)].name == "Empty":
                break
        for i in range(size-(location[1]+1)):
            if modifiers[3] or not pieces[location[0]][location[1]+(i+1)].owner == player_list[current_player]:
                possible_moves.append((location[0], location[1]+(i+1)))
            if not pieces[location[0]][location[1]+(i+1)].name == "Empty":
                break
        for i in range(location[0]):
            if modifiers[3] or not pieces[location[0]-(i+1)][location[1]].owner == player_list[current_player]:
                possible_moves.append((location[0]-(i+1), location[1]))
            if not pieces[location[0]-(i+1)][location[1]].name == "Empty":
                break
        for i in range(size-(location[0]+1)):
            if modifiers[3] or not pieces[location[0]+(i+1)][location[1]].owner == player_list[current_player]:
                possible_moves.append((location[0]+(i+1), location[1]))
            if not pieces[location[0]+(i+1)][location[1]].name == "Empty":
                break
    if piece.name == "Bishop" or piece.name == "Queen":
        for i in range(min(location[0], location[1])):
            if modifiers[3] or not pieces[location[0]-(i+1)][location[1]-(i+1)].owner == player_list[current_player]:
                possible_moves.append((location[0]-(i+1), location[1]-(i+1)))
            if not pieces[location[0]-(i+1)][location[1]-(i+1)].name == "Empty":
                break
        for i in range(min(location[0], size-(location[1]+1))):
            if modifiers[3] or not pieces[location[0]-(i+1)][location[1]+(i+1)].owner == player_list[current_player]:
                possible_moves.append((location[0]-(i+1), location[1]+(i+1)))
            if not pieces[location[0]-(i+1)][location[1]+(i+1)].name == "Empty":
                break
        for i in range(min(size-(location[0]+1), location[1])):
            if modifiers[3] or not pieces[location[0]+(i+1)][location[1]-(i+1)].owner == player_list[current_player]:
                possible_moves.append((location[0]+(i+1), location[1]-(i+1)))
            if not pieces[location[0]+(i+1)][location[1]-(i+1)].name == "Empty":
                break
        for i in range(min(size-(location[0]+1), size-(location[1]+1))):
            if modifiers[3] or not pieces[location[0]+(i+1)][location[1]+(i+1)].owner == player_list[current_player]:
                possible_moves.append((location[0]+(i+1), location[1]+(i+1)))
            if not pieces[location[0]+(i+1)][location[1]+(i+1)].name == "Empty":
                break
    return possible_moves


def select_piece(canvas, field, pieces, player_list, turn_text, location):
    for y in range(size):
        for x in range(size):
            if pieces[x][y].owner == player_list[current_player]:
                canvas.tag_unbind(pieces[x][y].body, "<Button-1>")
    moves = calculate_possible_moves(pieces, player_list, location)
    move_display_list = []
    for move in moves:
        x = left_bound + (square_size * move[0])
        y = top_bound + (square_size * move[1])
        move_display = canvas.create_rectangle(x, y, x + square_size, y + square_size, fill="#0038a6", stipple="gray50", outline="#0038a6")
        move_display_list.append(move_display)
        canvas.tag_raise(turn_text)
        if pieces[move[0]][move[1]].body is not None:
            canvas.tag_bind(pieces[move[0]][move[1]].body, "<Button-1>", lambda event, nx=move[0], ny=move[1], l0=location[0], l1=location[1]: command_piece(canvas, field, pieces, player_list, turn_text, move_display_list, (l0, l1), (nx, ny)))
        if pieces[move[0]][move[1]].name_label is not None:
            canvas.tag_bind(pieces[move[0]][move[1]].name_label, "<Button-1>", lambda event, nx=move[0], ny=move[1], l0=location[0], l1=location[1]: command_piece(canvas, field, pieces, player_list, turn_text, move_display_list, (l0, l1), (nx, ny)))
        if pieces[move[0]][move[1]].owner_label is not None:
            canvas.tag_bind(pieces[move[0]][move[1]].owner_label, "<Button-1>", lambda event, nx=move[0], ny=move[1], l0=location[0], l1=location[1]: command_piece(canvas, field, pieces, player_list, turn_text, move_display_list, (l0, l1), (nx, ny)))
        canvas.tag_bind(move_display, "<Button-1>", lambda event, nx=move[0], ny=move[1], l0=location[0], l1=location[1]: command_piece(canvas, field, pieces, player_list, turn_text, move_display_list, (l0, l1), (nx, ny)))
    x = left_bound + (square_size * location[0])
    y = top_bound + (square_size * location[1])
    select_display = canvas.create_rectangle(x, y, x + square_size, y + square_size, fill="#ff3b3b", stipple="gray50", outline="#ff3b3b")
    canvas.tag_bind(select_display, "<Button-1>", lambda event: unselect_piece(canvas, field, pieces, player_list, turn_text, move_display_list))
    move_display_list.append(select_display)


def unselect_piece(canvas, field, pieces, player_list, turn_text, move_display_list):
    for y in range(size):
        for x in range(size):
            if pieces[x][y].body is not None:
                canvas.tag_unbind(pieces[x][y].body, "<Button-1>")
    canvas.delete(turn_text)
    for display in move_display_list:
        canvas.delete(display)
    command_round(canvas, field, pieces, player_list)


def command_piece(canvas, field, pieces, player_list, turn_text, move_display_list, old_location, location):
    global current_player
    canvas.delete(turn_text)
    for display in move_display_list:
        canvas.delete(display)
    player_list[current_player].command = [(old_location[0], old_location[1]), (location[0], location[1])]
    current_player += 1
    unselect_piece(canvas, field, pieces, player_list, turn_text, move_display_list)


def battle_round(canvas, field, pieces, player_list):
    global rounds
    global is_win
    decisive_path = [-400, height/2, 1, 0.5, width/2, height/2, 3, 0.1, width+400, height/2]
    inconclusive_path = [-400, height/2, 1, 0.5, width/2, height/2, 1, 0.1, width+400, height/2]
    description_path = [-1000, height/2+100, 1.5, 0, width/2, height/2+100, 3, 0, width+1000, height/2+100]
    i_description_path = [-1000, height/2+100, 1.5, 0, width/2, height/2+100, 1, 0, width+1000, height/2+100]
    empty_piece = Piece("Empty", None)
    text_list = []
    result_text = False
    description_text = False
    p1_init_x, p1_init_y = player_list[0].command[0]
    p1_move_x, p1_move_y = player_list[0].command[1]
    p2_init_x, p2_init_y = player_list[1].command[0]
    p2_move_x, p2_move_y = player_list[1].command[1]
    p1_piece = pieces[p1_init_x][p1_init_y]
    p2_piece = pieces[p2_init_x][p2_init_y]
    if p1_move_x == p2_move_x and p1_move_y == p2_move_y:
        if p1_piece.name == "King" and p2_piece.name == "King":
            is_win = True
            p1_piece.destroy(canvas)
            pieces[p1_init_x][p1_init_y] = empty_piece
            p2_piece.destroy(canvas)
            pieces[p2_init_x][p2_init_y] = empty_piece
            result_text = canvas.create_text(0, -200, text="Bash!", font=announcement_font, fill="red")
            description_text = canvas.create_text(0, -200, text="Both Kings Destroyed!", font=turn_font, fill="blue")
            text_list.append(result_text)
            text_list.append(description_text)
            canvas.tag_raise(result_text)
            canvas.tag_raise(description_text)
            animate_object(canvas, result_text, decisive_path, fade=True, function=lambda: end_game(canvas, player_list, None, text_list))
            animate_object(canvas, description_text, description_path)
        elif p1_piece.name == "King" or p2_piece.name == "King":
            is_win = True
            if p1_piece.name == "King":
                p1_piece.destroy(canvas)
                pieces[p1_init_x][p1_init_y] = empty_piece
                p2_piece.move(canvas, (p2_init_x, p2_init_y), (p2_move_x, p2_move_y))
                pieces[p2_init_x][p2_init_y] = empty_piece
                pieces[p2_move_x][p2_move_y] = p2_piece
                result_text = canvas.create_text(0, -200, text="Bash!", font=announcement_font, fill="red")
                description_text = canvas.create_text(0, -200, text=player_list[0].name+"'s King Destroyed!", font=turn_font, fill="blue")
                text_list.append(result_text)
                text_list.append(description_text)
                canvas.tag_raise(result_text)
                canvas.tag_raise(description_text)
                animate_object(canvas, result_text, decisive_path, fade=True, function=lambda: end_game(canvas, player_list, player_list[1], text_list))
                animate_object(canvas, description_text, description_path)
            elif p2_piece.name == "King":
                is_win = True
                p2_piece.destroy(canvas)
                pieces[p2_init_x][p2_init_y] = empty_piece
                p1_piece.move(canvas, (p1_init_x, p1_init_y), (p1_move_x, p1_move_y))
                pieces[p1_init_x][p1_init_y] = empty_piece
                pieces[p1_move_x][p1_move_y] = p1_piece
                result_text = canvas.create_text(0, -200, text="Bash!", font=announcement_font, fill="red")
                description_text = canvas.create_text(0, -200, text=player_list[1].name+"'s King Destroyed!", font=turn_font, fill="blue")
                text_list.append(result_text)
                text_list.append(description_text)
                canvas.tag_raise(result_text)
                canvas.tag_raise(description_text)
                animate_object(canvas, result_text, decisive_path, fade=True, function=lambda: end_game(canvas, player_list, player_list[0], text_list))
                animate_object(canvas, description_text, description_path)
        else:
            result_text = canvas.create_text(0, -200, text="Bash!", font=announcement_font, fill="red")
            description_text = canvas.create_text(0, -200, text="Troops Remain!", font=turn_font, fill="blue")
            text_list.append(result_text)
            text_list.append(description_text)
            canvas.tag_raise(result_text)
            canvas.tag_raise(description_text)
            animate_object(canvas, result_text, inconclusive_path, fade=True)
            animate_object(canvas, description_text, i_description_path)
            if modifiers[5]:
                if p1_init_x < p1_move_x:
                    p1_mod_x = p1_move_x - 1
                elif p1_init_x > p1_move_x:
                    p1_mod_x = p1_move_x + 1
                else:
                    p1_mod_x = p1_move_x
                if p1_init_y < p1_move_y:
                    p1_mod_y = p1_move_y - 1
                elif p1_init_y > p1_move_y:
                    p1_mod_y = p1_move_y + 1
                else:
                    p1_mod_y = p1_move_y
                if p2_init_x < p2_move_x:
                    p2_mod_x = p2_move_x - 1
                elif p2_init_x > p2_move_x:
                    p2_mod_x = p2_move_x + 1
                else:
                    p2_mod_x = p2_move_x
                if p2_init_y < p2_move_y:
                    p2_mod_y = p2_move_y - 1
                elif p2_init_y > p2_move_y:
                    p2_mod_y = p2_move_y + 1
                else:
                    p2_mod_y = p2_move_y
                if not p1_init_x == p1_mod_x and not p1_init_y == p1_mod_y:
                    pieces[p1_mod_x][p1_mod_y].destroy(canvas)
                    p1_piece.move(canvas, (p1_init_x, p1_init_y), (p1_mod_x, p1_mod_y))
                    pieces[p1_init_x][p1_init_y] = empty_piece
                if not p2_init_x == p2_mod_x and not p2_init_y == p2_mod_y:
                    pieces[p2_mod_x][p2_mod_y].destroy(canvas)
                    p2_piece.move(canvas, (p2_init_x, p2_init_y), (p2_mod_x, p2_mod_y))
                    pieces[p2_init_x][p2_init_y] = empty_piece
                if p1_piece.name == "Pawn" and p1_mod_y == 0:
                    p1_piece.destroy(canvas)
                    p1_piece = Piece("Queen", player_list[0])
                    pieces[p1_mod_x][p1_mod_y] = p1_piece
                    p1_piece.draw(canvas, (p1_mod_x, p1_mod_y))
                else:
                    pieces[p1_mod_x][p1_mod_y] = p1_piece
                if p2_piece.name == "Pawn" and p2_mod_y == size-1:
                    p2_piece.destroy(canvas)
                    p2_piece = Piece("Queen", player_list[1])
                    pieces[p2_mod_x][p2_mod_y] = p2_piece
                    p2_piece.draw(canvas, (p2_mod_x, p2_mod_y))
                else:
                    pieces[p2_mod_x][p2_mod_y] = p2_piece
            rounds -= 1
            if not is_win:
                if rounds <= 0:
                    end_game(canvas, player_list, None, text_list)
                elif modifiers[7]:
                    path = [-400, height/2, 1, 0.5, width/2, height/2, 1, 0.1, width+400, height/2]
                    round_text = canvas.create_text(0, -200, text="Command!", font=announcement_font, fill="red")
                    animate_object(canvas, round_text, path, fade=True, function=lambda: command_round(canvas, field, pieces, player_list))
                else:
                    round_text = canvas.create_text(0, -200, text="Recruit!", font=announcement_font, fill="red")
                    text_list.append(round_text)
                    canvas.master.after(3000, lambda: animate_object(canvas, round_text, inconclusive_path, fade=True, function=lambda: recruit_round(canvas, field, pieces, player_list, text_list)))
    else:
        if pieces[p1_move_x][p1_move_y].name == "King" and pieces[p2_move_x][p2_move_y].name == "King" and not (p1_piece.name == "King" and p2_piece.name == "King"):
            is_win = True
            result_text = canvas.create_text(0, -200, text="Swoop!", font=announcement_font, fill="red")
            description_text = canvas.create_text(0, -200, text="Both Kings Captured!", font=turn_font, fill="blue")
            text_list.append(result_text)
            text_list.append(description_text)
            canvas.tag_raise(result_text)
            canvas.tag_raise(description_text)
            animate_object(canvas, result_text, decisive_path, fade=True, function=lambda: end_game(canvas, player_list, None, text_list))
            animate_object(canvas, description_text, description_path)
        elif (pieces[p1_move_x][p1_move_y].name == "King" and not p2_piece.name == "King") or (pieces[p2_move_x][p2_move_y].name == "King" and not p1_piece.name == "King"):
            is_win = True
            if pieces[p1_move_x][p1_move_y].name == "King" and not p2_piece.name == "King":
                result_text = canvas.create_text(0, -200, text="Swoop!", font=announcement_font, fill="red")
                description_text = canvas.create_text(0, -200, text=player_list[1].name+"'s King Captured!", font=turn_font, fill="blue")
                text_list.append(result_text)
                text_list.append(description_text)
                canvas.tag_raise(result_text)
                canvas.tag_raise(description_text)
                animate_object(canvas, result_text, decisive_path, fade=True, function=lambda: end_game(canvas, player_list, player_list[0], text_list))
                animate_object(canvas, description_text, description_path)
            elif pieces[p2_move_x][p2_move_y].name == "King" and not p1_piece.name == "King":
                result_text = canvas.create_text(0, -200, text="Swoop!", font=announcement_font, fill="red")
                description_text = canvas.create_text(0, -200, text=player_list[0].name+"'s King Captured!", font=turn_font, fill="blue")
                text_list.append(result_text)
                text_list.append(description_text)
                canvas.tag_raise(result_text)
                canvas.tag_raise(description_text)
                animate_object(canvas, result_text, decisive_path, fade=True, function=lambda: end_game(canvas, player_list, player_list[1], text_list))
                animate_object(canvas, description_text, description_path)
        elif (p1_move_x == p2_init_x and p1_move_y == p2_init_y) and (p2_move_x == p1_init_x and p2_move_y == p1_init_y):
            result_text = canvas.create_text(0, -200, text="SWAP!", font=announcement_font, fill="red")
            description_text = canvas.create_text(0, -200, text="Wait, What?", font=turn_font, fill="blue")
            text_list.append(result_text)
            text_list.append(description_text)
            animate_object(canvas, result_text, inconclusive_path, fade=True)
            animate_object(canvas, description_text, i_description_path)
        elif (p1_move_x == p2_init_x and p1_move_y == p2_init_y) or (p2_move_x == p1_init_x and p2_move_y == p1_init_y):
            result_text = canvas.create_text(0, -200, text="DODGE!", font=announcement_font, fill="red")
            description_text = canvas.create_text(0, -200, text="So Close!", font=turn_font, fill="blue")
            text_list.append(result_text)
            text_list.append(description_text)
            animate_object(canvas, result_text, inconclusive_path, fade=True)
            animate_object(canvas, description_text, i_description_path)
        if not pieces[p1_move_x][p1_move_y] == p2_piece:
            pieces[p1_move_x][p1_move_y].destroy(canvas)
        if not pieces[p2_move_x][p2_move_y] == p1_piece:
            pieces[p2_move_x][p2_move_y].destroy(canvas)
        p1_piece.move(canvas, (p1_init_x, p1_init_y), (p1_move_x, p1_move_y))
        p2_piece.move(canvas, (p2_init_x, p2_init_y), (p2_move_x, p2_move_y))
        pieces[p1_init_x][p1_init_y] = empty_piece
        pieces[p2_init_x][p2_init_y] = empty_piece
        if p1_piece.name == "Pawn" and p1_move_y == 0:
            p1_piece.destroy(canvas)
            p1_piece = Piece("Queen", player_list[0])
            pieces[p1_move_x][p1_move_y] = p1_piece
            p1_piece.draw(canvas, (p1_move_x, p1_move_y))
        else:
            pieces[p1_move_x][p1_move_y] = p1_piece
        if p2_piece.name == "Pawn" and p2_move_y == size-1:
            p2_piece.destroy(canvas)
            p2_piece = Piece("Queen", player_list[1])
            pieces[p2_move_x][p2_move_y] = p2_piece
            p2_piece.draw(canvas, (p2_move_x, p2_move_y))
        else:
            pieces[p2_move_x][p2_move_y] = p2_piece
        if result_text:
            canvas.tag_raise(result_text)
        if description_text:
            canvas.tag_raise(description_text)
        rounds -= 1
        if not is_win:
            if rounds <= 0:
                end_game(canvas, player_list, None, text_list)
            elif modifiers[7]:
                path = [-400, height/2, 1, 0.5, width/2, height/2, 1, 0.1, width+400, height/2]
                round_text = canvas.create_text(0, -200, text="Command!", font=announcement_font, fill="red")
                canvas.master.after(3000, lambda: animate_object(canvas, round_text, path, fade=True, function=lambda: command_round(canvas, field, pieces, player_list)))
            else:
                round_text = canvas.create_text(0, -200, text="Recruit!", font=announcement_font, fill="red")
                text_list.append(round_text)
                canvas.master.after(3000, lambda: animate_object(canvas, round_text, inconclusive_path, fade=True, function=lambda: recruit_round(canvas, field, pieces, player_list, text_list)))


def end_game(canvas, player_list, result, text_list):
    global rounds
    global is_win
    global current_player
    is_win = False
    for text in text_list:
        canvas.delete(text)
    rounds = max_rounds
    current_player = 0
    path = [-400, height/2, 1, 0.5, width/2, height/2, 3, 0.1, width+400, height/2]
    if result is None:
        result_text = canvas.create_text(0, -200, text="Tie!", font=announcement_font, fill="red")
        p1_tie_text = canvas.create_text(0, -200, text=player_list[0].name+": "+player_list[0].ts, font=turn_font, fill="blue")
        p2_tie_text = canvas.create_text(0, -200, text=player_list[1].name+": "+player_list[1].ts, font=turn_font, fill="blue")
        animate_object(canvas, result_text, path)
        animate_object(canvas, p1_tie_text, [-400, height/2+100, 1, 0.5, width/2, height/2+100, 3, 0.1, width+400, height/2+100])
        animate_object(canvas, p2_tie_text, [-400, height/2+150, 1, 0.5, width/2, height/2+150, 3, 0.1, width+400, height/2+150], function=lambda: setup_main_menu(canvas))
    else:
        player_list.remove(result)
        result_text = canvas.create_text(0, -200, text=result.name+" Wins!", font=announcement_font, fill="red")
        victory_text = canvas.create_text(0, -200, text=result.name+": "+result.vs, font=turn_font, fill="blue")
        defeat_text = canvas.create_text(0, -200, text=player_list[0].name+": "+player_list[0].ds, font=turn_font, fill="blue")
        animate_object(canvas, result_text, path)
        animate_object(canvas, victory_text, [-400, height/2+100, 1, 0.5, width/2, height/2+100, 3, 0.1, width+400, height/2+100])
        animate_object(canvas, defeat_text, [-400, height/2+150, 1, 0.5, width/2, height/2+150, 3, 0.1, width+400, height/2+150], function=lambda: setup_main_menu(canvas))


def setup_menu(canvas):
    global paused
    canvas.unbind('<Escape>')
    paused = True
    item_list = []
    cover = canvas.create_rectangle(0, 0, width, height, fill="#a1a1a1")
    item_list.append(cover)
    resume_button = canvas.create_rectangle(width/2-100, 300, width/2+100, 350, fill="gray")
    resume_text = canvas.create_text(width/2, 325, text="Resume", fill="black", font=menu_font)
    canvas.tag_bind(resume_button, "<Button-1>", lambda event: close_menu(canvas, item_list))
    canvas.tag_bind(resume_text, "<Button-1>", lambda event: close_menu(canvas, item_list))
    item_list.append(resume_button)
    item_list.append(resume_text)
    main_button = canvas.create_rectangle(width/2-100, 400, width/2+100, 450, fill="gray")
    main_text = canvas.create_text(width/2, 425, text="Main Menu", fill="black", font=menu_font)
    item_list.append(main_button)
    item_list.append(main_text)
    canvas.tag_bind(main_button, "<Button-1>", lambda event: close_menu(canvas, item_list, lambda: setup_main_menu(canvas)))
    canvas.tag_bind(main_text, "<Button-1>", lambda event: close_menu(canvas, item_list, lambda: setup_main_menu(canvas)))
    canvas.bind('<Escape>', lambda event: close_menu(canvas, item_list))


def close_menu(canvas, item_list, option=None):
    global paused
    canvas.bind('<Escape>', lambda event: setup_menu(canvas))
    paused = False
    for item in item_list:
        canvas.delete(item)
    if option is not None:
        option()


def setup_game(canvas):
    global square_size
    global offset
    global left_bound
    global top_bound
    global current_player
    canvas.delete('all')
    coldbeef = Player("coldbeef", "#ffffff", "EZ", "EZ", "EZ")
    xxdmogxx = Player("xXDMOGXx", "#3cb544", "Suck It!", "Fuck You", "Bitch...")
    player_list = [coldbeef, xxdmogxx]
    empty_piece = Piece("Empty", None)
    empty_line = [empty_piece]*size
    field = []
    pieces = []
    for i in range(size):
        field.append(empty_line.copy())
        pieces.append(empty_line.copy())
    if width < height:
        square_size = (width - 10) / len(field)
    else:
        square_size = (height - 10) / len(field)
    offset = (square_size * size) / 2
    left_bound = (width / 2) - offset
    top_bound = (height / 2) - offset
    if modifiers[9]:
        pieces[0][0] = Piece("Rook", player_list[1])
        pieces[1][0] = Piece("Knight", player_list[1])
        pieces[2][0] = Piece("Bishop", player_list[1])
        pieces[3][0] = Piece("Queen", player_list[1])
        pieces[4][0] = Piece("King", player_list[1])
        pieces[5][0] = Piece("Bishop", player_list[1])
        pieces[6][0] = Piece("Knight", player_list[1])
        pieces[7][0] = Piece("Rook", player_list[1])
        pieces[0][size-1] = Piece("Rook", player_list[0])
        pieces[1][size-1] = Piece("Knight", player_list[0])
        pieces[2][size-1] = Piece("Bishop", player_list[0])
        pieces[3][size-1] = Piece("Queen", player_list[0])
        pieces[4][size-1] = Piece("King", player_list[0])
        pieces[5][size-1] = Piece("Bishop", player_list[0])
        pieces[6][size-1] = Piece("Knight", player_list[0])
        pieces[7][size-1] = Piece("Rook", player_list[0])
        for i in range(8):
            pieces[i][1] = Piece("Pawn", player_list[1])
            pieces[i][size-2] = Piece("Pawn", player_list[0])
    else:
        pieces[size-1][size-1] = Piece("King", player_list[0])
        pieces[0][0] = Piece("King", player_list[1])
    draw_board(canvas, field, pieces)
    canvas.bind('<Escape>', lambda event: setup_menu(canvas))
    path = [-300, height/2, 1, 0.5, width/2, height/2, 1, 0.1, width+300, height/2]
    begin_text = canvas.create_text(0, -200, text="Begin!", font=announcement_font, fill="red")
    round_text = canvas.create_text(0, -200, text="Recruit!", font=announcement_font, fill="red")
    text_list = [begin_text, round_text]
    if modifiers[7]:
        animate_object(canvas, begin_text, path, fade=True, function=lambda: recruit_round(canvas, field, pieces, player_list, text_list))
    else:
        animate_object(canvas, begin_text, path, fade=True, function=lambda: animate_object(canvas, round_text, path, fade=True, function=lambda: recruit_round(canvas, field, pieces, player_list, text_list)))


def draw_board(canvas, field, pieces):
    canvas.delete('all')
    for y in range(size):
        y_pos = top_bound + (square_size * y)
        for x in range(size):
            x_pos = left_bound + (square_size * x)
            if (x + y) % 2 == 0:
                color = "#c7c281"
            else:
                color = "#303025"
            if outline_tiles:
                outline = 'black'
            else:
                outline = color
            field[x][y] = canvas.create_rectangle(x_pos, y_pos, x_pos + square_size, y_pos + square_size, fill=color, outline=outline)
            if not pieces[x][y].name == "Empty":
                pieces[x][y].draw(canvas, (x, y))


def change_setting(canvas, setting, value=None, optional=None, exclusive=None, multi=False):
    global size
    global classic
    if multi:
        for s in setting:
            if s[0] == "size":
                size = s[1]
                if size < 3:
                    size = 3
                elif size > 10:
                    size = 10
            elif s[0] == "mod":
                if s[1] == "bool":
                    if modifiers[s[2]]:
                        modifiers[s[2]] = False
                    else:
                        modifiers[s[2]] = True
                        if len(s) >= 4:
                            for mod in s[3]:
                                modifiers[mod] = False
                else:
                    modifiers[s[2]] = s[1]
                    if len(s) >= 4:
                        for mod in s[3]:
                            if s[1]:
                                modifiers[mod] = False
                            else:
                                modifiers[mod] = True
                            modifiers[mod] = False
            elif s[0] == "classic":
                if classic:
                    classic = False
                else:
                    classic = True
    else:
        if setting == "size":
            size = value
            if size < 3:
                size = 3
            elif size > 10:
                size = 10
        elif setting == "mod":
            if value == "bool":
                if modifiers[optional]:
                    modifiers[optional] = False
                else:
                    modifiers[optional] = True
                    if exclusive is not None:
                        for mod in exclusive:
                            modifiers[mod] = False
            else:
                modifiers[optional] = value
                for mod in exclusive:
                    if value:
                        modifiers[mod] = False
                    else:
                        modifiers[mod] = True
        elif setting == "classic":
            if classic:
                classic = False
            else:
                classic = True
    setup_settings(canvas)


def setup_settings(canvas):
    global size
    canvas.bind('<Escape>', lambda event: setup_main_menu(canvas))
    canvas.delete('all')
    if modifiers[9]:
        size = 8
    canvas.create_rectangle(width/2-100, 300, width/2+100, 350, fill="gray")
    canvas.create_text(width/2-25, 325, text="Size:", fill="black", font=menu_font)
    canvas.create_text(width/2+30, 325, text=str(size), fill="black", font=menu_font)
    if not modifiers[9]:
        if size < 10:
            size_increase_button = canvas.create_polygon(width/2+70, 320, width/2+80, 305, width/2+90, 320, fill="blue")
            canvas.tag_bind(size_increase_button, "<Button-1>", lambda event: change_setting(canvas, "size", size+1))
        if size > 3:
            size_decrease_button = canvas.create_polygon(width/2+70, 330, width/2+80, 345, width/2+90, 330, fill="blue")
            canvas.tag_bind(size_decrease_button, "<Button-1>", lambda event: change_setting(canvas, "size", size-1))
    canvas.create_text(width/2, 375, text="Modifiers", fill="black", font=turn_font)
    if modifiers[0]:
        mod0_button = canvas.create_rectangle(width/2-425, 400, width/2-25, 450, fill="#99ff91")
    else:
        mod0_button = canvas.create_rectangle(width/2-425, 400, width/2-25, 450, fill="#ff7878")
    mod0_text = canvas.create_text(width/2-225, 425, text="Amnesia", fill="black", font=menu_font)
    canvas.tag_bind(mod0_button, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 0, [1, 7, 9]))
    canvas.tag_bind(mod0_text, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 0, [1, 7, 9]))
    if modifiers[1]:
        mod1_button = canvas.create_rectangle(width/2+25, 400, width/2+425, 450, fill="#99ff91")
    else:
        mod1_button = canvas.create_rectangle(width/2+25, 400, width/2+425, 450, fill="#ff7878")
    mod1_text = canvas.create_text(width/2+225, 425, text="Infiltration", fill="black", font=menu_font)
    canvas.tag_bind(mod1_button, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 1, [0, 7, 9]))
    canvas.tag_bind(mod1_text, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 1, [0, 7, 9]))
    if modifiers[2]:
        mod2_button = canvas.create_rectangle(width/2-425, 475, width/2-25, 525, fill="#99ff91")
    else:
        mod2_button = canvas.create_rectangle(width/2-425, 475, width/2-25, 525, fill="#ff7878")
    mod2_text = canvas.create_text(width/2-225, 500, text="Spring Cleaning", fill="black", font=menu_font)
    canvas.tag_bind(mod2_button, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 2, [9, ]))
    canvas.tag_bind(mod2_text, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 2, [9, ]))
    if modifiers[3]:
        mod3_button = canvas.create_rectangle(width/2+25, 475, width/2+425, 525, fill="#99ff91")
    else:
        mod3_button = canvas.create_rectangle(width/2+25, 475, width/2+425, 525, fill="#ff7878")
    mod3_text = canvas.create_text(width/2+225, 500, text="Brave Knight", fill="black", font=menu_font)
    canvas.tag_bind(mod3_button, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 3))
    canvas.tag_bind(mod3_text, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 3))
    if modifiers[5]:
        mod5_button = canvas.create_rectangle(width/2+25, 550, width/2+425, 600, fill="#99ff91")
    else:
        mod5_button = canvas.create_rectangle(width/2+25, 550, width/2+425, 600, fill="#ff7878")
    mod5_text = canvas.create_text(width/2+225, 575, text="Malnutrition", fill="black", font=menu_font)
    canvas.tag_bind(mod5_button, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 5))
    canvas.tag_bind(mod5_text, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 5))
    if classic:
        mod6_button = canvas.create_rectangle(width/2-425, 625, width/2-25, 675, fill="#19bd1b")
    elif modifiers[6]:
        mod6_button = canvas.create_rectangle(width/2-425, 625, width/2-25, 675, fill="#99ff91")
    else:
        mod6_button = canvas.create_rectangle(width/2-425, 625, width/2-25, 675, fill="#ff7878")
    mod6_text = canvas.create_text(width/2-225, 650, text="Cowardly King", fill="black", font=menu_font)
    if not classic:
        canvas.tag_bind(mod6_button, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 6))
        canvas.tag_bind(mod6_text, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 6))
    if classic:
        mod7_button = canvas.create_rectangle(width/2+25, 625, width/2+425, 675, fill="#19bd1b")
    elif modifiers[7]:
        mod7_button = canvas.create_rectangle(width/2+25, 625, width/2+425, 675, fill="#99ff91")
    else:
        mod7_button = canvas.create_rectangle(width/2+25, 625, width/2+425, 675, fill="#ff7878")
    mod7_text = canvas.create_text(width/2+225, 650, text="Troop Shortage", fill="black", font=menu_font)
    if not classic:
        canvas.tag_bind(mod7_button, "<Button-1>", lambda event: change_setting(canvas, [["mod", "bool", 7, [0, 1]], ["mod", False, 9]], multi=True))
        canvas.tag_bind(mod7_text, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 7, [0, 1]))
    if classic:
        mod8_button = canvas.create_rectangle(width/2-425, 700, width/2-25, 750, fill="#19bd1b")
    elif modifiers[8]:
        mod8_button = canvas.create_rectangle(width/2-425, 700, width/2-25, 750, fill="#99ff91")
    else:
        mod8_button = canvas.create_rectangle(width/2-425, 700, width/2-25, 750, fill="#ff7878")
    mod8_text = canvas.create_text(width/2-225, 725, text="Chivalry", fill="black", font=menu_font)
    if not classic:
        canvas.tag_bind(mod8_button, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 8))
        canvas.tag_bind(mod8_text, "<Button-1>", lambda event: change_setting(canvas, "mod", "bool", 8))
    if classic:
        mod9_button = canvas.create_rectangle(width/2+25, 700, width/2+425, 750, fill="#19bd1b")
    elif modifiers[9]:
        mod9_button = canvas.create_rectangle(width/2+25, 700, width/2+425, 750, fill="#99ff91")
    else:
        mod9_button = canvas.create_rectangle(width/2+25, 700, width/2+425, 750, fill="#ff7878")
    mod9_text = canvas.create_text(width/2+225, 725, text="Full Cast", fill="black", font=menu_font)
    if not classic:
        canvas.tag_bind(mod9_button, "<Button-1>", lambda event: change_setting(canvas, [["mod", "bool", 9, [2, ]], ["mod", not modifiers[9], 7, [0, 1]]], multi=True))
        canvas.tag_bind(mod9_text, "<Button-1>", lambda event: change_setting(canvas, [["mod", "bool", 9, [2, ]], ["mod", not modifiers[9], 7, [0, 1]]], multi=True))
    if classic:
        classic_lcross = canvas.create_polygon(width/2-35, 675, width/2-25, 675, width/2-25, 665, width/2+35, 700, width/2+25, 700, width/2+25, 710, fill="#99ff91", outline="black")
        classic_rcross = canvas.create_polygon(width/2+35, 675, width/2+25, 675, width/2+25, 665, width/2-35, 700, width/2-25, 700, width/2-25, 710, fill="#99ff91", outline="black")
        classic_circle = canvas.create_oval(width/2+20, 667.5, width/2-20, 707.5, fill="#99ff91")
    else:
        classic_lcross = canvas.create_polygon(width/2-35, 675, width/2-25, 675, width/2-25, 665, width/2+35, 700, width/2+25, 700, width/2+25, 710, fill="#ff7878", outline="black")
        classic_rcross = canvas.create_polygon(width/2+35, 675, width/2+25, 675, width/2+25, 665, width/2-35, 700, width/2-25, 700, width/2-25, 710, fill="#ff7878", outline="black")
        classic_circle = canvas.create_oval(width/2+20, 667.5, width/2-20, 707.5, fill="#ff7878")
    canvas.tag_bind(classic_lcross, "<Button-1>", lambda event: change_setting(canvas, [["classic", "bool"], ["mod", not classic, 6], ["mod", not classic, 7, [0, 1]], ["mod", not classic, 8], ["mod", not classic, 9, [2, ]]], multi=True))
    canvas.tag_bind(classic_rcross, "<Button-1>", lambda event: change_setting(canvas, [["classic", "bool"], ["mod", not classic, 6], ["mod", not classic, 7, [0, 1]], ["mod", not classic, 8], ["mod", not classic, 9, [2, ]]], multi=True))
    canvas.tag_bind(classic_circle, "<Button-1>", lambda event: change_setting(canvas, [["classic", "bool"], ["mod", not classic, 6], ["mod", not classic, 7, [0, 1]], ["mod", not classic, 8], ["mod", not classic, 9, [2, ]]], multi=True))
    main_button = canvas.create_rectangle(width/2-200, height-75, width/2+200, height-25, fill="gray")
    main_text = canvas.create_text(width/2, height-50, text="Main Menu", fill="black", font=menu_font)
    canvas.tag_bind(main_button, "<Button-1>", lambda event: setup_main_menu(canvas))
    canvas.tag_bind(main_text, "<Button-1>", lambda event: setup_main_menu(canvas))


def setup_tutorial(canvas):
    canvas.bind('<Escape>', lambda event: setup_main_menu(canvas))
    canvas.delete('all')
    main_button = canvas.create_rectangle(width/2-100, 400, width/2+100, 450, fill="gray")
    main_text = canvas.create_text(width/2, 425, text="Main Menu", fill="black", font=menu_font)
    canvas.tag_bind(main_button, "<Button-1>", lambda event: setup_main_menu(canvas))
    canvas.tag_bind(main_text, "<Button-1>", lambda event: setup_main_menu(canvas))


def exit_program(canvas):
    canvas.delete('all')
    canvas.master.destroy()


def setup_main_menu(canvas):
    canvas.unbind('<Escape>')
    canvas.focus_set()
    canvas.delete('all')
    play_button = canvas.create_rectangle(width/2-100, 300, width/2+100, 350, fill="gray")
    play_text = canvas.create_text(width/2, 325, text="Play", fill="black", font=menu_font)
    canvas.tag_bind(play_button, "<Button-1>", lambda event: setup_game(canvas))
    canvas.tag_bind(play_text, "<Button-1>", lambda event: setup_game(canvas))
    settings_button = canvas.create_rectangle(width/2-100, 400, width/2+100, 450, fill="gray")
    settings_text = canvas.create_text(width/2, 425, text="Settings", fill="black", font=menu_font)
    canvas.tag_bind(settings_button, "<Button-1>", lambda event: setup_settings(canvas))
    canvas.tag_bind(settings_text, "<Button-1>", lambda event: setup_settings(canvas))
    tutorial_button = canvas.create_rectangle(width/2-100, 500, width/2+100, 550, fill="gray")
    tutorial_text = canvas.create_text(width/2, 525, text="Tutorial", fill="black", font=menu_font)
    canvas.tag_bind(tutorial_button, "<Button-1>", lambda event: setup_tutorial(canvas))
    canvas.tag_bind(tutorial_text, "<Button-1>", lambda event: setup_tutorial(canvas))
    exit_button = canvas.create_rectangle(width/2-100, 600, width/2+100, 650, fill="gray")
    exit_text = canvas.create_text(width/2, 625, text="Exit", fill="black", font=menu_font)
    canvas.tag_bind(exit_button, "<Button-1>", lambda event: exit_program(canvas))
    canvas.tag_bind(exit_text, "<Button-1>", lambda event: exit_program(canvas))


def main():
    global width
    global height
    root = Tk()
    root.attributes('-fullscreen', True)
    root.title("Altered Chess")
    width, height = root.winfo_screenwidth(), root.winfo_screenheight()
    canvas = Canvas(root, width=width, height=height)
    canvas.configure(background='#a1a1a1')
    canvas.pack()

    root.after(1, setup_main_menu, canvas)
    root.mainloop()


if __name__ == '__main__':
    main()
