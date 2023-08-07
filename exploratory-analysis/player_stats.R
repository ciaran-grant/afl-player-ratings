

# Load Library
library(AFL)
library(data.table)
library(plyr)

# Load AFL Stats Object
Stats = load_stats()

# Collect all Player_stats from Matches
round_metadata_list = c(".consolidated_metadata",".__enclos_env__","Metadata","clone","initialize")

player_stats = list()
for (season in c("2021", "2022", "2023")){
  print(season)
  round_list = sort(names(Stats)[grepl(paste0("^",season), names(Stats))])
  for (round in round_list){
    print(round)
    Stats_round = Stats[[round]]
    match_list= sort(setdiff(names(Stats_round), round_metadata_list))
    for (match in match_list){
      Stats_match = Stats_round[[match]]
      print(match)
      # print("AFL API Match Stats")
      player_stats = rbind.fill(match_chains, Stats_match[['AFL_API_Player_Stats']])
    }
  }
}
player_stats = data.table(player_stats)

## Export
write.csv(player_stats, "/Users/ciaran/Documents/Projects/AFL/git-repositories/afl-player-ratings/data/player_stats_202319.csv", row.names = FALSE)

