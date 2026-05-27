# Country Standard of Living Research

## Objective
Given a country name, fetch all required data fields for the AP Macro Standard of Living worksheet, generate a formatted PDF report, and send it to the user's phone via iMessage.

## Required Inputs
- Country name (e.g., "Norway", "Chad", "Japan")

## Delivery
- Email: calebjohnsteele@gmail.com
- Method: macOS Mail.app (PDF attachment)

## Data Fields Collected
### Geography
- Natural Resources
- Land Use

### People
- Population
- Ethnic Groups
- Population Pyramid (Age Structure)
- Population Growth
- Maternal Mortality Rate
- Infant Mortality Rate
- Life Expectancy at Birth
- Physician Density
- Educational Expenditures
- School Life Expectancy

### Government
- Type
- Suffrage

### Economy
- Real GDP
- Real GDP Growth Rate
- Real GDP per Capita
- Inflation Rate
- GDP by Sector
- GDP Composition by End Use
- Labor Force
- Unemployment %
- Population below the Poverty Line
- GINI Index
- Budget Surplus/Deficit
- Current Account Balance
- Export $$$
- Export Partners
- Export Commodities
- Import $$$
- Import Partners
- Import Commodities
- Exchange Rate with USA

### Military
- Military Expenditure

### Different Source (UNDP)
- HDI: Human Development Index (from https://hdr.undp.org)

## Steps
1. Run `tools/fetch_country_data.py "{country}"` to pull data from factbook.json and HDI lookup
2. Run `tools/generate_pdf.py ".tmp/{country}_data.json"` to create the formatted PDF
3. Run `tools/send_email.py "calebjohnsteele@gmail.com" ".tmp/{country}_report.pdf" "Standard of Living Data - {country}" "Here is the Standard of Living worksheet data for {country}."` to deliver via email

## Data Sources
- **CIA World Factbook**: https://github.com/factbook/factbook.json (auto-updated weekly from original CIA data; site retired Feb 2026)
- **UNDP HDI**: https://hdr.undp.org (HDI values from 2025 Human Development Report, based on 2023 data)

## Edge Cases
- If a country name isn't found, the fetch script will attempt partial matching
- Some smaller countries may have missing fields (shown as "N/A")
- HDI values are embedded in the fetch script; if a country isn't in the lookup, it shows "N/A"
- Email requires the Mac to be signed into Mail.app with an active account

## Notes
- All intermediate files land in `.tmp/` and are disposable
- The factbook.json repo uses FIPS country codes, not ISO (mapping built into the fetch script)
