## Motivation and Purpose

Food security and supply are fundamental to human survival, but many developing countries still face food shortages and insecurity. NGOs work to enhance food security through various programs, while policymakers develop policies to improve food supply in these regions. Our goal is to provide data-driven support for NGOs and policymakers to optimize decision-making and resource allocation. To achieve this, we will develop a dashboard that monitors food conditions in developing countries in real time, including key indicators such as food trends, affordability, and price fluctuations. This tool will help identify the regions that need assistance and enable the design and implementation of more effective food aid programs or policies.

## Description of the Data

The dataset used in this project is the [Global Food Prices](https://data.humdata.org/dataset/global-wfp-food-prices) dataset from the World Food Programme, which contains approximately 300,000 records of monthly food prices across 98 developing countries and 3,000 markets from January 1990 to February 2025. Key variables include the date of the record, market location (city with latitude/longitude), food category (e.g., cereals, oils, tubers), specific food item, local currency, price, and price in USD.

To supplement this dataset, we will incorporate the adjusted net national income per capita (US$) from the past ten years, sourced from the [World Development Indicators](https://databank.worldbank.org/source/world-development-indicators). This will allow us to derive a new variable as an indicator of food affordability per country, providing additional context to price trends. Moreover, we will incorporate the prevalence of undernourishment of different countries from the past twenty years, sourced from the [Food and Agriculture Organization](https://www.fao.org/faostat/en/#data/FS). 

## Research Questions and Usage Scenarios

Ann is a staff member at the World Food Programme (WFP), currently preparing a proposal for a food aid project targeting specific regions in developing countries. To ensure the project's effectiveness, she needs to understand the food security situation in the target areas, including food affordability, price fluctuations, and demand levels. This information will help her identify the project's target beneficiaries and develop specific implementation strategies.  
She hopes to explore datasets and use an interactive dashboard to visualize food prices and demand trends in developing countries. By doing so, she can identify markets with low food affordability and high prices, enabling her to design targeted intervention measures.  
When Ann logs into the visualization dashboard, she first sees an overview of food pricing across developing countries and the proportion of the population suffering from malnutrition. By analyzing these two visualizations together, she can identify the target countries that need assistance.  
Furthermore, Ann can switch to the country-level analysis page to examine the food situation in greater detail. After selecting a country, she can view a map displaying regional price variations and analyze food affordability. She can also track commodity price fluctuations to identify food categories with unstable prices.  
By comparing food affordability across multiple countries, Ann may find that sub-Saharan Africa has the lowest affordability. She hypothesizes that this is due to high demand for grain products combined with price instability. However, since the dataset and dashboard lack information on grain supply chain models in this region, she decides to conduct further research to validate her hypothesis and better understand the factors affecting food affordability. Based on her findings, she can then develop a more targeted food aid strategy to improve food security in the region.  

The dashboard can help answer the following questions:  
Which countries are struggling the most with food affordability recently?  
How have food prices changed over the years?  
Which countries saw the fastest increase in food prices?  
Which markets within countries are the most vulnerable?  
How much do prices vary within categories/countries? Is there seasonal variation?  
Which type of commodity has the most unstable prices in a specific region of a country?  
Which cities in a country are in need of assistance?  

