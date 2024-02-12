import pygame
import reader

size = (4320//4, 2160//4)
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()

current_position = reader.MapPosition(0, 0, 4320//4, 2160//4, 0, resolution=4)
etopo = current_position.bake()

last_position = (0, 0)
min_position_distance_update = 10
last_position_update_time = 0

loop_offset_range = (0, 1000)
is_looping = False
loop_way = 1
count = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                current_position.y -= 100
                etopo = current_position.bake()
            elif event.key == pygame.K_DOWN:
                current_position.y += 100
                etopo = current_position.bake()
            elif event.key == pygame.K_LEFT:
                current_position.x -= 100
                etopo = current_position.bake()
            elif event.key == pygame.K_RIGHT:
                current_position.x += 100
                etopo = current_position.bake()
            elif event.key == pygame.K_z:
                current_position.offset += 10
                etopo = current_position.bake()
            elif event.key == pygame.K_s:
                current_position.offset -= 10
                if current_position.offset < 0:
                    current_position.offset = 0
                etopo = current_position.bake()

            elif event.key == pygame.K_SPACE:
                is_looping = not is_looping
        elif event.type == pygame.MOUSEBUTTONDOWN:
            current_position.scale /= 2
            if current_position.scale < 1/4:
                current_position.scale = 4

            if current_position.scale == 4:
                current_position.resolution = 4
            elif current_position.scale == 2:
                current_position.resolution = 2
            else:
                current_position.resolution = 1
            etopo = current_position.bake()

    """position, posy = pygame.mouse.get_pos()
    pos_delta = (position - last_position[0]
                 ) ** 2 + (posy - last_position[1]) ** 2
    if pos_delta > min_position_distance_update:
        last_position = (position, posy)
        last_position_update_time = time.time()
        current_position.resolution = 3
    elif time.time() - last_position_update_time > 0.3:
        current_position.resolution = 1

    current_position.x = (position) * 3
    current_position.y = posy * 3"""

    if is_looping:
        count += 1

    while count > 10:
        count -= 10
        current_position.offset += loop_way * 5
        if current_position.offset > loop_offset_range[1]:
            loop_way = -1
        elif current_position.offset < loop_offset_range[0]:
            loop_way = 1
    etopo = current_position.bake()

    pygame.surfarray.blit_array(screen, etopo)

    pygame.display.flip()
    fps = clock.tick(60)
    caption = f"FPS: {clock.get_fps():.1f} | Hauteur: {current_position.offset} | Position: {current_position.x}, {current_position.y}"
    pygame.display.set_caption(caption)
