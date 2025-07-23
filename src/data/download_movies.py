import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator
import xml.etree.ElementTree as ET

import requests
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MovieData:
    title: str
    genres: str
    countries: str
    directors: str

    @classmethod
    def from_wikidata(cls, item: dict[str, Any]) -> 'MovieData':
        return cls(
            title=item.get("filmLabel", {}).get("value", ""),
            genres=item.get("genres", {}).get("value", ""),
            countries=item.get("countries", {}).get("value", ""),
            directors=item.get("directors", {}).get("value", "")
        )

class WikidataMovieFetcher:
    WIKIDATA_URL = "https://query.wikidata.org/sparql"
    BATCH_SIZE = 1000
    
    def __init__(self, start_year: int = 2010):
        self.start_year = start_year
        self.current_year = datetime.now().year
        self._base_query = self._load_sparql_query()

    @staticmethod
    def _load_sparql_query() -> str:
        return """
        SELECT ?film ?filmLabel
            (GROUP_CONCAT(DISTINCT ?genreLabel; separator=", ") AS ?genres)
            (GROUP_CONCAT(DISTINCT ?countryLabel; separator=", ") AS ?countries)
            (GROUP_CONCAT(DISTINCT ?directorLabel; separator=", ") AS ?directors)
        WHERE {
            ?film wdt:P31 wd:Q11424;
            wdt:P577 ?releaseDate.
            FILTER(YEAR(?releaseDate) = YEAR_PLACEHOLDER)
            OPTIONAL { ?film wdt:P136 ?genre.
                    ?genre rdfs:label ?genreLabel.
                    FILTER(LANG(?genreLabel) = "en") }
            OPTIONAL { ?film wdt:P495 ?country.
                    ?country rdfs:label ?countryLabel.
                    FILTER(LANG(?countryLabel) = "en") }
            OPTIONAL { ?film wdt:P57 ?director.
                    ?director rdfs:label ?directorLabel.
                    FILTER(LANG(?directorLabel) = "en") }
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }
        GROUP BY ?film ?filmLabel
        """

    def _fetch_batch(self, year: int, offset: int) -> list[dict[str, Any]]:
        query = self._base_query.replace("YEAR_PLACEHOLDER", str(year))
        query += f" LIMIT {self.BATCH_SIZE} OFFSET {offset}"
        
        response = requests.get(
            self.WIKIDATA_URL,
            headers={"Accept": "application/json"},
            params={"query": query}
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch data for year {year}: HTTP {response.status_code}")
            return []
            
        return response.json()["results"]["bindings"]

    def fetch_year(self, year: int) -> list[dict[str, Any]]:
        data = []
        offset = 0
        
        while True:
            batch = self._fetch_batch(year, offset)
            if not batch:
                break
            data.extend(batch)
            offset += self.BATCH_SIZE
            
        return data

class MovieDataExporter:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_to_csv(self, movies: list[MovieData], year: int) -> None:
        filepath = self.output_dir / f"movies_data_{year}.csv"
        
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["title", "genres", "country", "extra_data"])
            
            for movie in movies:
                writer.writerow([
                    movie.title,
                    movie.genres,
                    movie.countries,
                    {"directors": movie.directors}
                ])

    def export_to_xml(self, movies: list[MovieData], year: int) -> None:
        root = ET.Element("movies")
        
        for movie in movies:
            movie_elem = ET.SubElement(root, "movie")
            
            for field in ["title", "genres", "countries", "directors"]:
                elem = ET.SubElement(movie_elem, field)
                elem.text = getattr(movie, field)

        tree = ET.ElementTree(root)
        filepath = self.output_dir / f"movies_data_{year}.xml"
        
        ET.indent(tree, space="  ")
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

def main() -> None:
    output_dir = Path("movie_data")
    fetcher = WikidataMovieFetcher()
    exporter = MovieDataExporter(output_dir)
    
    years = range(fetcher.start_year, fetcher.current_year + 1)
    for year in tqdm(years, desc="Fetching movie data"):
        raw_data = fetcher.fetch_year(year)
        movies = [MovieData.from_wikidata(item) for item in raw_data[:10]]  # Limit to 10 movies per year
        
        exporter.export_to_csv(movies, year)
        exporter.export_to_xml(movies, year)
        
        logger.info(f"Processed {len(movies)} movies for year {year}")

if __name__ == "__main__":
    main()