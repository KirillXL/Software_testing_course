import pygame as pg
import numpy as np
import cv2

class ArtASCII:
    """
    Базовый класс для преобразования изображения в ASCII-стиль.

    Args:
        path (str): Путь к изображению (по умолчанию 'photo/nya.jpg').
        font_size (int): Размер шрифта для символов (по умолчанию 10).
        screen_res (tuple): Разрешение экрана (по умолчанию (800, 600)).

    Attributes:
        surface (pygame.Surface): Поверхность для отрисовки.
        font (pygame.font.Font): Шрифт для символов ASCII.
        clock (pygame.time.Clock): Объект для управления FPS.
    """
    def __init__(self, path='photo/nya.jpg', font_size=10, screen_res=(800, 600)):
        pg.init()
        self.path = path
        self.font_size = font_size
        self.screen_res = screen_res
        self.RES = self.WIDTH, self.HEIGHT = screen_res
        self.surface = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont('Courier', font_size, bold=True)
        self.CHAR_STEP = int(font_size * 0.6)

    def get_image(self):
        """
        Загружает изображение и обрабатывает альфа-канал, если он присутствует.

        Returns:
            numpy.ndarray: Изображение в формате RGB.

        Raises:
            FileNotFoundError: Если изображение не найдено.
        """
        self.cv2_image = cv2.imread(self.path, cv2.IMREAD_UNCHANGED)
        if self.cv2_image is None:
            raise FileNotFoundError(f"Image at path {self.path} could not be loaded.")
        if self.cv2_image.shape[-1] == 4:
            bgra_image = self.cv2_image
            self.cv2_image = cv2.cvtColor(bgra_image, cv2.COLOR_BGRA2BGR)
            print("Alpha channel detected and removed.")
        return cv2.cvtColor(self.cv2_image, cv2.COLOR_BGR2RGB)

    def draw_converted_image(self):
        """
        Абстрактный метод для отрисовки преобразованного изображения.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError("This method should be implemented in the subclass.")

    def draw_cv2_image(self):
        """
        Отображает исходное изображение с помощью OpenCV.
        """
        resized_cv2_image = cv2.resize(self.cv2_image, self.screen_res, interpolation=cv2.INTER_AREA)
        cv2.imshow('photo', resized_cv2_image)

    def draw(self):
        """
        Отрисовывает преобразованное изображение и исходное изображение.
        """
        self.surface.fill('black')
        self.draw_converted_image()
        self.draw_cv2_image()

    def run(self):
        """
        Запускает основной цикл обработки и отображения.

        Example:
            >>> app = ArtASCII('photo/nya.jpg')
            >>> app.run()
        """
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            self.draw()
            pg.display.set_caption("Обработанное изображение")
            pg.display.flip()
            self.clock.tick()

class ArtASCIIGray(ArtASCII):
    """
    Класс для преобразования изображения в серый ASCII-стиль.

    Наследуется от ArtASCII и использует символы для представления яркости.

    Args:
        path (str): Путь к изображению (по умолчанию 'photo/nya.jpg').
        font_size (int): Размер шрифта (по умолчанию 10).
        screen_res (tuple): Разрешение экрана (по умолчанию (800, 600)).
    """
    def __init__(self, path='photo/nya.jpg', font_size=10, screen_res=(800, 600)):
        super().__init__(path, font_size, screen_res)
        self.ASCII_CHARS = ' .",:;!~+-xmo*#W&8@'
        self.ASCII_COEFF = 255 // (len(self.ASCII_CHARS) - 1)
        self.image = self.get_image()
        self.image = cv2.resize(self.image, self.screen_res, interpolation=cv2.INTER_AREA)
        self.RENDERED_ASCII_CHARS = [self.font.render(char, False, 'white') for char in self.ASCII_CHARS]

    def get_image(self):
        """
        Загружает изображение и конвертирует его в оттенки серого.

        Returns:
            numpy.ndarray: Изображение в оттенках серого.
        """
        self.cv2_image = cv2.imread(self.path)
        gray_image = cv2.cvtColor(self.cv2_image, cv2.COLOR_BGR2GRAY)
        return gray_image

    def draw_converted_image(self):
        """
        Отрисовывает изображение в сером ASCII-стиле.
        """
        char_indices = self.image // self.ASCII_COEFF
        for x in range(0, self.WIDTH, self.CHAR_STEP):
            for y in range(0, self.HEIGHT, self.CHAR_STEP):
                char_index = char_indices[y, x]
                if char_index:
                    self.surface.blit(self.RENDERED_ASCII_CHARS[char_index], (x, y))

class ArtASCIIColor(ArtASCII):
    """
    Класс для преобразования изображения в цветной ASCII-стиль.

    Наследуется от ArtASCII и добавляет поддержку цвета для символов.

    Args:
        path (str): Путь к изображению (по умолчанию 'photo/nya.jpg').
        font_size (int): Размер шрифта (по умолчанию 10).
        screen_res (tuple): Разрешение экрана (по умолчанию (800, 600)).
        color_lvl (int): Уровень квантования цвета (по умолчанию 8).
    """
    def __init__(self, path='photo/nya.jpg', font_size=10, screen_res=(800, 600), color_lvl=8):
        super().__init__(path, font_size, screen_res)
        self.COLOR_LVL = color_lvl
        self.ASCII_CHARS = ' ixzao*#MW&8%B@$'
        self.ASCII_COEFF = 255 // (len(self.ASCII_CHARS) - 1)
        self.image = self.get_image()
        self.image = cv2.resize(self.image, (self.WIDTH // self.CHAR_STEP, self.HEIGHT // self.CHAR_STEP), interpolation=cv2.INTER_AREA)
        self.PALETTE, self.COLOR_COEFF = self.create_palette()

    def get_image(self):
        """
        Загружает изображение и конвертирует его в RGB.

        Returns:
            numpy.ndarray: Изображение в формате RGB.
        """
        self.cv2_image = cv2.imread(self.path)
        return cv2.cvtColor(self.cv2_image, cv2.COLOR_BGR2RGB)

    def create_palette(self):
        """
        Создает цветовую палитру для символов ASCII.

        Формула квантования цвета:
        \[
        color_key = \frac{RGB}{COLOR_COEFF}
        \]

        Returns:
            tuple: Словарь палитры и коэффициент квантования.
        """
        colors, color_coeff = np.linspace(0, 255, num=self.COLOR_LVL, dtype=int, retstep=True)
        color_palette = [np.array([r, g, b]) for r in colors for g in colors for b in colors]
        palette = dict.fromkeys(self.ASCII_CHARS, None)
        color_coeff = int(color_coeff)
        for char in palette:
            char_palette = {}
            for color in color_palette:
                color_key = tuple(color // color_coeff)
                char_palette[color_key] = self.font.render(char, False, tuple(color))
            palette[char] = char_palette
        return palette, color_coeff

    def draw_converted_image(self):
        """
        Отрисовывает изображение в цветном ASCII-стиле.
        """
        char_indices = self.image.mean(axis=2) // self.ASCII_COEFF
        color_indices = self.image // self.COLOR_COEFF
        for x in range(0, self.WIDTH, self.CHAR_STEP):
            for y in range(0, self.HEIGHT, self.CHAR_STEP):
                img_x = int(x / self.WIDTH * self.image.shape[1])
                img_y = int(y / self.HEIGHT * self.image.shape[0])
                char_index = int(char_indices[img_y, img_x])
                if char_index:
                    char = self.ASCII_CHARS[char_index]
                    color = tuple(color_indices[img_y, img_x])
                    rendered_char = self.PALETTE[char][color]
                    self.surface.blit(rendered_char, (x, y))