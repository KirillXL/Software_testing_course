import pygame as pg
import numpy as np
import pygame.gfxdraw
import cv2

class ArtPixel:
    """
    Базовый класс для преобразования изображения в пиксельный стиль.

    Инициализирует Pygame, загружает изображение и предоставляет методы для его обработки и отображения.

    Args:
        path (str): Путь к изображению (по умолчанию 'photo/nya.png').
        pixel_size (int): Размер пикселя для обработки (по умолчанию 5).
        screen_res (tuple): Разрешение экрана в формате (ширина, высота) (по умолчанию (800, 600)).

    Attributes:
        surface (pygame.Surface): Поверхность для отрисовки изображения.
        clock (pygame.time.Clock): Объект для управления FPS.
        image (numpy.ndarray): Загруженное изображение в формате RGB.
    """
    def __init__(self, path='photo/nya.png', pixel_size=5, screen_res=(800, 600)):
        pg.init()
        self.path = path
        self.screen_res = screen_res
        self.image = self.get_image()
        self.PIXEL_SIZE = pixel_size
        self.image = cv2.resize(self.image, self.screen_res, interpolation=cv2.INTER_AREA)
        self.RES = self.WIDTH, self.HEIGHT = self.screen_res
        self.surface = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()

    def get_image(self):
        """
        Загружает изображение и конвертирует его из BGR в RGB.

        Returns:
            numpy.ndarray: Изображение в формате RGB.
        """
        self.cv2_image = cv2.imread(self.path)
        image = cv2.cvtColor(self.cv2_image, cv2.COLOR_BGR2RGB)
        return image

    def draw_cv2_image(self):
        """
        Отображает исходное изображение с помощью OpenCV в отдельном окне.
        """
        resized_cv2_image = cv2.resize(self.cv2_image, self.screen_res, interpolation=cv2.INTER_AREA)
        cv2.imshow('photo', resized_cv2_image)

    def draw_converted_image(self):
        """
        Абстрактный метод для отрисовки преобразованного изображения.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError("Этот метод должен быть реализован в дочернем классе")

    def run(self):
        """
        Запускает основной цикл обработки и отображения изображения.

        Example:
            >>> app = ArtPixel('photo/nya.png')
            >>> app.run()
        """
        running = True
        while running:
            for i in pg.event.get():
                if i.type == pg.QUIT:
                    running = False
            self.draw_converted_image()
            pg.display.set_caption("Обработанное изображение")
            pg.display.flip()
            self.clock.tick()

class ArtPixelColor(ArtPixel):
    """
    Класс для преобразования изображения в цветной пиксельный стиль.

    Наследуется от ArtPixel и добавляет поддержку цветовой палитры с квантованием.

    Args:
        path (str): Путь к изображению (по умолчанию 'photo/nya.png').
        pixel_size (int): Размер пикселя (по умолчанию 5).
        color_lvl (int): Уровень квантования цвета (по умолчанию 8).
        screen_res (tuple): Разрешение экрана (по умолчанию (800, 600)).

    Attributes:
        PALETTE (dict): Словарь цветовой палитры для пикселей.
        COLOR_COEFF (int): Коэффициент квантования цвета.
    """
    def __init__(self, path='photo/nya.png', pixel_size=5, color_lvl=8, screen_res=(800, 600)):
        super().__init__(path, pixel_size, screen_res)
        self.COLOR_LVL = color_lvl
        self.PALETTE, self.COLOR_COEFF = self.create_palette()

    def create_palette(self):
        """
        Создает цветовую палитру для пиксельного стиля.

        Формула квантования цвета:
        \[
        color_key = \frac{RGB}{COLOR_COEFF}
        \]

        Returns:
            tuple: Словарь палитры и коэффициент квантования.
        """
        colors, color_coeff = np.linspace(0, 255, num=self.COLOR_LVL, dtype=int, retstep=True)
        color_palette = [np.array([r, g, b]) for r in colors for g in colors for b in colors]
        palette = {}
        color_coeff = int(color_coeff)
        for color in color_palette:
            color_key = tuple(color // color_coeff)
            palette[color_key] = color
        return palette, color_coeff

    def draw_converted_image(self):
        """
        Отрисовывает изображение в цветном пиксельном стиле.
        """
        self.surface.fill('black')
        color_indices = self.image // self.COLOR_COEFF
        for x in range(0, self.WIDTH, self.PIXEL_SIZE):
            for y in range(0, self.HEIGHT, self.PIXEL_SIZE):
                color_key = tuple(color_indices[y, x])
                if sum(color_key):
                    color = self.PALETTE[color_key]
                    pygame.gfxdraw.box(self.surface, (x, y, self.PIXEL_SIZE, self.PIXEL_SIZE), color)
        self.draw_cv2_image()

class ArtPixelGray(ArtPixel):
    """
    Класс для преобразования изображения в серый пиксельный стиль.

    Наследуется от ArtPixel и применяет серый фильтр к изображению.

    Args:
        path (str): Путь к изображению (по умолчанию 'photo/nya.png').
        pixel_size (int): Размер пикселя (по умолчанию 5).
        screen_res (tuple): Разрешение экрана (по умолчанию (800, 600)).
    """
    def __init__(self, path='photo/nya.png', pixel_size=5, screen_res=(800, 600)):
        super().__init__(path, pixel_size, screen_res)

    def apply_gray_filter(self):
        """
        Применяет серый фильтр к изображению.

        Returns:
            numpy.ndarray: Изображение в оттенках серого, преобразованное в RGB для отображения.
        """
        gray_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
        gray_image_rgb = cv2.merge([gray_image] * 3)
        return gray_image_rgb

    def draw_converted_image(self):
        """
        Отрисовывает изображение в сером пиксельном стиле.
        """
        self.surface.fill('black')
        gray_image = self.apply_gray_filter()
        for x in range(0, self.WIDTH, self.PIXEL_SIZE):
            for y in range(0, self.HEIGHT, self.PIXEL_SIZE):
                r, g, b = gray_image[y, x]
                pygame.gfxdraw.box(self.surface, (x, y, self.PIXEL_SIZE, self.PIXEL_SIZE), (r, g, b))
        self.draw_cv2_image()