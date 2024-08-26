"""
The main comparision file which sees if there's been updates.
It formats updates and notifies the stakeholders.
"""

import logging
from compliance_updates.moec import get_sections, download_sections


def main():
    """Main function to compare and send updates."""
    sections = get_sections()
    download_sections(sections)
    logging.info("MOEC Rules downloaded successfully.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] [%(levelname)5s] - %(message)s (%(filename)s:%(lineno)s)",
        datefmt="%Y-%m-%d %H:%M",
        handlers=[logging.FileHandler("script.log"), logging.StreamHandler()],
        encoding="utf-8",
    )

    logging.info("Starting Script")
    main()
    logging.info("Script terminated successfully")
