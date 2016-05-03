# football_data

## Mongo collections

![Alt Text](https://github.com/hcastor/football_data/blob/master/mongo_collections.png)

## Mongo collection stats
Shows key occurence rate, and value types for each collection.
Produced with https://github.com/variety/variety

###### schedule

```
+---------------------------------------------------------------------------------+
| key           | types                       | occurrences | percents            |
| ------------- | --------------------------- | ----------- | ------------------- |
| _id           | ObjectId                    |       12010 | 100.000000000000000 |
| awayTeam      | String                      |       12010 | 100.000000000000000 |
| awayTeamScore | Number (11954),String (56)  |       12010 | 100.000000000000000 |
| date          | String                      |       12010 | 100.000000000000000 |
| day           | String                      |       12010 | 100.000000000000000 |
| homeTeam      | String                      |       12010 | 100.000000000000000 |
| homeTeamScore | Number (11954),String (56)  |       12010 | 100.000000000000000 |
| week          | String (533),Number (11477) |       12010 | 100.000000000000000 |
| year          | Number                      |       12010 | 100.000000000000000 |
| dateTime      | String                      |        1535 |  12.781015820149875 |
+---------------------------------------------------------------------------------+
```

###### stadium_info

```
+-------------------------------------------------------------------+
| key         | types                      | occurrences | percents |
| ----------- | -------------------------- | ----------- | -------- |
| _id         | ObjectId                   |        1535 |    100.0 |
| capacity    | Number                     |        1535 |    100.0 |
| location    | String                     |        1535 |    100.0 |
| schedule_id | ObjectId                   |        1535 |    100.0 |
| stadium     | String                     |        1535 |    100.0 |
| surface     | String                     |        1535 |    100.0 |
| type        | String                     |        1535 |    100.0 |
| week        | Number                     |        1535 |    100.0 |
| year        | Number                     |        1535 |    100.0 |
| zip         | Number (1363),String (172) |        1535 |    100.0 |
+-------------------------------------------------------------------+
```

###### weather_info

```
+-------------------------------------------------------------------+
| key                | types    | occurrences | percents            |
| ------------------ | -------- | ----------- | ------------------- |
| _id                | ObjectId |        1535 | 100.000000000000000 |
| schedule_id        | ObjectId |        1535 | 100.000000000000000 |
| shortWind          | String   |        1535 | 100.000000000000000 |
| weatherPicAlt      | String   |        1535 | 100.000000000000000 |
| weatherText        | String   |        1535 | 100.000000000000000 |
| week               | Number   |        1535 | 100.000000000000000 |
| year               | Number   |        1535 | 100.000000000000000 |
| temperature        | String   |        1534 |  99.934853420195438 |
| humidity           | String   |        1526 |  99.413680781758956 |
| dew_point          | String   |        1523 |  99.218241042345284 |
| visibility         | String   |        1507 |  98.175895765472319 |
| barometer          | String   |        1503 |  97.915309446254071 |
| wind               | String   |        1017 |  66.254071661237788 |
| feels_like         | String   |         325 |  21.172638436482085 |
| cloud_cover        | String   |         320 |  20.846905537459282 |
| precipitation_prob | String   |         320 |  20.846905537459282 |
+-------------------------------------------------------------------+
```

###### game_info

```
+------------------------------------------------------------------------------------+
| key             | types                       | occurrences | percents             |
| --------------- | --------------------------- | ----------- | -------------------- |
| _id             | ObjectId                    |       12010 | 100.0000000000000000 |
| schedule_id     | ObjectId                    |       12010 | 100.0000000000000000 |
| week            | String (533),Number (11477) |       12010 | 100.0000000000000000 |
| year            | Number                      |       12010 | 100.0000000000000000 |
| roof            | String                      |       11944 |  99.4504579517069089 |
| stadium         | String                      |       11944 |  99.4504579517069089 |
| surface         | String                      |       11944 |  99.4504579517069089 |
| start_time_(et) | String                      |       10924 |  90.9575353871773586 |
| weather         | String                      |        9727 |  80.9908409658617785 |
| vegas_line      | String                      |        9396 |  78.2348043297252360 |
| over/under      | String                      |        9106 |  75.8201498751040788 |
| duration        | String                      |        4515 |  37.5936719400499584 |
| won_toss        | String                      |        4514 |  37.5853455453788499 |
| attendance      | String (4510),Number (2)    |        4512 |  37.5686927560366328 |
| tickets         | String                      |         255 |   2.1232306411323898 |
| super_bowl_mvp  | String                      |          50 |   0.4163197335553705 |
+------------------------------------------------------------------------------------+
```

###### team_stats

```
+----------------------------------------------------------------------------------------+
| key                | types                        | occurrences | percents             |
| ------------------ | ---------------------------- | ----------- | -------------------- |
| _id                | ObjectId                     |       47179 | 100.0000000000000000 |
| category           | String                       |       47179 | 100.0000000000000000 |
| role               | String                       |       47179 | 100.0000000000000000 |
| seasonType         | String                       |       47179 | 100.0000000000000000 |
| team               | String                       |       47179 | 100.0000000000000000 |
| year               | Number                       |       47179 | 100.0000000000000000 |
| g                  | Number                       |       46871 |  99.3471671718349256 |
| pts/g              | Number                       |       46871 |  99.3471671718349256 |
| totpts             | Number (46839),String (32)   |       46871 |  99.3471671718349256 |
| yds/g              | Number                       |       23110 |  48.9836579834248269 |
| fum                | String (7468),Number (11024) |       18492 |  39.1954047351575880 |
| avg                | Number (17386),String (271)  |       17657 |  37.4255495029568266 |
| td                 | Number (16576),String (1081) |       17657 |  37.4255495029568266 |
| yds                | Number                       |       17657 |  37.4255495029568266 |
| lng                | String (8333),Number (7963)  |       16296 |  34.5407914538247951 |
| 1st                | String (3718),Number (10136) |       13854 |  29.3647597448017130 |
| 1st%               | String (3850),Number (10004) |       13854 |  29.3647597448017130 |
| 20+                | String (3718),Number (10136) |       13854 |  29.3647597448017130 |
| 40+                | String (3718),Number (10136) |       13854 |  29.3647597448017130 |
| 1st/g              | Number                       |        9256 |  19.6188982386231174 |
| 3rd_att            | String (3750),Number (5506)  |        9256 |  19.6188982386231174 |
| 3rd_md             | String (3750),Number (5506)  |        9256 |  19.6188982386231174 |
| 3rd_pct            | Number                       |        9256 |  19.6188982386231174 |
| 4th_att            | String (3750),Number (5506)  |        9256 |  19.6188982386231174 |
| 4th_md             | String (3750),Number (5506)  |        9256 |  19.6188982386231174 |
| 4th_pct            | Number                       |        9256 |  19.6188982386231174 |
| lost               | String (3750),Number (5506)  |        9256 |  19.6188982386231174 |
| pen                | Number (9224),String (32)    |        9256 |  19.6188982386231174 |
| pen_yds            | Number (9224),String (32)    |        9256 |  19.6188982386231174 |
| scrm_plys          | Number (9224),String (32)    |        9256 |  19.6188982386231174 |
| top/g              | String                       |        9256 |  19.6188982386231174 |
| yds/p              | Number                       |        9256 |  19.6188982386231174 |
| att                | Number                       |        9236 |  19.5765064965344742 |
| att/g              | Number                       |        9236 |  19.5765064965344742 |
| rec                | Number                       |        9236 |  19.5765064965344742 |
| ret                | Number (7340),String (1081)  |        8421 |  17.8490430064223489 |
| pct                | Number (5921),String (58)    |        5979 |  12.6730112973992668 |
| fumbles_ff         | String (731),Number (5133)   |        5864 |  12.4292587803895795 |
| fumbles_rec        | String (1781),Number (4083)  |        5864 |  12.4292587803895795 |
| fumbles_td         | String (1781),Number (4083)  |        5864 |  12.4292587803895795 |
| interceptions_int  | Number                       |        5864 |  12.4292587803895795 |
| interceptions_lng  | String (2919),Number (2945)  |        5864 |  12.4292587803895795 |
| interceptions_pdef | Number                       |        5864 |  12.4292587803895795 |
| interceptions_tds  | Number                       |        5864 |  12.4292587803895795 |
| interceptions_yds  | Number                       |        5864 |  12.4292587803895795 |
| tackles_ast        | String (731),Number (5133)   |        5864 |  12.4292587803895795 |
| tackles_comb       | Number                       |        5864 |  12.4292587803895795 |
| tackles_sck        | String (731),Number (5133)   |        5864 |  12.4292587803895795 |
| tackles_sfty       | Number                       |        5864 |  12.4292587803895795 |
| tackles_total      | String (731),Number (5133)   |        5864 |  12.4292587803895795 |
| to                 | String (2194),Number (2710)  |        4904 |  10.3944551601348056 |
| comp               | Number                       |        4618 |   9.7882532482672371 |
| def                | Number                       |        4618 |   9.7882532482672371 |
| int                | Number                       |        4618 |   9.7882532482672371 |
| kicking_fgm        | Number                       |        4618 |   9.7882532482672371 |
| kicking_xpm        | Number                       |        4618 |   9.7882532482672371 |
| other_2-pt         | String (1859),Number (2759)  |        4618 |   9.7882532482672371 |
| other_sfty         | Number                       |        4618 |   9.7882532482672371 |
| pts                | Number                       |        4618 |   9.7882532482672371 |
| rate               | Number                       |        4618 |   9.7882532482672371 |
| rsh                | Number                       |        4618 |   9.7882532482672371 |
| sck                | Number                       |        4618 |   9.7882532482672371 |
| total              | Number                       |        4618 |   9.7882532482672371 |
| touchdowns_blk_fg  | Number                       |        4618 |   9.7882532482672371 |
| touchdowns_blk_pnt | Number                       |        4618 |   9.7882532482672371 |
| touchdowns_fum     | Number                       |        4618 |   9.7882532482672371 |
| touchdowns_int     | Number                       |        4618 |   9.7882532482672371 |
| touchdowns_kret    | Number                       |        4618 |   9.7882532482672371 |
| touchdowns_pret    | Number                       |        4618 |   9.7882532482672371 |
| touchdowns_rec     | Number                       |        4618 |   9.7882532482672371 |
| touchdowns_rsh     | Number                       |        4618 |   9.7882532482672371 |
| oob                | String (1081),Number (2722)  |        3803 |   8.0607897581551118 |
| tb                 | String (1081),Number (2722)  |        3803 |   8.0607897581551118 |
| 1-19_a-m           | String                       |        2442 |   5.1760317090230821 |
| 1-19_pct           | String (1081),Number (1361)  |        2442 |   5.1760317090230821 |
| 20-29_a-m          | String                       |        2442 |   5.1760317090230821 |
| 20-29_pct          | String (1081),Number (1361)  |        2442 |   5.1760317090230821 |
| 30-39_a-m          | String                       |        2442 |   5.1760317090230821 |
| 30-39_pct          | String (1081),Number (1361)  |        2442 |   5.1760317090230821 |
| 40-49_a-m          | String                       |        2442 |   5.1760317090230821 |
| 40-49_pct          | String (1081),Number (1361)  |        2442 |   5.1760317090230821 |
| 50+_a-m            | String                       |        2442 |   5.1760317090230821 |
| 50+_pct            | String (1081),Number (1361)  |        2442 |   5.1760317090230821 |
| blk                | Number                       |        2442 |   5.1760317090230821 |
| dn                 | String (1081),Number (1361)  |        2442 |   5.1760317090230821 |
| fc                 | String (1081),Number (1361)  |        2442 |   5.1760317090230821 |
| fg_overall_blk     | Number                       |        2442 |   5.1760317090230821 |
| fg_overall_fg_att  | Number                       |        2442 |   5.1760317090230821 |
| fg_overall_fgm     | Number                       |        2442 |   5.1760317090230821 |
| fg_overall_lng     | String (479),Number (1963)   |        2442 |   5.1760317090230821 |
| fg_overall_pct     | Number (2364),String (78)    |        2442 |   5.1760317090230821 |
| in_20              | String (1081),Number (1361)  |        2442 |   5.1760317090230821 |
| net_avg            | String (1082),Number (1360)  |        2442 |   5.1760317090230821 |
| net_yds            | String (1081),Number (1361)  |        2442 |   5.1760317090230821 |
| pat_blk            | Number                       |        2442 |   5.1760317090230821 |
| pat_pct            | Number (2379),String (63)    |        2442 |   5.1760317090230821 |
| pat_xp_att         | Number                       |        2442 |   5.1760317090230821 |
| pat_xpm            | Number                       |        2442 |   5.1760317090230821 |
| punts              | Number                       |        2442 |   5.1760317090230821 |
| rety               | String (1081),Number (1361)  |        2442 |   5.1760317090230821 |
| kick_returns_20+   | String (1059),Number (1357)  |        2416 |   5.1209224443078485 |
| kick_returns_40+   | String (1059),Number (1357)  |        2416 |   5.1209224443078485 |
| kick_returns_avg   | Number                       |        2416 |   5.1209224443078485 |
| kick_returns_fc    | Number                       |        2416 |   5.1209224443078485 |
| kick_returns_fum   | String (1059),Number (1357)  |        2416 |   5.1209224443078485 |
| kick_returns_lng   | String (825),Number (1591)   |        2416 |   5.1209224443078485 |
| kick_returns_ret   | Number                       |        2416 |   5.1209224443078485 |
| kick_returns_td    | Number                       |        2416 |   5.1209224443078485 |
| kick_returns_yds   | Number                       |        2416 |   5.1209224443078485 |
| punt_returns_20+   | String (1059),Number (1357)  |        2416 |   5.1209224443078485 |
| punt_returns_40+   | String (1059),Number (1357)  |        2416 |   5.1209224443078485 |
| punt_returns_avg   | Number (2380),String (36)    |        2416 |   5.1209224443078485 |
| punt_returns_fc    | Number                       |        2416 |   5.1209224443078485 |
| punt_returns_fum   | String (1059),Number (1357)  |        2416 |   5.1209224443078485 |
| punt_returns_lng   | String (913),Number (1503)   |        2416 |   5.1209224443078485 |
| punt_returns_ret   | Number                       |        2416 |   5.1209224443078485 |
| punt_returns_rety  | Number                       |        2416 |   5.1209224443078485 |
| punt_returns_td    | Number                       |        2416 |   5.1209224443078485 |
| ko                 | Number                       |        1361 |   2.8847580491320293 |
| osk                | Number                       |        1361 |   2.8847580491320293 |
| oskr               | Number                       |        1361 |   2.8847580491320293 |
| qb_hits            | Number                       |         308 |   0.6528328281650735 |
| rush_center_+10y   | Number                       |         308 |   0.6528328281650735 |
| rush_center_1st    | Number                       |         308 |   0.6528328281650735 |
| rush_center_neg    | Number                       |         308 |   0.6528328281650735 |
| rush_center_pwr    | Number (284),String (24)     |         308 |   0.6528328281650735 |
| rush_left_+10y     | Number                       |         308 |   0.6528328281650735 |
| rush_left_1st      | Number                       |         308 |   0.6528328281650735 |
| rush_left_neg      | Number                       |         308 |   0.6528328281650735 |
| rush_left_pwr      | Number (272),String (36)     |         308 |   0.6528328281650735 |
| rush_right_+10y    | Number                       |         308 |   0.6528328281650735 |
| rush_right_1st     | Number                       |         308 |   0.6528328281650735 |
| rush_right_neg     | Number                       |         308 |   0.6528328281650735 |
| rush_right_pwr     | Number (282),String (26)     |         308 |   0.6528328281650735 |
| rush_total_att     | Number                       |         308 |   0.6528328281650735 |
| rush_total_avg     | Number                       |         308 |   0.6528328281650735 |
| rush_total_exp     | Number                       |         308 |   0.6528328281650735 |
| rush_total_tds     | Number                       |         308 |   0.6528328281650735 |
| rush_total_yds     | Number                       |         308 |   0.6528328281650735 |
| sacks              | Number                       |         308 |   0.6528328281650735 |
+----------------------------------------------------------------------------------------+
```

###### player_profiles

```
+-------------------------------------------------------------+
| key           | types    | occurrences | percents           |
| ------------- | -------- | ----------- | ------------------ |
| College       | String   |        1765 | 100.00000000000000 |
| Experience    | String   |        1765 | 100.00000000000000 |
| Height        | String   |        1765 | 100.00000000000000 |
| High School   | String   |        1765 | 100.00000000000000 |
| Weight        | String   |        1765 | 100.00000000000000 |
| _id           | ObjectId |        1765 | 100.00000000000000 |
| firstName     | String   |        1765 | 100.00000000000000 |
| lastName      | String   |        1765 | 100.00000000000000 |
| playerNumber  | String   |        1765 | 100.00000000000000 |
| playerUrl_api | String   |        1765 | 100.00000000000000 |
| player_url    | String   |        1765 | 100.00000000000000 |
| position      | String   |        1765 | 100.00000000000000 |
| Born          | String   |        1764 |  99.94334277620396 |
| Age           | String   |        1763 |  99.88668555240793 |
+-------------------------------------------------------------+
```

###### player_combines

```
+------------------------------------------------------------------+
| key               | types    | occurrences | percents            |
| ----------------- | -------- | ----------- | ------------------- |
| _id               | ObjectId |         827 | 100.000000000000000 |
| combineYear       | String   |         827 | 100.000000000000000 |
| player_profile_id | ObjectId |         827 | 100.000000000000000 |
| 40 Yard Dash      | String   |         724 |  87.545344619105194 |
| Vertical Jump     | String   |         674 |  81.499395405078602 |
| Broad Jump        | String   |         658 |  79.564691656590085 |
| Bench Press       | String   |         619 |  74.848851269649330 |
| 20 Yard Shuttle   | String   |         579 |  70.012091898428054 |
| 3 Cone Drill      | String   |         560 |  67.714631197097944 |
| 60 Yard Shuttle   | String   |         218 |  26.360338573155985 |
+------------------------------------------------------------------+
```

###### player_drafts

```
+-------------------------------------------------------+
| key               | types    | occurrences | percents |
| ----------------- | -------- | ----------- | -------- |
| _id               | ObjectId |         805 |    100.0 |
| draftAnalysis     | String   |         805 |    100.0 |
| draftYear         | String   |         805 |    100.0 |
| pickNumber        | String   |         805 |    100.0 |
| player_profile_id | ObjectId |         805 |    100.0 |
| round             | String   |         805 |    100.0 |
| team              | String   |         805 |    100.0 |
+-------------------------------------------------------+
```

###### player_career_stats

```
+---------------------------------------------------------------------------------------+
| key               | types                        | occurrences | percents             |
| ----------------- | ---------------------------- | ----------- | -------------------- |
| _id               | ObjectId                     |       19624 | 100.0000000000000000 |
| category          | String                       |       19624 | 100.0000000000000000 |
| g                 | Number                       |       19624 | 100.0000000000000000 |
| player_profile_id | ObjectId                     |       19624 | 100.0000000000000000 |
| team              | String                       |       19624 | 100.0000000000000000 |
| year              | Number                       |       19624 | 100.0000000000000000 |
| yds               | String (12174),Number (5820) |       17994 |  91.6938442723196090 |
| avg               | Number (12115),String (3796) |       15911 |  81.0792906644924614 |
| lng               | String (10093),Number (5624) |       15717 |  80.0907052588666915 |
| td                | Number (6330),String (6368)  |       12698 |  64.7064818589482229 |
| fum               | String (4302),Number (6300)  |       10602 |  54.0256828373420319 |
| sfty              | Number (3792),String (5291)  |        9083 |  46.2851610273134924 |
| 20+               | String (3363),Number (5409)  |        8772 |  44.7003668976763180 |
| 40+               | String (3363),Number (5409)  |        8772 |  44.7003668976763180 |
| int               | String (5738),Number (1515)  |        7253 |  36.9598450876477784 |
| sck               | String (1714),Number (5539)  |        7253 |  36.9598450876477784 |
| ast               | String (1161),Number (4987)  |        6148 |  31.3289849164288619 |
| comb              | Number (6138),String (10)    |        6148 |  31.3289849164288619 |
| pdef              | String (1153),Number (4995)  |        6148 |  31.3289849164288619 |
| tds               | String (5177),Number (971)   |        6148 |  31.3289849164288619 |
| total             | String (1161),Number (4987)  |        6148 |  31.3289849164288619 |
| yds/g             | String (1422),Number (4601)  |        6023 |  30.6920097839380368 |
| rec               | String (3104),Number (2315)  |        5419 |  27.6141459437423578 |
| 1st               | String (1271),Number (3647)  |        4918 |  25.0611496127191202 |
| oob               | Number (2115),String (1811)  |        3926 |  20.0061149612719120 |
| tb                | Number (2115),String (1811)  |        3926 |  20.0061149612719120 |
| att               | Number (2413),String (1476)  |        3889 |  19.8175703220546282 |
| ret               | Number (1898),String (1842)  |        3740 |  19.0582959641255592 |
| att/g             | Number                       |        3539 |  18.0340399510803095 |
| fc                | String (1708),Number (1488)  |        3196 |  16.2861801875254777 |
| ff                | String (890),Number (2045)   |        2935 |  14.9561761108846305 |
| lost              | String (1500),Number (1435)  |        2935 |  14.9561761108846305 |
| 1st%              | String (864),Number (1570)   |        2434 |  12.4031797798613947 |
| pct               | Number (1234),String (765)   |        1999 |  10.1865063187933149 |
| rety              | String (600),Number (699)    |        1299 |   6.6194455768446803 |
| comp              | Number (544),String (561)    |        1105 |   5.6308601712189157 |
| int%              | Number (539),String (566)    |        1105 |   5.6308601712189157 |
| rate              | Number                       |        1105 |   5.6308601712189157 |
| scky              | Number (544),String (561)    |        1105 |   5.6308601712189157 |
| td%               | Number (539),String (566)    |        1105 |   5.6308601712189157 |
| blk               | String (228),Number (569)    |         797 |   4.0613534447615169 |
| ko                | Number (410),String (134)    |         544 |   2.7721157766000815 |
| osk               | Number (410),String (134)    |         544 |   2.7721157766000815 |
| oskr              | Number (410),String (134)    |         544 |   2.7721157766000815 |
| dn                | String (177),Number (270)    |         447 |   2.2778230737871992 |
| in_20             | String (177),Number (270)    |         447 |   2.2778230737871992 |
| net_avg           | String (177),Number (270)    |         447 |   2.2778230737871992 |
| net_yds           | String (391),Number (56)     |         447 |   2.2778230737871992 |
| punts             | String (177),Number (270)    |         447 |   2.2778230737871992 |
| gs                | Number                       |         428 |   2.1810028536485935 |
| fg_att            | Number (299),String (51)     |         350 |   1.7835303709743171 |
| fgm               | Number (299),String (51)     |         350 |   1.7835303709743171 |
| m                 | Number (296),String (54)     |         350 |   1.7835303709743171 |
| xp_att            | Number (299),String (51)     |         350 |   1.7835303709743171 |
| xpm               | Number (299),String (51)     |         350 |   1.7835303709743171 |
+---------------------------------------------------------------------------------------+
```

###### player_game_logs

```
+-----------------------------------------------------------------------------------------+
| key                | types                         | occurrences | percents             |
| ------------------ | ----------------------------- | ----------- | -------------------- |
| _id                | ObjectId                      |      126702 | 100.0000000000000000 |
| category           | String                        |      126702 | 100.0000000000000000 |
| game_date          | String                        |      126702 | 100.0000000000000000 |
| games_g            | Number                        |      126702 | 100.0000000000000000 |
| games_gs           | Number                        |      126702 | 100.0000000000000000 |
| opp                | String                        |      126702 | 100.0000000000000000 |
| player_profile_id  | ObjectId                      |      126702 | 100.0000000000000000 |
| result             | String                        |      126702 | 100.0000000000000000 |
| week               | Number                        |      126702 | 100.0000000000000000 |
| year               | Number                        |      126702 | 100.0000000000000000 |
| fumbles_ff         | String (15577),Number (42723) |       58300 |  46.0134804501902082 |
| interceptions_avg  | Number                        |       58300 |  46.0134804501902082 |
| interceptions_int  | String (56074),Number (2226)  |       58300 |  46.0134804501902082 |
| interceptions_lng  | String (56378),Number (1922)  |       58300 |  46.0134804501902082 |
| interceptions_pdef | String (15577),Number (42723) |       58300 |  46.0134804501902082 |
| interceptions_tds  | String (56074),Number (2226)  |       58300 |  46.0134804501902082 |
| interceptions_yds  | String (56074),Number (2226)  |       58300 |  46.0134804501902082 |
| tackles_ast        | String (15577),Number (42723) |       58300 |  46.0134804501902082 |
| tackles_comb       | Number                        |       58300 |  46.0134804501902082 |
| tackles_sck        | String (15577),Number (42723) |       58300 |  46.0134804501902082 |
| tackles_sfty       | String (57728),Number (572)   |       58300 |  46.0134804501902082 |
| tackles_total      | String (15577),Number (42723) |       58300 |  46.0134804501902082 |
| fumbles_fum        | String (46642),Number (3870)  |       50512 |  39.8667740051459347 |
| fumbles_lost       | String (46642),Number (3870)  |       50512 |  39.8667740051459347 |
| rushing_att        | String (36391),Number (14121) |       50512 |  39.8667740051459347 |
| rushing_avg        | String (36396),Number (14116) |       50512 |  39.8667740051459347 |
| rushing_td         | String (36391),Number (14121) |       50512 |  39.8667740051459347 |
| rushing_yds        | String (36391),Number (14121) |       50512 |  39.8667740051459347 |
| receiving_avg      | Number (23216),String (17417) |       40633 |  32.0697384413821425 |
| receiving_lng      | String (19678),Number (20955) |       40633 |  32.0697384413821425 |
| receiving_rec      | Number (26013),String (14620) |       40633 |  32.0697384413821425 |
| receiving_td       | Number (26013),String (14620) |       40633 |  32.0697384413821425 |
| receiving_yds      | Number (26013),String (14620) |       40633 |  32.0697384413821425 |
| rushing_lng        | String (31577),Number (9056)  |       40633 |  32.0697384413821425 |
| passing_att        | Number (5751),String (4128)   |        9879 |   7.7970355637637923 |
| passing_avg        | Number (5743),String (4136)   |        9879 |   7.7970355637637923 |
| passing_comp       | Number (5751),String (4128)   |        9879 |   7.7970355637637923 |
| passing_int        | Number (5751),String (4128)   |        9879 |   7.7970355637637923 |
| passing_pct        | Number (5743),String (4136)   |        9879 |   7.7970355637637923 |
| passing_rate       | Number                        |        9879 |   7.7970355637637923 |
| passing_sck        | Number (5751),String (4128)   |        9879 |   7.7970355637637923 |
| passing_scky       | Number (5751),String (4128)   |        9879 |   7.7970355637637923 |
| passing_td         | Number (5751),String (4128)   |        9879 |   7.7970355637637923 |
| passing_yds        | Number (5751),String (4128)   |        9879 |   7.7970355637637923 |
| kickoffs_avg       | Number (4103),String (1175)   |        5278 |   4.1656800997616452 |
| kickoffs_ko        | Number (4514),String (764)    |        5278 |   4.1656800997616452 |
| kickoffs_ret       | Number (4514),String (764)    |        5278 |   4.1656800997616452 |
| kickoffs_tb        | Number (4514),String (764)    |        5278 |   4.1656800997616452 |
| overall_fgs_blk    | Number (4928),String (350)    |        5278 |   4.1656800997616452 |
| overall_fgs_fg_att | Number (4928),String (350)    |        5278 |   4.1656800997616452 |
| overall_fgs_fgm    | Number (4928),String (350)    |        5278 |   4.1656800997616452 |
| overall_fgs_lng    | Number (4928),String (350)    |        5278 |   4.1656800997616452 |
| overall_fgs_pct    | Number (4294),String (984)    |        5278 |   4.1656800997616452 |
| pat_blk            | Number (4928),String (350)    |        5278 |   4.1656800997616452 |
| pat_pct            | Number (4444),String (834)    |        5278 |   4.1656800997616452 |
| pat_xp_att         | Number (4928),String (350)    |        5278 |   4.1656800997616452 |
| pat_xpm            | Number (4928),String (350)    |        5278 |   4.1656800997616452 |
| punter_avg         | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_blk         | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_dn          | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_fc          | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_in_20       | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_lng         | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_net_avg     | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_net_yds     | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_oob         | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_punts       | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_ret         | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_rety        | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_tb          | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_td          | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
| punter_yds         | Number (4387),String (116)    |        4503 |   3.5540086186484823 |
+-----------------------------------------------------------------------------------------+
```

###### player_splits

```
+------------------------------------------------------------------------------------------+
| key               | types                           | occurrences | percents             |
| ----------------- | ------------------------------- | ----------- | -------------------- |
| _id               | ObjectId                        |      547707 | 100.0000000000000000 |
| category          | String                          |      547707 | 100.0000000000000000 |
| currentTabText    | String                          |      547707 | 100.0000000000000000 |
| player_profile_id | ObjectId                        |      547707 | 100.0000000000000000 |
| rowName           | String                          |      547707 | 100.0000000000000000 |
| splitType         | String                          |      547707 | 100.0000000000000000 |
| year              | Number                          |      547707 | 100.0000000000000000 |
| avg               | String (284082),Number (248498) |      532580 |  97.2381218425179839 |
| lng               | Number                          |      532580 |  97.2381218425179839 |
| yds               | Number (523645),String (8935)   |      532580 |  97.2381218425179839 |
| int               | Number                          |      314634 |  57.4456780724000211 |
| sck               | Number                          |      314634 |  57.4456780724000211 |
| g                 | Number                          |      310900 |  56.7639266980337993 |
| ast               | Number                          |      284082 |  51.8675131046344120 |
| comb              | Number                          |      284082 |  51.8675131046344120 |
| pdef              | Number                          |      284082 |  51.8675131046344120 |
| sfty              | Number                          |      284082 |  51.8675131046344120 |
| tds               | Number                          |      284082 |  51.8675131046344120 |
| total             | Number                          |      284082 |  51.8675131046344120 |
| 1st               | Number                          |      234629 |  42.8384154301478688 |
| td                | Number                          |      234629 |  42.8384154301478688 |
| 1st%              | Number                          |      144623 |  26.4051764903497670 |
| 20+               | Number                          |      144623 |  26.4051764903497670 |
| att               | Number                          |      120558 |  22.0114039075637145 |
| 40+               | Number                          |      114071 |  20.8270115225841543 |
| rec               | Number                          |      114071 |  20.8270115225841543 |
| pct               | Number                          |       45679 |   8.3400431252476235 |
| comp              | Number                          |       30552 |   5.5781649677656118 |
| rate              | Number                          |       30552 |   5.5781649677656118 |
| scky              | Number                          |       16752 |   3.0585696366853079 |
| a-m               | String                          |       15127 |   2.7618781574820113 |
| fg_att            | Number                          |       15127 |   2.7618781574820113 |
| fgm               | Number                          |       15127 |   2.7618781574820113 |
| blk               | Number                          |       13869 |   2.5321933077357053 |
| in_20             | Number                          |       13869 |   2.5321933077357053 |
| net_avg           | Number                          |       13869 |   2.5321933077357053 |
| punts             | Number                          |       13869 |   2.5321933077357053 |
| ret               | Number                          |       13869 |   2.5321933077357053 |
| rety              | Number                          |       13869 |   2.5321933077357053 |
+------------------------------------------------------------------------------------------+
```

###### fanduel_prices

```
+-----------------------------------------------------------------+
| key       | types                      | occurrences | percents |
| --------- | -------------------------- | ----------- | -------- |
| _id       | ObjectId                   |       36418 |    100.0 |
| fd_points | Number                     |       36418 |    100.0 |
| fd_salary | Number (36355),String (63) |       36418 |    100.0 |
| gid       | Number (36415),String (3)  |       36418 |    100.0 |
| h/a       | String                     |       36418 |    100.0 |
| name      | String                     |       36418 |    100.0 |
| oppt      | String                     |       36418 |    100.0 |
| pos       | String                     |       36418 |    100.0 |
| team      | String                     |       36418 |    100.0 |
| week      | Number                     |       36418 |    100.0 |
| year      | Number                     |       36418 |    100.0 |
+-----------------------------------------------------------------+
```