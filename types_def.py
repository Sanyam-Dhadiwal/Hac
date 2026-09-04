from typing import TypedDict, Optional

class SearchQuery(TypedDict):
    category: str;
    location: str;

class ScraperConfig(TypedDict):
    headless: bool
    timeout: int  # in milliseconds
    baseUrl: str

class Business(TypedDict, total=False):
    name: str
    rating: Optional[str]
    reviews: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    verified: Optional[bool]
