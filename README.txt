taptweets.py
------------
Extracts unique users from the Twitter Stream API. User information stored includes:
	
	1. ID - The unique ID for a user's account
	2. CREATED_AT - The date and time at which the account was created
	3. STATUSES_COUNT - The total number of user statuses
	4. FRIENDS_COUNT - The number of users followed by the user in question
	5. LISTED_COUNT - The number of public lists on which the user makes an appearance
	6. FAVORITES_COUNT - The total number of statuses favorited by the user
	7. VERIFIED - If the user has been verified by Twitter
	8. FOLLOWERS_COUNT - The number of users following the user in question
	9. DESCRIPTION - The length of the description field in the user's profile
	10. URL - If the user profile is associated with a URL
	11. LOCATION - If the user profile specifies a location


taptimelines.py
---------------
Extracts upto (approximately) 3,200 tweets from the timelines of saved users.


getuserstats.py
---------------
Uses the stored user timeline to extract the following additional information:

	1. REPLIES - The number of statuses marked replies (by the field 'in_reply_to_user_id')
	2. MENTIONS - The number of '@' symbols in the recorded statuses
	3. RETWEETS_OF_USER_TWEETS - The sum of the retweet_count in all examined statuses
	4. RETWEETS_BY_USER - The number of retweets posted by the user 
	5. FAVORITE_COUNT_FOR_USER - The number of 'favorites' acquired by user statuses across all examined statuses
	6. HASHTAGS - The number of hashtags used across all examined user status
	7. BROADCAST_COMMS - The number of statuses that have no mentions (the '@' symbol) in them
	8. QUOTES - The number of quoted statuses across all user statuses
	9. URLS - The number of posted URLs across all user statuses
	10. TWEETS_EXAMINED - The number of user statuses examined


makemodel.R
------------
Uses a log-log linear model to predict FOLLOWERS_COUNT.



MODEL CONSTRUCTION
------------------

The predictors under consideration (in addition to the ones mentioned above) are:
	
	1. USER_AGE - The time elapsed (in days) since the user account was created

The correlation table plotting all predictors against each other can be found in model/metrics/correlation/table.txt
The scatter plots of all predictors vs FOLLOWERS_COUNT can be found in model/metrics/correlation/plots/FOLLOWERS_COUNT_vs_everything_else.pdf

The data is filtered based on the following critera:
	
	1. USER_AGE > 30 - To account for newly minted users whose followers are real-world acquaintances
	2. FRIENDS_COUNT > 15 - To account for users whose friends are real-world acquaintances
	3. STATUSES_COUNT > 10 - To weed out inactive users
	4. STATUSES_COUNT < 100000 - To allow for accurate sampling of user timelines with 3,200 statuses
	5. FOLLOWERS_COUNT < 100000 - To dissociate FOLLOWERS_COUNT from the effect of users (such as those who have been verified) who are famous in real life
	6. FOLLOWERS_COUNT > 50 - To account for users whose followers are only real-world acquaintances

After filtering the data it was found that none of the remaining users were verified, this column from hence dropped from the data.

The data was modeled using support vector regression (the e1071 library)

The standardized and regression coefficients can be found in model/result/tables/std_coefs.txt and model/result/tables/reg_coefs.txt 

The graph of actual vs predicted follower counts can be found in model/result/plots/ACTUAL_vs_PREDICTED.pdf

Tabulated errors (FOLLOWERS_COUNT, PREDICTED, ABS_DIFF_FROM_PRED and PERC_DIFF_FROM_PRED) can be found in model/result/tables/errors.csv

The average percentage error in perdiction (53.2%) can be found in model/result/tables/eval.txt