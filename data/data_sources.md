# Dataset Documentation — Travel.pk Review Sentiment Analyzer

## Overview
The dataset contains **125 hotel and travel destination reviews** for Pakistani
locations (hotels, guesthouses, resorts, and natural sites).

## Source Type
| Source Type   | Count | Description |
|---------------|-------|-------------|
| Self-written / Simulated | 125 | Reviews written by the project team based on realistic travel experiences in Pakistan. Each review reflects genuine traveler pain points and positive experiences documented on platforms like TripAdvisor, Booking.com, and Google Reviews — but the text itself is **original** and not copied. |

> **Note:** No copyrighted or proprietary text has been used. All reviews are
> original simulations for research and educational purposes.

## Locations Covered
- **Hotels:** Pearl Continental (Lahore, Karachi, Rawalpindi, Muzaffarabad),
  Serena (Islamabad, Quetta, Gilgit, Swat), Marriott (Karachi, Islamabad),
  Avari Towers Lahore, Mövenpick Karachi, Ramada Lahore, Hotel One (multiple cities)
- **Destinations:** Hunza Valley, Swat Valley, Murree, Naran/Kaghan, Gilgit,
  Skardu, Chitral, Kalash Valley, Fairy Meadows, Nathiagali, Shogran,
  Thandiani, Khunjerab, Besham, Azad Kashmir

## Dataset Structure (`reviews_dataset.csv`)
| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Unique review ID (1–125) |
| `review_text` | str | Full review text |
| `sentiment` | str | Ground-truth label: `positive`, `negative`, `neutral` |
| `themes` | str | Comma-separated ground-truth themes |
| `split` | str | `train` (reviews 1–100) or `test` (reviews 101–125, held-out) |
| `location` | str | Hotel or destination name |
| `source` | str | Always `simulated` — confirms this is original text |

## Label Distribution
| Sentiment | Train | Test | Total |
|-----------|-------|------|-------|
| Positive  | 40    | 10   | 50    |
| Negative  | 30    | 10   | 40    |
| Neutral   | 30    | 5    | 35    |
| **Total** | **100** | **25** | **125** |

## Theme Distribution (approximate, reviews may have multiple themes)
| Theme | Approx. Count |
|-------|---------------|
| Food | ~70 |
| Cleanliness | ~80 |
| Staff | ~75 |
| Location | ~60 |
| Value for Money | ~40 |

## Usage Rights
This dataset is **freely usable** for the Travel.pk sentiment analysis project.
It may be shared publicly as supplementary material since all content is
original and self-authored.
