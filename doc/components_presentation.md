# Components :

- **Streamer** : component that loads and preprocesses the data. It is the entry to any model.
- **Bundler** : Bundler is the name given to the object that contains a grouping algorithm. It takes as input a stream and export a CSV with all bundled notifications. BaseNotificationBundler is a base object that is inherited by every Bundler. It contains methods that reads the notifications, call the algorithm and export the output.
- **Reviewer** : component that compares initial notifications to bundled notifications. First, it verifies that the output is correct (all notifications sent once and after the initial timestamp). Then it computes a few interesting metrics to evaluate the model.
- **Delay predictor** : Model to predict how much time we need to wait before sending a notification.


# Bundlers :

Performances of each bundler are available in the `performances` section.

## Base Bundler

This bundler is not actionable by itself but is inherited by every other bundler.

## Naive Bundler

First bundler that I built. The only behavior is to keep all notifications as they are and send them with zero-second delay. Goal is to have a first integration Streamer-Bundler-Reviewer that properly works.   
**Benefits :** almost no implementation needed. Delay is minimal.  
**Drawbacks :** users are over-spammed.   

## Cheater Bundler

This bundler cheats and breaks the implicit rule that the algorithm cannot see the future notifications. Internally, it looks at all the notifications received by each user each day. Then it does a k-means clustering on the 1-D vector of notification timestamps (k=4). This way, it is impossible that the system sends more than 4 notifications per user per day. The goal is to know what is the best case scenario.  
**Benefits :** no users spammed and delay can't be improved.  
**Drawbacks :** cheats.


## Waiter Bundler

The Waiter Bundler is bundler that has a simple algorithm. First time a notification is received for a user, we keep it aside for a certain delay (ex: 1 hour). Once the delay has expired, the notification is sent bundled with all the notifications that have been received during this period.  
**Benefits :** some notifications are bundled : number of spammed users decreases.  
**Drawbacks :** there is some place for improvements.  
In the current implementation, there is no guaranty that the notification will be sent on the same day.  


## Statistical Waiter Bundler

The Statistical Waiter Bundler is an advance version of the previous one. The idea is to apply a different delay to each notification based on several features. This bundler instantiate a DelayPredictor (see below) that decides by how much time the notification must be delayed.  
**Benefits :** does not process all notifications the same which allows better performances (if DelayPredictor is good). Quite simple to implement and extend with new features.  
**Drawbacks :** again, there is place for improvements. For instance, the WaiterBundler do not take into account the number of notifications received during the 1-hour timer. Sometimes, it could be interesting to use this feature to modulate the initial delay.  


# Delay Predictor :

The DelayPredictor is the component associated to the Statistical Waiter Bundler. The current implementation is based on 3 features :
- period of the day : morning, afternoon, evening or night.
- number of notifications already sent that day : 0, 1, 2 or 3+.
- the day of the week : Monday, Tuesday, Wednesday, Thursday, Friday, Saturday or Sunday.  

### Mode of operation :
- Take a train dataset of notifications.
- Process it with the CheaterBundler to get the best possible delay by notification.
- Assign a category (out of `4 * 7 * 4 = 112`) to each notification.
- Group notifications by category and compute the average delay. Training is now finished.
- Inference : for each (not bundled) new notification, return the average delay assigned to its category.


### Possible improvements :
I can see a lot of ways to increase the DelayPredictor performances, based on the same concept. Other features that could be used :
- a receiver-based metric. Some users has a lot of sportive friends while others are rarely disturb.  
- a per-day metric continuously reassessed. For instance, at 11am, we can have a good idea whether or not the day will be very busy (compared to a average day). On the same idea, sunny days are more likely to be busy than rainy days. It can be a good feature to use data from external sources.
- take into account which friend sent the notification. It is very-likely that we can find patterns in the behavior of each friend or group of friends. This option might be much more difficult to implement since it requires working with something like a social graph.
- take into account the country / region of the users and friends (not provided here). One might not be bothered if only 1 notification with more delay is received during the night rather than several. The Statistical Waiter could also benefit from geographical provenance since habits (and weather) might not be globally shared.
- We might in some cases be capable to predict notifications since we knows when our users are going for a tour.
