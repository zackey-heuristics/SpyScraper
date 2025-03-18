"""
This module is used to output the SpyScraper result in JSON format.

Usage:
    python ss_json_output.py [URL] [--useragent USER_AGENT] [--output OUTPUT_JSON_FILE_PATH]

Options:
    URL: str
        The URL to be scraped.
    USER_AGENT: str
        The user-agent to be used in the request header.
        When “random” is set, a user-agent is selected at random from the list of user-agents prepared in advance.
        Default is “random”.
    OUTPUT_JSON_FILE_PATH: pathlib.Path
        The path to the output JSON file.
"""
import argparse
import asyncio
import datetime
import json
from math import exp
import pathlib
import random
import re
import sys

import whois
import phonenumbers
from bs4 import BeautifulSoup

import lib.formats
from lib.requests import Requests



async def extract_emails(url: str, useragents: list[str]) -> list:
    try:
        headers = {
            "User-Agent": random.choice(useragents)
        }

        response = await Requests(url, headers=headers).sender()
        email_regex = lib.formats.EMAIL
        emails = re.findall(email_regex, response.text)

        return emails

    except:
        return []


async def extract_href(url: str, useragents: list[str]) -> list:
    try:
        headers = {
            "User-Agent": random.choice(useragents)
        }
        
        response = await Requests(url, headers=headers).sender()
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')
        hrefs = [link.get('href') for link in links]
        return hrefs
    
    except:
        return []


async def author_infos(url: str, useragents: list[str]):
    try:
        headers = {
            "User-Agent": random.choice(useragents)
        }

        response = await Requests(url, headers=headers).sender()

        soup = BeautifulSoup(response.text, 'html.parser')
        author_element = soup.find('meta', {'name': 'author'})
        if author_element:
            return author_element['content']
        else:
            return None
        
    except:
        return None


async def extract_phone(url: str, useragents: list[str]) -> list:
    try:
        headers = {
            "User-Agent": random.choice(useragents)
        }
        
        response = await Requests(url, headers=headers).sender()
        phone_regex = lib.formats.PHONE_NUMBER
        phone_numbers = re.findall(phone_regex, response.text)
        
        unique_phone_numbers = list(set(phone_numbers))
        
        formatted_phone_numbers = []
        for phone_number in unique_phone_numbers:
            try:
                parsed_phone_number = phonenumbers.parse(phone_number, None)
                formatted_phone_numbers.append(parsed_phone_number)
            except:
                pass
        
        return formatted_phone_numbers

    except:
        return []


async def creation_update(url: str) -> dict:
    try:
        domain = url.replace("https://", "").replace("http://", "").replace("www.", "")
        
        whois_info = await asyncio.to_thread(whois.whois, domain)
        
        creation_date = whois_info.creation_date
        expiration_date = whois_info.expiration_date
        updated_date = whois_info.updated_date
        
        if isinstance(creation_date, list):
            creation_date_ = [
                date.replace(tzinfo=datetime.timezone.utc).isoformat() for date in creation_date if isinstance(date, datetime.datetime)
            ]
        else:
            creation_date_ = creation_date.replace(tzinfo=datetime.timezone.utc).isoformat()
        
        if isinstance(expiration_date, list):
            expiration_date_ = [
                date.replace(tzinfo=datetime.timezone.utc).isoformat() for date in expiration_date if isinstance(date, datetime.datetime)
            ]
        else:
            expiration_date_ = expiration_date.replace(tzinfo=datetime.timezone.utc).isoformat()
        
        if isinstance(updated_date, list):
            updated_date_ = [
                date.replace(tzinfo=datetime.timezone.utc).isoformat() for date in updated_date if isinstance(date, datetime.datetime)
            ]
        else:
            updated_date_ = updated_date.replace(tzinfo=datetime.timezone.utc).isoformat()
        
        return {
            "creation_date": creation_date_,
            "expiration_date": expiration_date_,
            "updated_date": updated_date_
        }
        
    except:
        return {}


async def servers_infos(url: str) -> list:
    try:
        domain = url.replace("https://", "").replace("http://", "").replace("www.", "")
        
        whois_info = whois.whois(domain)
        
        servers = whois_info.name_servers
        
        return servers
        
    except:
        return []


async def extract_location(url: str) -> list:
    try:
        response = await Requests(url).sender()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        locations = []
        location_elements = soup.find_all('meta', {'name': 'geo.position'})
        
        for element in location_elements:
            location = element.text.strip()
            locations.append(location)
        
        return locations

    except:
        return []


async def maincore():
    parser = argparse.ArgumentParser(
        description="Output the SpyScraper result in JSON format."
    )
    parser.add_argument("url", type=str, help="The URL to be scraped.")
    parser.add_argument(
        "--useragent",
        type=str,
        default="random",
        help="The user-agent to be used in the request header. When “random” is set, a user-agent is selected at random from the list of user-agents prepared in advance.",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        help="The path to the output JSON file.",
    )
    args = parser.parse_args()
    target_url = args.url
    output_json_file_path = args.output
    
    # Check the user-agent
    if args.useragent == "random":
        with open("useragents.txt", "r") as useragents_file:
            useragents = useragents_file.read().split('\n')
    else:
        useragents = [args.useragent]
    
    emails = await extract_emails(target_url, useragents)
    links = await extract_href(target_url, useragents)
    authors = await author_infos(target_url, useragents)
    phones = await extract_phone(target_url, useragents)
    creation_update_info = await creation_update(target_url)
    servers = await servers_infos(target_url)
    locations = await extract_location(target_url)
    
    result = {
        "target_url": target_url,
        "emails": emails,
        "links": links,
        "authors": authors,
        "phones": phones,
        "creation_update_info": creation_update_info,
        "servers": servers,
        "locations": locations
    }
    
    if output_json_file_path:
        with open(output_json_file_path, "w") as output_json_file:
            json.dump(result, output_json_file, indent=4)
    else:
        print(json.dumps(result, indent=4))


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(maincore())


if __name__ == "__main__":
    main()
