import csv
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional
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
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds

    def __init__(self, start_year: int = 2010):
        self.start_year = start_year
        self.current_year = datetime.now().year
        self._base_query = self._load_sparql_query()
        self.progress_file = Path("download_progress.json")

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

    def _load_progress(self) -> dict:
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_progress(self, year: int, offset: int) -> None:
        progress = self._load_progress()
        progress[str(year)] = offset
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f)

    def _fetch_batch(self, year: int, offset: int) -> Optional[list[dict[str, Any]]]:
        for attempt in range(self.MAX_RETRIES):
            try:
                query = self._base_query.replace("YEAR_PLACEHOLDER", str(year))
                query += f" LIMIT {self.BATCH_SIZE} OFFSET {offset}"

                response = requests.get(
                    self.WIKIDATA_URL,
                    headers={"Accept": "application/json"},
                    params={"query": query},
                    timeout=30  # Add timeout
                )

                if response.status_code == 429:  # Rate limit
                    wait_time = int(response.headers.get('Retry-After', self.RETRY_DELAY))
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                return response.json()["results"]["bindings"]

            except requests.RequestException as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_DELAY * (attempt + 1)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Failed to fetch data for year {year} at offset {offset} after {self.MAX_RETRIES} attempts: {e}")
                    return None

        return None

    def fetch_year(self, year: int) -> list[dict[str, Any]]:
        data = []
        progress = self._load_progress()
        offset = int(progress.get(str(year), 0))

        while True:
            batch = self._fetch_batch(year, offset)
            if batch is None:  # Error occurred
                break
            if not batch:  # No more data
                self._save_progress(year, 0)  # Reset progress for this year
                break

            data.extend(batch)
            offset += self.BATCH_SIZE
            self._save_progress(year, offset)

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
        try:
            raw_data = fetcher.fetch_year(year)
            if not raw_data:
                logger.warning(f"No data retrieved for year {year}, skipping...")
                continue

            movies = [MovieData.from_wikidata(item) for item in raw_data[:10]]  # Limit to 10 movies per year

            exporter.export_to_csv(movies, year)
            exporter.export_to_xml(movies, year)

            logger.info(f"Processed {len(movies)} movies for year {year}")

        except Exception as e:
            logger.error(f"Error processing year {year}: {e}")
            continue


if __name__ == "__main__":
    main()