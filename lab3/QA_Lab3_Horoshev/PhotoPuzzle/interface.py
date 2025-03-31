import pygame as pg
import os
from tkinter import Tk, filedialog



class Interface:
    def __init__(self,path = "photo" ,screen_res = (800,600)):
        # Инициализация Pygame
        pg.init()
        self.PATH = path
        # Настройки окна
        self.screen_res = screen_res
        self.RES = self.WIDTH, self.HEIGHT = screen_res
        self.surface = pg.display.set_mode(self.RES)

        # Цвета
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)

        self.scroll_offset = 0

        # Шрифт
        self.font = pg.font.Font(None, 36)

        self.clock = pg.time.Clock()

    # Функция отображения текста
    def render_text(self, text, x, y,font = None, color = (0,0,0), center=True):
        if font is None:
            font = self.font
        text_surface = font.render(text, True, color)
        if center:
            x -= text_surface.get_width() // 2
            y -= text_surface.get_height() // 2
        self.surface.blit(text_surface, (x, y))

    # Основной цикл
    def run(self):
        while True:
            for i in pg.event.get():
                if i.type == pg.QUIT:
                    exit()
            self.select_event()
            pg.display.flip()
            self.clock.tick(30)

    def select_event(self):
        raise NotImplementedError("Этот метод должен быть реализован в дочернем классе")

class StartMenu(Interface):
    def __init__(self,path = "photo",screen_res = (800,600)):
        super().__init__(path,screen_res)

    def select_event(self):
        pg.display.set_caption("Start Menu")
        # Кнопки

        start_button = ['Start','Upload Image','Exit']

        running = True
        select_button = None

        while running:
            self.surface.fill(self.WHITE)
            # Отображение списка изображений
            for i, name_button in enumerate(start_button):
                rect = pg.Rect(50, 50 + i * 50, 700, 50)
                pg.draw.rect(self.surface, self.GRAY, rect)
                pg.draw.rect(self.surface, self.BLACK, rect, 2)
                self.render_text(name_button, rect.centerx, rect.centery)

            # Обработка событий
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ
                    mouse_x, mouse_y = event.pos
                    for i, name_button in enumerate(start_button):
                        rect = pg.Rect(50, 50 + i * 50, 700, 50)
                        if rect.collidepoint(mouse_x, mouse_y):
                            select_button = name_button
                            running = False

            pg.display.flip()
            self.clock.tick(30)

        return select_button



class PickPicture(Interface):
    def __init__(self,path = "photo",screen_res = (800,600)):
        super().__init__(path,screen_res)



    def select_event(self):
        pg.display.set_caption("Выбор картинки")
        # Список изображений
        try:
            images = [os.path.join(self.PATH, img) for img in os.listdir(self.PATH)
                      if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
        except FileNotFoundError:
            print(f"Папка {self.PATH} не найдена!")
            return None

        if not images:
            print(f"В папке {self.PATH} нет подходящих изображений!")
            return

        #Размеры для слайдера
        total_height = len(images) * 60
        visible_ratio = min(1, self.HEIGHT / total_height)
        slider_height = max(30, visible_ratio * self.HEIGHT)
        slider_width = 20
        slider_x = self.WIDTH - slider_width - 10
        dragging_slider = False
        start_drag_y = None



        running = True
        selected_image = None

        while running:
            self.surface.fill(self.WHITE)

            # Отображение списка изображений
            for i, img_path in enumerate(images):
                y = 50 + i * 60 - self.scroll_offset
                if -50 < y < self.HEIGHT:
                    rect = pg.Rect(50, y, 700, 50)
                    pg.draw.rect(self.surface, self.GRAY, rect)
                    pg.draw.rect(self.surface, self.BLACK, rect, 2)
                    self.render_text(os.path.basename(img_path), rect.centerx, rect.centery)

            # Отрисовка слайдера
            slider_y = (self.scroll_offset / total_height) * self.HEIGHT
            slider_rect = pg.Rect(slider_x, slider_y, slider_width, slider_height)
            pg.draw.rect(self.surface, self.GRAY, slider_rect)

            # Обработка событий
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ
                    mouse_x, mouse_y = event.pos
                    for i, img_path in enumerate(images):
                        rect = pg.Rect(50, 50 + i * 50, 700, 50)
                        if rect.collidepoint(mouse_x, mouse_y):
                            selected_image = img_path
                            running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if slider_rect.collidepoint(event.pos):
                        dragging_slider = True
                        start_drag_y = event.pos[1]
                elif event.type == pg.MOUSEBUTTONUP:
                    dragging_slider = False
                if event.type == pg.MOUSEMOTION:
                    if dragging_slider:
                        delta_y = event.pos[1] - start_drag_y
                        self.scroll_offset += (delta_y / self.HEIGHT) * total_height
                        self.scroll_offset = max(0, min(self.scroll_offset, total_height - self.HEIGHT))
                        start_drag_y = event.pos[1]

                elif event.type == pg.MOUSEWHEEL:
                    self.scroll_offset -= event.y * 30  # Adjust scroll speed
                    self.scroll_offset = max(0, min(self.scroll_offset, total_height - self.HEIGHT))

            pg.display.flip()
            self.clock.tick(30)



        return selected_image

class PickArt(Interface):
    def __init__(self, path="photo", screen_res=(800, 600)):
        super().__init__(path, screen_res)

    def select_event(self):
        pg.display.set_caption("Выбор cтиля")
        # Список изображений

        art_array = ['ASCII','ASCII Color', 'PIXEL','PIXEL Color']

        running = True
        select_art = None

        while running:
            self.surface.fill(self.WHITE)

            # Отображение списка изображений
            for i, name_art in enumerate(art_array):
                rect = pg.Rect(50, 50 + i * 50, 700, 50)
                pg.draw.rect(self.surface, self.GRAY, rect)
                pg.draw.rect(self.surface, self.BLACK, rect, 2)
                self.render_text(name_art, rect.centerx, rect.centery)

            # Обработка событий
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ
                    mouse_x, mouse_y = event.pos
                    for i, name_art in enumerate(art_array):
                        rect = pg.Rect(50, 50 + i * 50, 700, 50)
                        if rect.collidepoint(mouse_x, mouse_y):
                            select_art = name_art
                            running = False
            pg.display.flip()
            self.clock.tick(30)

        return select_art

class UploadImage(Interface):
    def __init__(self, path="photo", screen_res=(800, 600)):
        super().__init__(path, screen_res)

    def open_file_explorer_and_copy(self):
        """Open a file explorer to select an image and copy it to the photo folder."""
        Tk().withdraw()  # Hide the root tkinter window
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )

        if file_path:
            try:
                if not os.path.exists(self.PATH):
                    os.makedirs(self.PATH)

                file_name = os.path.basename(file_path)
                dest_path = os.path.join(self.PATH, file_name)

                with open(file_path, 'rb') as src_file:
                    with open(dest_path, 'wb') as dest_file:
                        dest_file.write(src_file.read())

                print(f"Image {file_name} copied to {self.PATH}")
            except Exception as e:
                print(f"Error copying file: {e}")

    def select_event(self):
        """Immediately open file explorer and exit."""
        self.open_file_explorer_and_copy()


