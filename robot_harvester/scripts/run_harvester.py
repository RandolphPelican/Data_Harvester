from robot_harvester.harvester.harvester import Harvester


def main():
    harvester = Harvester(query="robot anxiety")
    harvester.run()


if __name__ == "__main__":
    main()
