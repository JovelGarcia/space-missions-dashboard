# Space Missions Dashboard

## Data Table View
- Contains sorting
- Contains filtering
- Contains search

## 3 Visualizations

### Visualization 1
- I chose this visualization as it shows the success rate trend over time when looking at a general view. In addition, the visualization can be utilized alongside filters to compare success rates between 2+ companies.

### Visualization 2
- I chose this visualization as it shows the formation and demise of the top 10 companies with total missions. In addition, the visualization can be utilized alongside the 'year range' filter to compare how the 'top N' companies by total missions changes over time. Similarly, the 'company' filter can allow for comparisons between 2+ companies.

### Visualization 3
- I chose this visualization as it provides great "at a glance" insights, along with the other 2 visuals, while allowing for specific values (on hover) for totals in success, failure, etc.

## Interactive Filters
- allows users to filter by date range, company, and mission status - affects all visualizations

## Summary Statistics
- provides vital insight to entirety of data set: total missions, overall success rate, total companies, average missions per year, most used rocket, and year range.

## Quick Lookup
- Added to utilize ALL `data_processing.py` functions within the frontend.

### Querying total missions given a year
- utilizes `getMissionsByYear()`

### Average missions per year given a range of years
- utilizes `getAverageMissionsPerYear()`

### Custom table view of missions given a range of dates
- utilizes `getMissionsByDateRange()`