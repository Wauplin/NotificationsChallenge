# Components :

- **Streamer** : component that loads and preprocesses the data. It is the entry to any model.
- **Bundler** : Bundler is the name given to the object that contains a grouping algorithm. It takes as input a stream and export a CSV with all bundled notifications. BaseNotificationBundler is a base object that is inherited by every Bundler. It contains methods that reads the notifications, call the algorithm and export the output.
- **Reviewer** : component that compares initial notifications to bundled notifications. First, it verifies that the output is correct (all notifications sent once and after the initial timestamp). Then it computes a few interesting metrics to evaluate the model.
- **Delay predictor** : Model to predict how much time we need to wait before sending a notification.


# Bundlers :

## Base Bundler

This bundler is not actionable by itself but is inherited by every other bundler.

## Naive Bundler

First bundler that I built. The only behavior is to keep all notifications as they are and send them with zero-second delay. Goal is to have a first integration Streamer-Bundler-Reviewer that properly works.   
**Benefits :** almost no implementation needed. Delay is minimal.  
**Drawbacks :** users are over-spammed.   

#### Metrics

| naive bundler | decrease percentage | user spammed above 4 notifications per day (rate) | Average delay | Median delay | Bundler processing time |
| --- | --- | --- | --- | --- | --- |
| train_august | 0% | 10.1% | 0h 0m 0s | 0h 0m 0s | 1.39s |
| test_august | 0% | 10.97% | 0h 0m 0s | 0h 0m 0s | 1.12s |
| train_september | 0% | 10.15% | 0h 0m 0s | 0h 0m 0s | 1.09s |
| test_september | 0% | 10.65% | 0h 0m 0s | 0h 0m 0s | 0.8s |
| all_dataset | 0% | 11.0% | 0h 0m 0s | 0h 0m 0s | 4.46s |

## Cheater Bundler

This bundler cheats and breaks the implicit rule that the algorithm cannot see the future notifications. Internally, it looks at all the notifications received by each user each day. Then it does a k-means clustering on the 1-D vector of notification timestamps (k=4). This way, it is impossible that the system sends more than 4 notifications per user per day. The goal is to know what is the best case scenario.  
**Benefits :** no users spammed and delay can't be improved.  
**Drawbacks :** cheats.

#### Metrics

| cheater bundler | decrease percentage | user spammed above 4 notifications per day (rate) | Average delay | Median delay | Bundler processing time |
| --- | --- | --- | --- | --- | --- |
| train_august | 39.06% | 0% | 0h 33m 15s | 0h 0m 0s | 103.84s |
| test_august | 43.76% | 0% | 0h 41m 45s | 0h 0m 0s | 81.7s |
| train_september | 43.55% | 0% | 0h 34m 7s | 0h 0m 0s | 71.97s |
| test_september | 47.27% | 0% | 0h 40m 9s | 0h 0m 0s | 113.3s |
| all_dataset | 42.92% | 0% | 0h 36m 50s | 0h 0m 0s | 424.15s |

## Waiter Bundler

The Waiter Bundler is bundler that has a simple algorithm. First time a notification is received for a user, we keep it aside for a certain delay (ex: 1 hour). Once the delay has expired, the notification is sent bundled with all the notifications that have been received during this period.  
**Benefits :** some notifications are bundled : number of spammed users decreases.  
**Drawbacks :** there is some place for improvements.  
In the current implementation, there is no guaranty that the notification will be sent on the same day.  

#### Metrics

| waiter bundler (1h) | decrease percentage | user spammed above 4 notifications per day (rate) | Average delay | Median delay | Bundler processing time |
| --- | --- | --- | --- | --- | --- |
| train_august | 35.96% | 6.15% | 0h 49m 23s | 1h 0m 0s | 1.62s |
| test_august | 39.78% | 6.98% | 0h 48m 11s | 1h 0m 0s | 1.11s |
| train_september | 39.86% | 6.54% | 0h 48m 21s | 1h 0m 0s | 1.31s |
| test_september | 42.99% | 7.14% | 0h 47m 23s | 1h 0m 0s | 0.87s |
| all_dataset | 39.23% | 6.04% | 0h 48m 27s | 1h 0m 0s | 5.23s |

## Statistical Waiter Bundler

The Statistical Waiter Bundler is an advance version of the previous one. The idea is to apply a different delay to each notification based on several features. This bundler instantiate a DelayPredictor (see below) that decides by how much time the notification must be delayed.  
**Benefits :** does not process all notifications the same which allows better performances (if DelayPredictor is good). Quite simple to implement and extend with new features.  
**Drawbacks :** again, there is place for improvements. For instance, the WaiterBundler do not take into account the number of notifications received during the 1-hour timer. Sometimes, it could be interesting to use this feature to modulate the initial delay.  

#### Metrics (august training)

| statistical waiter bundler (august training) | decrease percentage | user spammed above 4 notifications per day (rate) | Average delay | Median delay | Bundler processing time |
| --- | --- | --- | --- | --- | --- |
| train_august | 35.9% | 7.4% | 0h 48m 45s | 0h 25m 40s | 22.98s |
| test_august | 39.6% | 7.91% | 0h 51m 35s | 0h 26m 33s | 14.15s |
| train_september | 39.91% | 7.32% | 0h 51m 7s | 0h 27m 50s | 22.93s |
| test_september | 43.19% | 8.08% | 0h 53m 21s | 0h 33m 31s | 12.55s |
| all_dataset | 39.28% | 7.54% | 0h 51m 15s | 0h 26m 43s | 70.87s |

#### Metrics (all notifications training)

| statistical waiter bundler (all dataset - /!\ biased) | decrease percentage | user spammed above 4 notifications per day (rate) | Average delay | Median delay | Bundler processing time |
| --- | --- | --- | --- | --- | --- |
| train_august | 36.48% | 7.08% | 0h 53m 2s | 0h 33m 16s | 23.11s |
| test_august | 40.61% | 7.59% | 0h 55m 53s | 0h 34m 29s | 14.1s |
| train_september | 41.65% | 7.17% | 0h 51m 5s | 0h 31m 58s | 14.79s |
| test_september | 44.94% | 7.94% | 0h 53m 30s | 0h 34m 16s | 12.29s |
| all_dataset | 40.46% | 7.14% | 0h 53m 51s | 0h 34m 29s | 63.96s |

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
