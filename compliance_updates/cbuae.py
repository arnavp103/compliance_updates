"""
Downloads the rules from the UAE central bank website.
Preprocesses and stores it for comparision.
"""

import sys

from bs4 import BeautifulSoup
import requests


def get_updates() -> list[dict[str, str]]:
    """
    Get a list of the most recent updates to the rulebook in the last 5 days
    """
    updates_list = []

    try:
        # for pagination on the website
        page_index = 0
        while True:
            # keep trying all the pages until there are no more pages
            domain = "https://rulebook.centralbank.ae"
            url = f"{domain}/en/view-revision-updates?f_days=on&changed=-30%20day&page={page_index}"
            # timeout after 5 seconds
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            headline = soup.find_all("div", class_="book-detail")
            trails = soup.find_all("div", class_="book-trail")

            # terminate the loop if there are no more updates
            if len(headline) == 0:
                break

            for headline, trail in zip(headline, trails):
                title = headline.find("a").text
                date = headline.find("time").text
                link = headline.find("a")["href"]
                body = trail.find("span", class_="field-content").text
                # the body typically has em dashes (\u2014)
                # these can't be jsonized so we replace them with hyphens
                body = body.replace("\u2014", " - ")

                updates_list.append(
                    {"title": title, "date": date, "link": link, "body": body}
                )

            page_index += 1
    # catch timeout and beautifulsoup exceptions
    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
        print(f"Error: During get_updates we got {e}")
        sys.exit(1)
    except (AttributeError, TypeError) as e:
        print(f"Error: During get_updates we got {e}")
        sys.exit(1)

    return updates_list
