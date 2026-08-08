#!/usr/bin/env python3

import requests
import json
import datetime
import time
import os
import sys
import random
import logging
import coloredlogs

coloredlogs.install(level="INFO", fmt="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SEASON_START = datetime.date(2022, 10, 7)
SEASON_END = datetime.date(2023, 4, 14)
SINGLE_DATE_THRESHOLD = 100
API_SLEEP_SECONDS = 0.5


def _is_finished(e):
    return (
        e.get("awayScore")
        and e.get("homeScore")
        and e.get("finalResultOnly") is False
        and e.get("status", {}).get("type") == "finished"
    )


def _fetch_date(date, api_key):
    url = f"https://icehockeyapi.p.rapidapi.com/api/ice-hockey/matches/{date}"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "icehockeyapi.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers)
    j = response.json()
    return [e for e in j.get("events", []) if _is_finished(e)]


def _fetch_single_date(date, api_key, split, n_examples):
    logger.info(f"Downloading ice_hockey split {split}")
    logger.info(f"Date: {date}")
    events = _fetch_date(date, api_key)
    logger.info(f"Games after filtering: {len(events)}")
    if len(events) < n_examples:
        logger.error(
            f"Not enough ice_hockey games available for the date {date} and the required number of examples: {n_examples}. "
            "Please choose a different date, either by specifying a different random seed, or by specifying the date manually. "
            "You can also consider manually combining examples from multiple dates."
        )
        return None
    return events


def _fetch_date_range(n_examples, api_key):
    logger.info(f"Downloading ice_hockey split dev (date range {SEASON_START} to {SEASON_END})")
    all_events = []
    seen_ids = set()
    current = SEASON_START
    dates_fetched = 0
    while current <= SEASON_END and len(all_events) < n_examples:
        date = current.strftime("%d/%m/%Y")
        try:
            day_events = _fetch_date(date, api_key)
        except Exception as exc:
            logger.warning(f"Could not parse API response for {date}; skipping: {exc}")
            current += datetime.timedelta(days=1)
            time.sleep(API_SLEEP_SECONDS)
            continue
        for e in day_events:
            eid = e.get("id")
            if eid is not None and eid in seen_ids:
                continue
            if eid is not None:
                seen_ids.add(eid)
            all_events.append(e)
        dates_fetched += 1
        if dates_fetched % 10 == 0:
            logger.info(f"Fetched {dates_fetched} dates, accumulated {len(all_events)} games so far")
        current += datetime.timedelta(days=1)
        time.sleep(API_SLEEP_SECONDS)
    logger.info(f"Fetched {dates_fetched} dates, accumulated {len(all_events)} games in total")
    if len(all_events) < n_examples:
        logger.error(
            f"Not enough ice_hockey games available across the whole season ({len(all_events)} found) "
            f"for the required number of examples: {n_examples}. Consider lowering -n."
        )
        return None
    return all_events


def generate_dataset(api_key, seed, n_examples, out_dir, extra_args, verbose=False):
    splits = {
        "dev": extra_args["ice_hockey_dev_date"],
        "test": extra_args["ice_hockey_test_date"],
    }

    for split, date in splits.items():
        if split == "dev" and n_examples > SINGLE_DATE_THRESHOLD:
            events = _fetch_date_range(n_examples, api_key)
        else:
            events = _fetch_single_date(date, api_key, split, n_examples)

        if events is None:
            return

        random.seed(seed)
        random.shuffle(events)
        events = events[:n_examples]

        with open(os.path.join(out_dir, f"{split}.json"), "w") as f:
            json.dump(events, f, indent=4)