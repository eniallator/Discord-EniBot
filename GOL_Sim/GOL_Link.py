URL_START = 'http://pmav.eu/stuff/javascript-game-of-life-v3.1.1/?autoplay=0&trail=1&grid=1&colors=1&zoom=1&s='
MAX_X = 179
MAX_Y = 85

def create_creature_url(creature):
    centered_x = int(MAX_X / 2 - creature.width / 2)
    centered_y = int(MAX_Y / 2 - creature.height / 2)
    creature_url = '['
    first_url_entry = True

    for relYVal in range(creature.height):
        new_height = True
        for relXVal in range(creature.width):
            if creature.dna[relYVal * creature.width + relXVal]:
                curr_x_coord = centered_x + relXVal
                curr_y_coord = centered_y + relYVal

                if new_height:
                    new_height = False
                    creature_url += '{"' + str(curr_y_coord) + '":[' + str(curr_x_coord)
                else:
                    creature_url += ',' + str(curr_x_coord)

        if not new_height:
            first_url_entry = False
            creature_url += ']}'

            if not first_url_entry:
                creature_url += ','
    
    return URL_START + creature_url[:-1] + ']'
