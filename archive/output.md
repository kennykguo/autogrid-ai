Energy Production Variables
Current Solar Power Generation (kW)
Source: Open Power System Data (OPSD) - open-power-system-data.org
Provides historical time series of solar generation for various European countries at hourly or sub-hourly resolution.
Example: German solar generation data from transmission system operators (TSOs).
Source: U.S. Energy Information Administration (EIA) - www.eia.gov
Real-time hourly electric grid data (e.g., Form EIA-930) for U.S. regions, including solar generation.
Accessibility: Publicly available, downloadable as CSV or Excel.
Notes: Granularity varies by region (e.g., 15-min in some datasets, hourly in others). You may need to scale to kW for local systems.
Current Wind Power Generation (kW)
Source: OPSD
Includes wind generation time series from European TSOs.
Source: EIA
Hourly wind generation data for U.S. balancing authorities.
Source: Chinese State Grid Renewable Energy Dataset - Figshare or GitHub
Two years (2019–2020) of 15-minute wind farm data from China.
Accessibility: Open access, often in Excel format.
Notes: Similar to solar, scaling may be needed for local kW-level analysis.
Forecasted Solar Generation (24-48 Hours)
Source: National Renewable Energy Laboratory (NREL) Solar Integration Data - www.nrel.gov
Datasets like the Western Wind and Solar Integration Study include simulated forecasts based on weather models.
Source: ECMWF (European Centre for Medium-Range Weather Forecasts) - www.ecmwf.int
Reanalysis data (e.g., ERA5) paired with solar models can simulate forecasts.
Accessibility: Some free tiers (e.g., ERA5 via CDS API), others require registration or fees.
Notes: Forecasts aren’t directly provided; you’d need to derive them from weather data and generation models.
Forecasted Wind Generation (24-48 Hours)
Source: NREL Wind Integration National Dataset (WIND Toolkit)
Simulated wind power forecasts based on historical weather data.
Source: ECMWF ERA5
Wind speed forecasts can be converted to generation using turbine power curves.
Accessibility: Publicly available, some preprocessing required.
Notes: Requires a wind turbine model to translate wind speed to kW.
Generation Capacity Limits
Source: OPSD
Installed capacity data for solar and wind by region or country.
Source: EIA
Monthly Electric Generator Inventory lists capacity for U.S. facilities.
Source: IRENA Renewable Capacity Statistics - www.irena.org
Global installed capacity data.
Accessibility: Free, downloadable as CSV/PDF.
Notes: Static data; you’d need to assume these as upper bounds for your RL environment.
Energy Storage Variables
These variables are harder to source publicly due to their proprietary or site-specific nature, but some proxies or simulated data exist.

Current Battery State of Charge (%)
Source: None directly available publicly at scale.
Alternative: NREL OpenEI Datasets - openei.org
Simulated battery dispatch data from microgrid studies (e.g., HOMER models).
Notes: You’d need to simulate this based on charge/discharge actions and initial assumptions.
Battery Health/Degradation Metrics
Source: None directly available.
Alternative: Academic Datasets (e.g., NASA Battery Dataset) - data.nasa.gov
Lab-based degradation data for lithium-ion batteries.
Notes: Not real-world grid data; requires adaptation.
Maximum Charge/Discharge Rates, Battery Capacity (kWh), Charging/Discharging Efficiency
Source: Manufacturer Specs or Simulated Data
Tesla Powerwall or generic battery specs from NREL’s System Advisor Model (SAM).
Source: PJM Battery Storage Data - www.pjm.com
Aggregated storage capacity and performance metrics (limited detail).
Accessibility: Public specs or simulation tools (SAM is free).
Notes: Assume typical values (e.g., 80-95% efficiency) or simulate based on capacity.
Energy Demand Variables
Current Local Energy Demand (kW)
Source: EIA Hourly Electric Grid Monitor
U.S. regional demand at hourly resolution.
Source: OPSD
European load profiles by country.
Accessibility: Free, downloadable.
Notes: May need to downscale to local kW levels.
Forecasted Demand (24-48 Hours)
Source: PJM Load Forecast - www.pjm.com
Historical and forecasted demand for PJM regions.
Source: ENTSO-E Transparency Platform - transparency.entsoe.eu
European demand forecasts.
Accessibility: Free, API access available.
Notes: Granularity varies; preprocessing needed for 24-48 hour horizon.
Critical Load Requirements
Source: Local Utility Reports or NREL Microgrid Studies
Example: NREL’s REopt tool datasets include critical load assumptions.
Accessibility: Public, some require registration.
Notes: Often generalized; may need to define based on your use case.
Grid Interaction Variables
Current Grid Electricity Price ($/kWh)
Source: EIA Wholesale Electricity Prices
Hourly wholesale prices for U.S. markets.
Source: ENTSO-E Transparency Platform
Day-ahead prices for European markets.
Accessibility: Free, downloadable.
Notes: Reflects wholesale, not retail; adjust for local context.
Forecasted Grid Prices (24-48 Hours)
Source: ENTSO-E
Day-ahead market forecasts.
Source: PJM Market Data
Forecasted locational marginal prices (LMPs).
Accessibility: Free, API or CSV.
Notes: Historical forecasts can train the RL model.
Grid Import/Export Limits
Source: Utility or TSO Data (e.g., PJM, ERCOT)
Interconnection limits from grid operators.
Notes: Often site-specific; assume typical values (e.g., 10-100 kW) if unavailable.
Grid Connection Status
Source: Simulated or Historical Outage Data
EIA or NREL outage datasets for U.S.
Notes: Rare in public datasets; simulate islanded/connected states.
Environmental Variables
Current Weather Conditions (Temperature, Cloud Cover, Wind Speed)
Source: NOAA National Climatic Data Center - www.ncdc.noaa.gov
Hourly weather data globally.
Source: Chinese State Grid Dataset
Weather paired with generation data.
Accessibility: Free, API or CSV.
Forecasted Weather (24-48 Hours)
Source: ECMWF ERA5 or NOAA GFS
Historical forecasts for temperature, wind, and solar irradiance.
Accessibility: Free tiers available.
Notes: Use to predict generation and demand impacts.
Time of Day, Day of Week, Season
Source: Any Time-Series Dataset
Included in OPSD, EIA, or weather datasets.
Accessibility: Trivial to generate or extract.
Action Space Alignment
Your RL agent’s actions can be simulated using these datasets:

Battery Management: Use simulated battery data (e.g., from NREL SAM) with charge/discharge rates tied to generation and demand data.
Grid Interaction: Leverage price and import/export data from EIA or ENTSO-E to decide buying/selling amounts.
Load Management: Shift demand based on forecasted demand and price peaks (PJM, ENTSO-E).
Generation Control: Limited to fixed solar/wind in most datasets; assume curtailment as an action if needed.
Recommended Datasets
Chinese State Grid Dataset (2019–2020)
Solar/wind generation, weather, 15-min resolution.
Ideal for integrated generation-weather modeling.
EIA Hourly Grid Data
U.S.-focused, covers generation, demand, and prices.
OPSD
European focus, comprehensive generation and demand data.
NREL SAM + ECMWF ERA5
Simulate battery and forecast generation/demand.
Gaps and Solutions
Battery Data: Simulate using NREL tools or assume typical specs.
Grid Limits/Status: Use regional averages or simulate outages.
Forecasts: Derive from historical weather and generation data using statistical models.
These datasets provide a solid foundation for your RL model. You’ll need to preprocess and integrate them into a cohesive environment, potentially using a simulator like OpenAI Gym to test actions. Let me know if you need help with specific preprocessing steps or simulation design!









Search Results

Solar and wind power data from the Chinese State Grid Renewable Energy Generation Forecasting Competition | Scientific Data
Accurate solar and wind generation forecasting along with high renewable energy penetration in power grids throughout the world are crucial to the days-ahead power scheduling of energy systems. It is difficult to precisely forecast on-site power generation due to the intermittency and fluctuation characteristics of solar and wind energy. Solar and wind generation data from on-site sources are beneficial for the development of data-driven forecasting models. In this paper, an open dataset consisting of data collected from on-site renewable energy stations, including six wind farms and eight solar stations in China, is provided. Over two years (2019–2020), power generation and weather-related data were collected at 15-minute intervals. The dataset was used in the Renewable Energy Generation Forecasting Competition hosted by the Chinese State Grid in 2021.

nature.com
Solar and wind to lead growth of U.S. power generation for the next two years - U.S. Energy Information Administration (EIA)
Energy Information Administration - EIA - Official Energy Statistics from the U.S. Government

eia.gov
A Decade of Growth in Solar and Wind Power: Trends Across the U.S. | Climate Central
Climate Central bridges the scientific community and the public, providing clear information to help people make sound decisions about the climate.

climatecentral.org
Data Sources – Open Power System Data
A platform for open data of the European power system.

open-power-system-data.org
Solar Industry Research Data – SEIA
Solar Industry Research Growing at a Record Pace Solar energy in the United States is booming. Along with our partners at Wood Mackenzie Power & Renewables, SEIA tracks trends and trajectories in the...

seia.org
2025 Renewable Energy Industry Outlook | Deloitte Insights
Renewables race to fill resource gap as demand for clean energy is outpacing supply

www2.deloitte.com
Global Market Outlook For Solar Power 2023 - 2027 - SolarPower Europe
Are you a member? Log in to the members area to get access to all stats and figures

solarpowereurope.org
Solar and wind power data from the Chinese State Grid Renewable Energy Generation Forecasting Competition - PMC
Accurate solar and wind generation forecasting along with high renewable energy penetration in power grids throughout the world are crucial to the days-ahead power scheduling of energy systems. It is difficult to precisely forecast on-site power ...

pmc.ncbi.nlm.nih.gov
Growth of Renewable Energy in the US | World Resources Institute
After several record-breaking years, the U.S. clean energy sector faces a critical moment.Solar deployment and electric vehicle (EV) sales broke records in 2023 and 2024. Renewables now dominate new power generation capacity, while new domestic clean energy manufacturing facilities are popping up around the nation.

wri.org
Energy Dashboard - real time and historical GB National Grid electricity data, carbon emissions and UK generation sites mapping
Live and historical GB National Grid electricity data, showing generation, demand and carbon emissions and UK generation sites mapping with API subscription service.

energydashboard.co.uk
Forecasting — Greening the Grid
Forecasting Wind and Solar Generation. English (PDF). Español (PDF) · To reduce the uncertainty inherent in demand and generation, system operators rely upon load and generation forecasts to balance electricity supply and demand. Accurate forecasts not only support the safe and reliable operation of the grid, but also encourage cost effective operation by improving the scheduling of generation and reducing the use of reserves. The better and more frequent the opportunities to use forecasts, the more impact that forecasts will have on systems operations

greeningthegrid.org
Solar, battery capacity saved the Texas grid last summer; an uncertain future awaits - Dallasfed.org
As ERCOT forecasts accelerated load growth due to anticipated data center construction and electrification trends, the current generation mix and market design should garner increased scrutiny.

dallasfed.org
Short-Term Energy Outlook - U.S. Energy Information Administration (EIA)
Energy Information Administration - EIA - Official Energy Statistics from the U.S. Government

eia.gov
Wind & Solar Share in Electricity Production Data | Enerdata
Weight of solar and wind in electricity production data. Data for solar and wind renewable energies in electricity production available in a map and excel file by country level.

yearbook.enerdata.net
Wind and solar to produce over a third of global power by 2030, report says | Reuters
Wind and solar projects are on track to account for more than a third of the world's electricity by 2030, signalling that the energy sector can achieve the change needed to meet global climate goals, a report by the Rocky Mountain Institute (RMI) said on Thursday.

reuters.com
Renewable Energy - Our World in Data
Renewable energy sources are growing quickly and will play a vital role in tackling climate change.

ourworldindata.org
Global Energy Perspective 2023: Power outlook | McKinsey
Globally, power demand is expected to grow, with renewables accounting for an increasing proportion of the power mix.

mckinsey.com
We expect solar will supply almost all growth in U.S. electricity generation through 2025 - U.S. Energy Information Administration (EIA)
Energy Information Administration - EIA - Official Energy Statistics from the U.S. Government

eia.gov
European Electricity Review 2025 | Ember
The EU’s electricity transition continued at pace in 2024, as solar overtook coal for the first time and gas declined for the fifth year in a row.

ember-energy.org
2025 Long-Term Load Forecast Report Predicts Significant Increase in Electricity Demand | PJM Inside Lines
PJM reviews the requests, gauging their significance and risk of double-counting; for example, is the trend likely to have been captured in the economic forecast? For the 2025 Long-Term Load Forecast, these include: Data centers (AEP, APS, ATSI, BGE, ComEd, Dayton, PECO, PL, PS, Dominion) ... This report includes long-term forecasts of peak loads, net energy, load management, distributed solar generation, plug-in electric vehicles (EVs) and battery storage for each PJM zone, region, locational deliverability area and the total RTO. The long-term forecast is for planning purposes and is separate from the daily and weekly forecasts performed by PJM Operations to prepare for daily load changes. The PJM long-term load forecast is constructed using 24 hourly models for each transmission zone. In each model, load is the dependent variable, considered alongside weather, calendar events, ...

insidelines.pjm.com


To address the research needs for training a reinforcement learning (RL) model in energy management, several publicly available datasets from the provided sources can be leveraged across the required state variables. Below is a structured breakdown of relevant datasets and their applicability to each category:

Energy Production Variables
Solar Power Generation & Forecasts
NREL Solar Power Data for Integration Studies

Provides synthetic 5-minute solar power data for 6,000+ hypothetical PV plants in the U.S. (2006 data). Includes day-ahead forecasts and capacity limits6.

Key variables: Current solar generation, forecasted solar generation (hourly), generation capacity limits.

Solargis

Offers 15-minute time-series solar data (up to 30 years) with high temporal (1-minute) and spatial (250 m) resolution. Includes probabilistic forecasts for future periods2.

Key variables: Solar generation forecasts (24–48 hours), weather-linked generation adjustments.

PVGIS (Photovoltaic Geographical Information System)

Free solar energy potential estimates for Europe and other regions, including hourly historical data and forecasts4.

Household Data Package

Includes 1-minute resolution solar generation data for residential systems, useful for granular simulations7.

Wind Power Generation & Forecasts
IEA Wind TCP Open Data

Danish Energy Agency datasets provide monthly wind turbine output, technical specs, and location data for Denmark8.

Key variables: Current wind generation (with regional limitations).

Energy Storage Variables
Most datasets do not explicitly include battery metrics. However:

Household Data Package may indirectly support battery modeling through load/generation time-series analysis7.

Synthetic data or physics-based battery models (e.g., using degradation equations) are recommended for variables like state of charge or efficiency.

Energy Demand Variables
Household Data Package

Contains 1-minute resolution electricity consumption data for households and small businesses, including critical load patterns7.

NREL Solar Integration Studies

Simulated distributed PV data reflects demand profiles in utility-scale scenarios6.

Grid Interaction Variables
Solar Energy Industries Association (SEIA) Market Insight

U.S.-specific grid pricing trends and market data4.

Key variables: Historical grid price patterns (use as a proxy for forecasts).

NREL Solar Power Data

Includes synthetic grid import/export limits for hypothetical plants6.

Environmental Variables
Solargis

High-resolution weather data (temperature, cloud cover) with forecasts2.

NASA POWER & NSRDB

Hourly meteorological data (temperature, wind speed) and solar radiation45.

Canadian Solar Resource Data

Historical and near-real-time weather station data15.

Action Space Support
Battery Management
Use Household Data Package7 demand/generation profiles to simulate charge/discharge cycles.

Grid Interaction
Leverage NREL’s synthetic grid limits6 and SEIA pricing data4 to model import/export decisions.

Load Management
Analyze Household Data Package7 load-shifting opportunities during peak periods.

Generation Control
Optimize using Solargis forecasts2 and NREL’s PV system models6.

Recommended Workflow
Combine NREL’s synthetic solar data6 with Solargis forecasts2 for generation variables.

Integrate Household Data Package7 demand profiles and NASA POWER4 weather data.

Model battery dynamics using synthetic degradation equations.

Use RL frameworks (e.g., OpenAI Gym) to simulate actions based on historical and forecasted data.

For variables without direct data (e.g., battery health), synthetic modeling or hybrid datasets (e.g., physics-based equations paired with real-world generation/demand data) are necessary.