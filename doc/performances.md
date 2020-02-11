# Highlight

## September test set

| Bundler | decrease percentage | user spammed above 4 notifications per day (rate) | number of notifications above 4 bundled notifications per day (rate) | Average delay | Median delay | Bundler processing time |
| --- | --- | --- | --- | --- | --- | --- |
| Naive bundler | 0% | 10.65% | 47.27% | 0h 0m 0s | 0h 0m 0s | 0.8s |
| Cheater bundler | 47.27% | 0% | 0% | 0h 40m 9s | 0h 0m 0s | 113.3s |
| Waiter bundler (1h) | 42.99% | **7.14%** | 13.46% | 0h 47m 23s | 1h 0m 0s | **0.87s** |
| Statistical bundler (training august) | **43.19%** | 8.08% | **10.37%** | **0h 53m 21s** | **0h 33m 31s** | 12.55s |
| Statistical bundler (train all data) | 44.94% | 7.94% | 7.85% | 0h 53m 30s | 0h 34m 16s | 12.29s |

### Comments

- The WaiterBundler seems to be a good first approximation. It is a simple algorithm but it works well to efficiently reduce the number of notifications above 4 per day (47.27% to 13.46%). However, the drawback of this simplicity is that the delay is often of 1 hour.
- The StatisticalBundler performs better by adding new parameters to the algorithm. It significantly reduces the delay (almost by half) while increasing performances (13.46% to 10.37%).
- Given those results, we have good evidence that defining more parameters will certainly get better results. As discussed in the `DelayPredictor` section, we could try to label users by their 'criticality' (based on the number of received notifications or based on their friend). Another possibility would be to predict the number of notifications that will be sent on a certain day, based on the data received at 11am and adapt the delays accordingly.
- Finally, we can also observe that the split between train/test august/september was necessary in order to test the StatisticalBundler on unseen data. In a production environment, we could think of retraining the StatisticalBundler every period of time (every day ? every week ? every month ?).

# Full results

## Naive Bundler performances

| naive bundler | decrease percentage | user spammed above 4 notifications per day (rate) | number of notifications above 4 bundled notifications per day (rate) | Average delay | Median delay | Bundler processing time |
| --- | --- | --- | --- | --- | --- | --- |
| train_august | 0% | 10.1% | 39.06% | 0h 0m 0s | 0h 0m 0s | 1.39s |
| test_august | 0% | 10.97% | 43.76% | 0h 0m 0s | 0h 0m 0s | 1.12s |
| train_september | 0% | 10.15% | 43.55% | 0h 0m 0s | 0h 0m 0s | 1.09s |
| test_september | 0% | 10.65% | 47.27% | 0h 0m 0s | 0h 0m 0s | 0.8s |
| all_dataset | 0% | 11.0% | 42.92% | 0h 0m 0s | 0h 0m 0s | 4.46s |

## Cheater Bundler performances

| cheater bundler | decrease percentage | user spammed above 4 notifications per day (rate) | number of notifications above 4 bundled notifications per day (rate) | Average delay | Median delay | Bundler processing time |
| --- | --- | --- | --- | --- | --- | --- |
| train_august | 39.06% | 0% | 0% | 0h 33m 15s | 0h 0m 0s | 103.84s |
| test_august | 43.76% | 0% | 0% | 0h 41m 45s | 0h 0m 0s | 81.7s |
| train_september | 43.55% | 0% | 0% | 0h 34m 7s | 0h 0m 0s | 71.97s |
| test_september | 47.27% | 0% | 0% | 0h 40m 9s | 0h 0m 0s | 113.3s |
| all_dataset | 42.92% | 0% | 0% | 0h 36m 50s | 0h 0m 0s | 424.15s |

## Waiter Bundler performances

| waiter bundler (1h) | decrease percentage | user spammed above 4 notifications per day (rate) | number of notifications above 4 bundled notifications per day (rate) | Average delay | Median delay | Bundler processing time |
| --- | --- | --- | --- | --- | --- | --- |
| train_august | 35.96% | 6.15% | 12.09% | 0h 49m 23s | 1h 0m 0s | 1.62s |
| test_august | 39.78% | 6.98% | 13.8% | 0h 48m 11s | 1h 13.8% | 0m 0s | 1.11s |
| train_september | 39.86% | 6.54% | 11.94% | 0h 48m 21s | 1h 0m 0s | 1.31s |
| test_september | 42.99% | 7.14% | 13.46% | 0h 47m 23s | 1h 0m 0s | 0.87s |
| all_dataset | 39.23% | 6.04% | 12.7% | 0h 48m 27s | 1h 0m 0s | 5.23s |

## Statistical Waiter Bundler performances

#### August training

| statistical waiter bundler (august training) | decrease percentage | user spammed above 4 notifications per day (rate) | number of notifications above 4 bundled notifications per day (rate) | Average delay | Median delay | Bundler processing time |
| --- | --- | --- | --- | --- | --- |  --- |
| train_august | 35.9% | 7.4% | 7.97% | 0h 48m 45s | 0h 25m 40s | 22.98s |
| test_august | 39.6% | 7.91% | 9.54% | 0h 51m 35s | 0h 26m 33s | 14.15s |
| train_september | 39.91% | 7.32% | 9.15% | 0h 51m 7s | 0h 27m 50s | 22.93s |
| test_september | 43.19% | 8.08% | 10.37% | 0h 53m 21s | 0h 33m 31s | 12.55s |
| all_dataset | 39.28% | 7.54% | 8.93% | 0h 51m 15s | 0h 26m 43s | 70.87s |

#### All notifications training

| statistical waiter bundler (all dataset - /!\ biased) | decrease percentage | user spammed above 4 notifications per day (rate) | number of notifications above 4 bundled notifications per day (rate) | Average delay | Median delay | Bundler processing time |
| --- | --- | --- | --- | --- | --- |  --- |
| train_august | 36.48% | 7.08% | 6.85% | 0h 53m 2s | 0h 33m 16s | 23.11s |
| test_august | 40.61% | 7.59% | 8.01% | 0h 55m 53s | 0h 34m 29s | 14.1s |
| train_september | 41.65% | 7.17% | 6.83% | 0h 51m 5s | 0h 31m 58s | 14.79s |
| test_september | 44.94% | 7.94% | 7.85% | 0h 53m 30s | 0h 34m 16s | 12.29s |
| all_dataset | 40.46% | 7.14% | 7.31% | 0h 53m 51s | 0h 34m 29s | 63.96s |
