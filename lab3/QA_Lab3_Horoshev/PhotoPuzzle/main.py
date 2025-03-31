from ascii import ArtASCIIGray, ArtASCIIColor
from pixel import ArtPixelGray, ArtPixelColor
from interface import StartMenu, PickPicture, PickArt, UploadImage



if __name__ == '__main__':

    while True:
        start = StartMenu()
        selected_menu = start.select_event()
        match selected_menu:
            case 'Start':
                picture = PickPicture("photo")
                selected_path = picture.select_event()
                selected_art = None

                if selected_path:
                    print(f"Вы выбрали: {selected_path}")
                    art = PickArt()
                    selected_art = art.select_event()
                else:
                    print("Выбор отменён или изображение не выбрано.")

                match selected_art:
                    case 'ASCII':
                        app = ArtASCIIGray(selected_path)
                        app.run()
                    case 'ASCII Color':
                        app = ArtASCIIColor(selected_path)
                        app.run()
                    case 'PIXEL':
                        app = ArtPixelGray(selected_path)
                        app.run()
                    case 'PIXEL Color':
                        app = ArtPixelColor(selected_path)
                        app.run()
            case 'Upload Image':
                download_image = UploadImage()
                download_image.select_event()
            case 'Exit':
                exit()




