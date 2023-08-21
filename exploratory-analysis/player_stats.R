

# Load Library
library(AFL)
library(data.table)
library(plyr)

# Load AFL Stats Object
Stats = load_stats()

# player_stats <- Stats[['Player_Stats']](2022)

# Collect all Player_stats from Matches
round_metadata_list = c(
  ".consolidated_metadata",
  ".__enclos_env__",
  "Metadata",
  "clone",
  "initialize", 
  "AFL_Tipping_Comp_Ladder_IAG_2022_Tipping", 
  "AFL_Tipping_Comp_Ladder_IAG_2023_Tipping",
  # "BrisbaneLions_NorthMelbourne",
  # "Collingwood_StKilda",
  # "GreaterWesternSydney_Hawthorn",
  "Footywire_Ladder")

player_stats = list()
coaches_votes = list()
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
      stats <- Stats_match[['AFL_API_Player_Stats']]
      coaches_votes <- Stats_match[['AFLCA_Coaches_Votes']]
      if ((!(is.null(coaches_votes))) & (!(is.null(stats)))){
        stats <- merge(stats, coaches_votes, all.x = T, by = c("Match_ID", "Team", "Player", "Round_ID"))
      }
      positions <- Stats_match[['AFL_API_Team_Positions']]
      if ((!(is.null(positions))) & (!(is.null(stats)))){
        stats <- merge(stats, positions, all.x = T, by = c("Match_ID", "Team", "Player", "AFL_API_Player_ID", "Round_ID", "Player_Type"))
      }
      brownlow <- Stats_match[['Fryzigg_Player_Stats']]
      brownlow <- data.table(brownlow)
      if ("Brownlow_Votes" %in% names(brownlow)){
        brownlow <- brownlow[, c("Match_ID", "Round_ID", "Team", "Player", "Brownlow_Votes")]
        if ((!(is.null(brownlow))) & (!(is.null(stats)))){
          stats <- merge(stats, brownlow, all.x = T, by = c("Match_ID", "Team", "Player", "Round_ID"))
        }
      }
    
      player_stats = rbind.fill(player_stats, stats)
    }
  }
}
player_stats = data.table(player_stats)
player_stats[, Season:=Season.x]
player_stats[, Season.x:=NULL]
player_stats[, Season.y:=NULL]
player_stats[, Year:=Year.x]
player_stats[, Year.x:=NULL]
player_stats[, Year.y:=NULL]

## Export
write.csv(player_stats, "/Users/ciaran/Documents/Projects/AFL/data/player_stats.csv", row.names = FALSE)

