import pygame
import random
import sys

# ---------------- INIT ----------------
pygame.init()
WIDTH, HEIGHT = 1000, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SORTED! - Advanced Multi Sorting Visualizer")

clock = pygame.time.Clock()
FPS = 60

FONT = pygame.font.SysFont("Arial", 18)
BIG_FONT = pygame.font.SysFont("Arial", 24)

# ---------------- COLORS ----------------
BG_COLOR = (30, 30, 30)
BAR_COLOR = (70, 130, 180)
COMPARE_COLOR = (255, 99, 71)
SORTED_COLOR = (46, 204, 113)

BUTTON_COLOR = (52, 152, 219)
BUTTON_HOVER = (41, 128, 185)
TEXT_COLOR = (240, 240, 240)

# ---------------- GLOBALS ----------------
ARRAY = []
SIZE = 60
DELAY = 8
sorting = False


# ---------------- BUTTON CLASS ----------------
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        color = BUTTON_HOVER if self.rect.collidepoint(mouse) else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=8)

        text_surface = FONT.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


# ---------------- ARRAY ----------------
def generate_array():
    global ARRAY
    ARRAY = [random.randint(50, 500) for _ in range(SIZE)]


def draw_array(highlight=[]):
    bar_width = WIDTH // len(ARRAY)
    for i, value in enumerate(ARRAY):
        x = i * bar_width
        y = HEIGHT - value
        color = COMPARE_COLOR if i in highlight else BAR_COLOR
        pygame.draw.rect(WIN, color, (x, y, bar_width - 2, value))


def update_screen(algo_name="", highlight=[]):
    WIN.fill(BG_COLOR)
    draw_array(highlight)
    draw_ui(algo_name)
    pygame.display.flip()
    pygame.time.delay(DELAY)


# ---------------- SORTS ----------------

def bubble_sort():
    global sorting
    sorting = True
    for i in range(len(ARRAY)):
        for j in range(len(ARRAY) - i - 1):
            handle_quit()
            update_screen("Bubble Sort - O(n²)", [j, j + 1])
            if ARRAY[j] > ARRAY[j + 1]:
                ARRAY[j], ARRAY[j + 1] = ARRAY[j + 1], ARRAY[j]
    sorting = False


def selection_sort():
    global sorting
    sorting = True
    for i in range(len(ARRAY)):
        min_idx = i
        for j in range(i + 1, len(ARRAY)):
            handle_quit()
            update_screen("Selection Sort - O(n²)", [min_idx, j])
            if ARRAY[j] < ARRAY[min_idx]:
                min_idx = j
        ARRAY[i], ARRAY[min_idx] = ARRAY[min_idx], ARRAY[i]
    sorting = False


def insertion_sort():
    global sorting
    sorting = True
    for i in range(1, len(ARRAY)):
        key = ARRAY[i]
        j = i - 1
        while j >= 0 and ARRAY[j] > key:
            handle_quit()
            ARRAY[j + 1] = ARRAY[j]
            update_screen("Insertion Sort - O(n²)", [j])
            j -= 1
        ARRAY[j + 1] = key
    sorting = False


def merge_sort():
    global sorting
    sorting = True

    def merge_sort_rec(arr, l, r):
        if l >= r:
            return
        mid = (l + r) // 2
        merge_sort_rec(arr, l, mid)
        merge_sort_rec(arr, mid + 1, r)
        merge(arr, l, mid, r)

    def merge(arr, l, m, r):
        left = arr[l:m + 1]
        right = arr[m + 1:r + 1]
        i = j = 0
        k = l
        while i < len(left) and j < len(right):
            handle_quit()
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            update_screen("Merge Sort - O(n log n)", [k])
            k += 1
        while i < len(left):
            arr[k] = left[i]
            i += 1
            update_screen("Merge Sort - O(n log n)", [k])
            k += 1
        while j < len(right):
            arr[k] = right[j]
            j += 1
            update_screen("Merge Sort - O(n log n)", [k])
            k += 1

    merge_sort_rec(ARRAY, 0, len(ARRAY) - 1)
    sorting = False


def quick_sort():
    global sorting
    sorting = True

    def quick_rec(arr, low, high):
        if low < high:
            pi = partition(arr, low, high)
            quick_rec(arr, low, pi - 1)
            quick_rec(arr, pi + 1, high)

    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            handle_quit()
            if arr[j] < pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
            update_screen("Quick Sort - O(n log n avg)", [j])
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    quick_rec(ARRAY, 0, len(ARRAY) - 1)
    sorting = False


def heap_sort():
    global sorting
    sorting = True

    def heapify(arr, n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2

        if l < n and arr[l] > arr[largest]:
            largest = l
        if r < n and arr[r] > arr[largest]:
            largest = r

        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            update_screen("Heap Sort - O(n log n)", [i, largest])
            heapify(arr, n, largest)

    n = len(ARRAY)
    for i in range(n // 2 - 1, -1, -1):
        heapify(ARRAY, n, i)

    for i in range(n - 1, 0, -1):
        ARRAY[i], ARRAY[0] = ARRAY[0], ARRAY[i]
        heapify(ARRAY, i, 0)

    sorting = False


def handle_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


# ---------------- UI ----------------
def draw_ui(algo=""):
    title = BIG_FONT.render("SORTED! - Multi Algorithm Visualizer", True, TEXT_COLOR)
    WIN.blit(title, (20, 10))

    algo_text = FONT.render(algo, True, TEXT_COLOR)
    WIN.blit(algo_text, (20, 45))

    for btn in buttons:
        btn.draw(WIN)


# ---------------- BUTTONS ----------------
buttons = [
    Button(750, 20, 200, 40, "Bubble"),
    Button(750, 70, 200, 40, "Selection"),
    Button(750, 120, 200, 40, "Insertion"),
    Button(750, 170, 200, 40, "Merge"),
    Button(750, 220, 200, 40, "Quick"),
    Button(750, 270, 200, 40, "Heap"),
    Button(750, 320, 200, 40, "New Array"),
]


# ---------------- MAIN ----------------
def main():
    generate_array()

    running = True
    while running:
        clock.tick(FPS)
        WIN.fill(BG_COLOR)
        draw_array()
        draw_ui()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not sorting:
                if buttons[0].clicked(event): bubble_sort()
                if buttons[1].clicked(event): selection_sort()
                if buttons[2].clicked(event): insertion_sort()
                if buttons[3].clicked(event): merge_sort()
                if buttons[4].clicked(event): quick_sort()
                if buttons[5].clicked(event): heap_sort()
                if buttons[6].clicked(event): generate_array()

    pygame.quit()
    sys.exit()


main()
