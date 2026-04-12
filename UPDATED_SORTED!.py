import pygame
import random
import sys

pygame.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 1100, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SORTED! FINAL")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Segoe UI", 16)
BIG_FONT = pygame.font.SysFont("Segoe UI", 26)

BG = (15, 15, 15)
PANEL = (25, 25, 25)

BAR = (52, 152, 219)
COMPARE = (255, 99, 71)

TEXT = (240, 240, 240)

BTN = (40, 55, 70)
BTN_HOVER = (70, 130, 255)

ARRAY = []
SIZE = 50
DELAY = 20

sorting_gen = None
highlight = []
paused = False
current_algo = ""
last_update = pygame.time.get_ticks()

# GAME
guess_mode = False
guess_answer = ""
score = 0
round_num = 0
total_rounds = 5
guess_phase = "idle"
result_text = ""
result_timer = 0

# ---------------- BUTTON ----------------
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self):
        mouse = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse)

        if hover:
            glow = self.rect.inflate(6, 6)
            pygame.draw.rect(WIN, (70,130,255), glow, border_radius=14)

        shadow = self.rect.copy()
        shadow.y += 4
        pygame.draw.rect(WIN, (0,0,0), shadow, border_radius=12)

        color = BTN_HOVER if hover else BTN
        pygame.draw.rect(WIN, color, self.rect, border_radius=12)

        txt = FONT.render(self.text, True, TEXT)
        WIN.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


# ---------------- ARRAY ----------------
def generate_array():
    global ARRAY
    ARRAY = [random.randint(50, 500) for _ in range(SIZE)]


def draw_array():
    start_x = 40
    width = 700
    bar_width = width // len(ARRAY)

    for i, val in enumerate(ARRAY):
        x = start_x + i * bar_width
        y = HEIGHT - val

        color = COMPARE if i in highlight else BAR
        pygame.draw.rect(WIN, color, (x, y, bar_width - 2, val))

        if bar_width > 15:
            txt = FONT.render(str(val), True, TEXT)
            WIN.blit(txt, (x, y - 20))


# ---------------- SORTING ----------------
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr)-i-1):
            yield j, j+1
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

def selection_sort(arr):
    for i in range(len(arr)):
        min_idx = i
        for j in range(i+1, len(arr)):
            yield min_idx, j
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]

def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            yield j, j+1
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key

def merge_sort(arr):
    def rec(l, r):
        if l >= r:
            return
        m = (l+r)//2
        yield from rec(l, m)
        yield from rec(m+1, r)
        yield from merge(l, m, r)

    def merge(l, m, r):
        left = arr[l:m+1]
        right = arr[m+1:r+1]
        i=j=0
        k=l

        while i < len(left) and j < len(right):
            yield k, k
            if left[i] <= right[j]:
                arr[k]=left[i]; i+=1
            else:
                arr[k]=right[j]; j+=1
            k+=1

        while i < len(left):
            yield k, k
            arr[k]=left[i]; i+=1; k+=1

        while j < len(right):
            yield k, k
            arr[k]=right[j]; j+=1; k+=1

    return rec(0, len(arr)-1)

def quick_sort(arr):
    def rec(low, high):
        if low < high:
            pi = yield from partition(low, high)
            yield from rec(low, pi-1)
            yield from rec(pi+1, high)

    def partition(low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            yield j, high
            if arr[j] < pivot:
                i+=1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i+1], arr[high] = arr[high], arr[i+1]
        return i+1

    return rec(0, len(arr)-1)

def heap_sort(arr):
    def heapify(n, i):
        largest = i
        l = 2*i+1
        r = 2*i+2

        if l<n and arr[l]>arr[largest]:
            largest=l
        if r<n and arr[r]>arr[largest]:
            largest=r

        if largest!=i:
            yield i, largest
            arr[i], arr[largest] = arr[largest], arr[i]
            yield from heapify(n, largest)

    n=len(arr)
    for i in range(n//2-1, -1, -1):
        yield from heapify(n,i)

    for i in range(n-1,0,-1):
        yield 0,i
        arr[i], arr[0] = arr[0], arr[i]
        yield from heapify(i,0)


# ---------------- UI ----------------
def draw_ui():
    pygame.draw.rect(WIN, PANEL, (0,0,WIDTH,80))
    pygame.draw.rect(WIN, PANEL, (800,0,300,HEIGHT))

    WIN.blit(BIG_FONT.render("SORTED!", True, TEXT), (20,15))

    if DELAY < 10:
        speed_label = "Fast"
    elif DELAY < 30:
        speed_label = "Medium"
    else:
        speed_label = "Slow"

    WIN.blit(FONT.render(f"Algorithm: {current_algo}", True, TEXT), (300,20))
    WIN.blit(FONT.render(f"Speed: {speed_label}", True, TEXT), (300,50))

    status = "PAUSED" if paused else "RUNNING"
    color = (255,80,80) if paused else (100,255,100)
    WIN.blit(FONT.render(f"Status: {status}", True, color), (550,35))

    if guess_mode:
        WIN.blit(FONT.render(f"Round: {round_num}/{total_rounds}", True, TEXT), (20,90))
        WIN.blit(FONT.render(f"Score: {score}", True, TEXT), (150,90))

    if guess_phase == "guessing":
        WIN.blit(FONT.render("Guess the Algorithm!", True, (255,255,100)), (350, 90))

    if guess_phase == "result":
        WIN.blit(FONT.render(result_text, True, (255,150,150)), (350, 90))

    pygame.draw.line(WIN, (50,50,50), (800,0), (800,HEIGHT), 2)

    for b in buttons:
        b.draw()

    if guess_mode and guess_phase == "guessing":
        for b in guess_buttons:
            b.draw()


# ---------------- BUTTONS ----------------
buttons = [
    Button(850, 80, 200, 35, "Bubble"),
    Button(850, 120, 200, 35, "Selection"),
    Button(850, 160, 200, 35, "Insertion"),
    Button(850, 200, 200, 35, "Merge"),
    Button(850, 240, 200, 35, "Quick"),
    Button(850, 280, 200, 35, "Heap"),
    Button(850, 320, 200, 35, "New Array"),
    Button(850, 360, 90, 35, "Speed +"),
    Button(960, 360, 90, 35, "Speed -"),
    Button(850, 400, 200, 35, "Pause"),
    Button(850, 440, 200, 35, "Guess Mode"),
]

guess_buttons = [
    Button(50, 520, 120, 30, "Bubble"),
    Button(200, 520, 120, 30, "Selection"),
    Button(350, 520, 120, 30, "Insertion"),
    Button(500, 520, 120, 30, "Merge"),
    Button(650, 520, 120, 30, "Quick"),
    Button(800, 520, 120, 30, "Heap"),
]


# ---------------- GAME ----------------
def start_guess():
    global guess_mode, guess_answer, sorting_gen, round_num, guess_phase

    guess_mode = True
    round_num += 1
    guess_phase = "running"

    options = ["Bubble","Selection","Insertion","Merge","Quick","Heap"]
    guess_answer = random.choice(options)

    if guess_answer == "Bubble": sorting_gen = bubble_sort(ARRAY)
    elif guess_answer == "Selection": sorting_gen = selection_sort(ARRAY)
    elif guess_answer == "Insertion": sorting_gen = insertion_sort(ARRAY)
    elif guess_answer == "Merge": sorting_gen = merge_sort(ARRAY)
    elif guess_answer == "Quick": sorting_gen = quick_sort(ARRAY)
    elif guess_answer == "Heap": sorting_gen = heap_sort(ARRAY)


# ---------------- MAIN ----------------
generate_array()

running = True
while running:
    clock.tick(60)
    WIN.fill(BG)

    current_time = pygame.time.get_ticks()

    if sorting_gen and not paused:
        if current_time - last_update > DELAY:
            try:
                highlight = next(sorting_gen)
            except StopIteration:
                sorting_gen = None
                highlight = []
                if guess_mode:
                    guess_phase = "guessing"
            last_update = current_time

    if guess_phase == "result":
        if pygame.time.get_ticks() - result_timer > 1500:
            if round_num < total_rounds:
                generate_array()
                start_guess()
            else:
                guess_mode = False
                guess_phase = "idle"

    draw_array()
    draw_ui()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if buttons[10].clicked(event):
            score = 0
            round_num = 0
            generate_array()
            start_guess()

        if guess_mode and guess_phase == "guessing":
            for b in guess_buttons:
                if b.clicked(event):
                    if b.text == guess_answer:
                        score += 1
                        result_text = "Correct!"
                    else:
                        result_text = f"Wrong! It was {guess_answer}"

                    guess_phase = "result"
                    result_timer = pygame.time.get_ticks()

        if buttons[9].clicked(event):
            paused = not paused
            buttons[9].text = "Resume" if paused else "Pause"

        if buttons[7].clicked(event):
            DELAY = max(1, DELAY - 3)

        if buttons[8].clicked(event):
            DELAY += 3

        if buttons[6].clicked(event):
            generate_array()

        if not guess_mode:
            if buttons[0].clicked(event): sorting_gen=bubble_sort(ARRAY); current_algo="Bubble"
            if buttons[1].clicked(event): sorting_gen=selection_sort(ARRAY); current_algo="Selection"
            if buttons[2].clicked(event): sorting_gen=insertion_sort(ARRAY); current_algo="Insertion"
            if buttons[3].clicked(event): sorting_gen=merge_sort(ARRAY); current_algo="Merge"
            if buttons[4].clicked(event): sorting_gen=quick_sort(ARRAY); current_algo="Quick"
            if buttons[5].clicked(event): sorting_gen=heap_sort(ARRAY); current_algo="Heap"

pygame.quit()
sys.exit()