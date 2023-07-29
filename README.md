# AFL Player Ratings

afl-player-ratings is a repository designed to bring together a variety of ideas to value AFL players. The ultimate goal is to create a player rating, player value model or range of ratings per player to help quantify and understand player performance.

As well as considering raw stat quantities and Expected Score, I am interested in Expected Possession Value models such as Expected Threat and VAEP from soccer.

Implementations of both will be included and experimental improvements will also be considered and tested.

## Installation

```python
git clone https://github.com/ciaran-grant/afl-player-ratings.git
```

## Usage

Each model or concept has it's own folder with analysis in notebooks and python modules.

Data is sourced from a private R package.

### Analysis

#### Expected Threat

![shot](expected-threat/figures/20230729_shot_probability.png)

![move](expected-threat/figures/20230729_move_probability.png)

![goal](expected-threat/figures/20230729_goal_probability.png)

![expected-threat](expected-threat/figures/20230729_expected_threat.png)

#### VAEP
TBD

#### Expected VAEP
TBD


## Credits
Data sourced using a private R package. Credits to dgt23.

Expected threat concept from Karun Singh and implementation from mplsoccer.

## CONTRIBUTING
I am currently working on this project so any bugs or suggestions are very welcome. Please contact me or create a pull request.

## License

[MIT](https://choosealicense.com/licenses/mit/)


