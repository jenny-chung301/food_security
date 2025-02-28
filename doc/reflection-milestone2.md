# Milestone 2 - Reflection

For this milestone, we have prototyped the five key plots for the dashboard:
1. Average commodity prices over time, by country
2. The share of the population that is undernourished, by country and over time
3. A map displaying food price volatility across country regions
4. Price distributions for different commodity categories
5. The top 20 most expensive commodities per region

So far, most of the intended functionality for these plots has been implemented, including:
- Separation of plots into Global and Country tabs for different analysis levels
- All plots have placeholder values for default states
- All plots are able to dynamically update with changes to dropdown selections
- Changing the commodity selection updates the available country options in the Global tab
- Shared country dropdown and year range slider used to update both Global plots
- Interactivity, where clicking market indicators on the map updates the commodity category distributions and top 20 most expensive commodities for the selected region
  
Some bugs exist in terms of styling which will be amended by the next milestone:
- Clearing all selections in the Select Country dropdown in the Global tab leaves plots empty
- The map does not dynamically resize with the viewport

Future developments will focus on:
- Enhancing styling consistency across tabs and states
- Improving interpretability with additional titles, subtitles, and context of the dashboard
- Boosting usability with clear instructions on how to use the dashboard, as well as the ability to revert states
- Enhancing visual aesthetic (e.g. tab containerization, better sizing and spacing of elements)
- Integrating additional key statistics (e.g. food affordability index)
