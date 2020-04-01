""" Quick and dirty Foursquare API implentation """

from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pandas as pd


class Foursquare:
    """ Foursquare Places API class """

    BASE_ENDPOINT = "https://api.foursquare.com/v2/venues"

    def __init__(self, client_id: str, client_secret: str, version: str):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.VERSION = version
        self.BASE_PARAMS = {
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "v": self.VERSION,
        }
        self.session = self.create_requests_session()
        self.categories = Categories(self)

    @staticmethod
    def create_requests_session():
        """ Creates a Requests Seesion with a retry strategy
        Copied from:
            Advanced usage of Python requests - timeouts, retries, hooks
        By:
            Dani Hodovic
        URL:
            https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/#retry-on-failure
        """
        retry_strategy = Retry(
            total=5,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        return http

    def get_resource(self, resource_enpoint: "str", params: dict = {}):
        """ Make the get request to Fourquare """
        params.update(self.BASE_PARAMS)
        r = self.session.get(
            url=f"{self.BASE_ENDPOINT}/{resource_enpoint}", params=params
        )
        return r.json()

    def explore(
        self,
        loc: str,
        loc_type: str = "ll",
        radius: float = 250.0,
        categories_id: Optional[list] = None,
        page: int = 1,
        limit: int = 50,
    ):
        """ Request the explore resource
        Params:
            loc (str): Search string for the users location depends on loc_type
            loc_type (str): Either ll (lat and lon) or near (geocodable
                location)
            categories_id (list): Specify a list of category ids to limit
                results
            page (int): Begins at 1 and sets the offset for the API to get
                more than 50 results
            limit (int): max is 50 results per API call
        """
        params = {
            loc_type: loc,
            "radius": radius,
            "limit": limit,
            "offset": (limit * (page - 1)),
        }
        if categories_id:
            params["categoryId"] = categories_id
        return self.get_resource("explore", params)


class Categories:
    """ Class to hold the Foursquare categories """

    def __init__(self, api_object: Foursquare):
        self.api = api_object
        self.get_categories()

    def get_categories(self):
        """ Creates a pandas.DataFrame of the Places Categoires """
        response = self.api.get_resource("categories")
        all_categories = list()
        for category in response["response"]["categories"]:
            all_categories.extend(self.flatten_categories(category))
        self.df = pd.DataFrame(all_categories)
        return self

    def search(self, keywords: list) -> pd.DataFrame:
        """ Provide a list of kewords to serach the category names """
        df = self.df
        search_mask = list()
        for keyword in keywords:
            search_mask.append(df["name"].str.contains(keyword, case=False))
        search_mask = pd.concat(search_mask, axis=1).any(axis=1)
        return df[search_mask]

    def parents(self, parents_to_mask: list) -> pd.DataFrame:
        """ The Categories are nested and have up to 5 parents.  Provide a
        list of parents to subset the list to look at the children categories
        """
        df = self.df
        masks = list()
        for i, parent in enumerate(parents_to_mask):
            masks.append(df[f"Parent_{i}"] == parent)

        return df[pd.concat(masks, axis=1).all(axis=1)]

    def select(self, names: list) -> pd.DataFrame:
        """ Select names from the categories, must be a list """
        return self.df[self.df["name"].isin(names)]

    @staticmethod
    def flatten_categories(child: dict, parents: list = list()) -> list:
        """ Recursively flattens out the categories dict and adds the parent
        names to each child
        """
        cat_list = list()

        cats = child.get("categories", None)
        for cat in cats:
            cat_list.extend(
                Categories.flatten_categories(cat, [*parents, child["name"]])
            )

        # Drop the keys below to reduce the size
        child.pop("categories", None)
        child.pop("icon", None)

        # Create the keys for each parent level name
        for i, p in enumerate([*parents, "Top-Level"]):
            child[f"Parent_{i}"] = p

        return [child, *cat_list]
