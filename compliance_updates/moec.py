"""
Scrapes the Ministry of Economy's webpage.
Looks for updates to the legislation page.
Downloads the PDFs and saves them to the `documents/new/moec` directory.
"""

import logging
import ssl
import sys
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup
import requests
import urllib3


# This mimics the behavior of the legacy ssl module
# https://stackoverflow.com/questions/71603314/ssl-error-unsafe-legacy-renegotiation-disabled
class CustomHttpAdapter(requests.adapters.HTTPAdapter):  # type: ignore
    """
    "Transport adapter" that allows us to use custom ssl_context.
    """

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **_kwargs):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
        )


def get_legacy_session():
    """
    Create a session with the legacy ssl module.
    """
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount("https://", CustomHttpAdapter(ctx))
    return session


@dataclass
class Law:
    """
    A link to a law along with its name
    """

    name: str
    link: str


@dataclass
class Section:
    """
    A category of laws with a title and a list of laws
    """

    title: str
    links: list[Law]


DOMAIN = "https://www.moec.gov.ae"
# this location is relative to main
LOCATION = "documents/new/moec"


def parse_card(card: BeautifulSoup) -> Section:
    """
    parses a card div and returns a Section object
    """
    title = card.find("span", class_="title").text  # type: ignore
    # get the <div class="accordian_sub_items">
    laws = []
    for law in card.find_all("div", class_="accordian_sub_items"):
        name = law.find("div", class_="text_title").text
        name = name.strip()
        # there's two <a>s but find returns the first
        # which is what we want
        link = law.find("a")["href"]
        link = link.strip()
        laws.append(Law(name, link))

    # since we're going to turn these into filenames
    # and directories, let's remove the slashes
    title = title.replace("/", ":")
    for law in laws:
        law.name = law.name.replace("/", ":")
        # truncate the file name if longer than 255 characters
        # which breaks the os limit
        if len(law.name.encode("utf-8")) > 255:
            # -5 chars for the `.pdf` extension, one extra for good measure
            law.name = law.name.encode("utf-8")[:250].decode("utf-8")

    # if any of the text is missing log some errors
    if not title:
        logging.error("Title missing for %s", card)
        sys.exit(1)
    for law in laws:
        if not law.name or not law.link:
            logging.error("Name or link missing for %s", card)
            sys.exit(1)

    logging.debug("Successfully parsed %s", title)
    return Section(title, laws)


def get_sections() -> list[Section]:
    """
    Gets the sections from requesting the laws page
    """
    response = get_legacy_session().get(f"{DOMAIN}/en/laws", timeout=5)
    soup = BeautifulSoup(response.text, "html.parser")

    logging.debug("Successfully fetched %s", f"{DOMAIN}/en/laws")

    categories = soup.find_all("div", class_="card")

    if len(categories) == 0:
        logging.error(
            "No categories (<div class=card>) found on page %s", f"{DOMAIN}/en/laws"
        )
        sys.exit(1)

    return [parse_card(category) for category in categories]


def download_sections(sections: list[Section]):
    """
    Downloads the PDFs from the sections
    to the location specified in the `LOCATION` variable
    """
    logging.debug("Writing to %s", LOCATION)
    for section in sections:
        for law in section.links:
            try:
                download_link = f"{DOMAIN}{law.link}"
                # download the file
                response = get_legacy_session().get(download_link, timeout=5)

                # create the file path if it doesn't exist
                output_path = Path(f"{LOCATION}/{section.title}/{law.name}.pdf")
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # write the file
                with open(f"{LOCATION}/{section.title}/{law.name}.pdf", "wb") as file:
                    file.write(response.content)
                    logging.debug("Successfully wrote %s", law.name)
            except Exception as e:  # pylint: disable=broad-except
                logging.exception("Failed to download %s with error %s", law.name, e)
