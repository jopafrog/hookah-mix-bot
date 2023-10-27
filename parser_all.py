from fake_useragent import UserAgent
from time import sleep
from pars_top100 import parsing_top100
from pars_top_brand import parsing_top_brands
from pars_flavors import parsing_flavors


def main():
    fake_ua = UserAgent()

    print("PARSING TOP100")
    headers = {"User-Agent": str(fake_ua.random)}
    parsing_top100(headers)
    sleep(3)

    print("PARSING TOP BRANDS")
    headers = {"User-Agent": str(fake_ua.random)}
    parsing_top_brands(headers)
    sleep(3)

    print("PARSING ALL FLAVORS")
    headers = {"User-Agent": str(fake_ua.random)}
    parsing_flavors(headers)

    print("PARSING COMPLETE")


if __name__ == "__main__":
    main()
