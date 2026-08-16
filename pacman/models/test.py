from entity import Entity, Pacman, Ghost
from mazemap import Map


def display_maze(map_test: Map, pacman_test: Pacman) -> None:
    """Method to display debug mode of the map"""
    lines: list[str] = []
    for y in range(map_test.height):
        toplane: str = "+"
        for x in range(map_test.width):
            if map_test.map[x][y].walls & 1:
                toplane += "---+"
            else:
                toplane += "   +"
        lines.append(toplane)
        midlane: str = ""
        for x in range(map_test.width):
            if map_test.map[x][y].walls & 8:
                midlane += "|"
            else:
                midlane += " "
            if (x, y) == pacman_test.initial_position:
                midlane += " P "
            elif map_test.map[x][y].super_gum is True:
                midlane += " o "
            elif map_test.map[x][y].simple_gum is True:
                midlane += " . "
            else:
                midlane += "   "
        if map_test.map[map_test.width - 1][y].walls & 2:
            midlane += "|"
        else:
            midlane += " "
        lines.append(midlane)
    botlane: str = "+"
    for x in range(map_test.width):
        botlane += "---+"
    lines.append(botlane)
    print("\n".join(lines))


if __name__ == "__main__":
    """Test the entities instanciation."""
    map_test: Map = Map(27, 28, 100, 42)
    map_test.super_gum_placement()
    map_test.simple_gum_placement()
    pacman_test: Pacman = Pacman(4, 6, (((map_test.width - 1) // 2), ((map_test.height - 1) // 2)))
    display_maze(map_test, pacman_test)
    print("Pacman_speed: ", pacman_test.speed)
    print("Pacman_super_speed: ", pacman_test.super_speed)
    print("Pacman_initial_pos: ", pacman_test.initial_position)