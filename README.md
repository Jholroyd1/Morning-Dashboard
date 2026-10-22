# Morning Dashboard

A personalized, automated morning dashboard built with Python. It runs on a schedule, aggregates news from RSS feeds, checks your upcoming sports schedules, pulls movie data from TMDB, and displays your highly-rated Letterboxd films.

The output is a self-contained `dashboard.html` file that you can open in any browser.

## Features

- **Custom News Sections** – Broad and team-specific news for College Football, College Basketball, College Baseball, NFL, MLB, NBA, Entertainment, Movies, and Current Events. Powered by Google News RSS.
- **Live Sports Schedules** – Automatically fetches the next scheduled game for your favorite teams (UNC, Ohio State, Chicago Cubs) using ESPN's API.
- **Movie Releases** – Shows upcoming US theatrical releases for the next 7 days using the TMDB API.
- **Random Movie Picker** – Selects a random movie from your personal `movie_pool.txt` list and fetches its IMDB/TMDB details.
- **Letterboxd Integration** – Picks a random film you've recently rated 4 stars or higher on Letterboxd via your public RSS feed.
- **Daily Quote** – Fetches the quote of the day from API Ninjas.
- **Smart Filtering** – Deduplicates stories across all sections and filters out known paywalled domains.
- **Single-Section Navigation** – The dashboard shows one card at a time, navigable with the left/right arrow keys.

## Prerequisites

- **Python 3.9+**
- **pip** (Python package installer)

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/morning-dashboard.git
cd morning-dashboard