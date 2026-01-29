## Agri-Tech Hackathon 2026

## Team Name : Meticura Team Leader : Lokesh Konka

# Problem Statement : AI Demand Forecasting for Local Markets

## Problem Identified:

## Core Problem

### Traditional forecasting methods overlook festival cycles, trends, and weather, causing

### inaccurate demand prediction, poor inventory decisions, and high volatility in local markets.

### This leads to overstocking, wastage, and lost sales, severely impacting small vendors.

## Limitations of Existing Systems

### Existing systems rely on historical averages, fail to model sudden or non-linear demand shifts,

### and lack real-time adaptability.

## Impact of the Problem

### Increased wastage of perishables, revenue loss during peak demand, financial stress on small

### vendors, and inefficient supply chains

## Economic Feasibility

### No expensive hardware; low development and maintenance cost reduces losses from

### stockouts and overstocking.

## Our Solution:

### ● Uses a data‑driven approach combining multiple influencing factors.

### ● Applies time‑series analysis and machine‑learning models.

### ● Captures both recurring patterns and sudden demand fluctuations.

## Key Components:

**Data Integration**

- Sales data from billing systems or CSV files.
- Festival calendars to capture event driven demand
    spikes
- Weather data (Temp,Rainfall) for climate based on
    demand changes
**Key Features
- Localized Forecasting:** Market specific predictions
- **Festival** ‑ **Aware Prediction:** Detects festive demand
spikes


- **Weather** ‑ **Sensitive Forecasting:** Models climate impact on demand.
- **Trend & Seasonality Analysis:** Separates normal vs abnormal demand.
- **Improved Accuracy:** Lower errors than traditional methods.
- **Inventory Support:** Data‑driven stock planning.
- **Scalable Design:** Works from single shops to multi‑market systems.
-

## Technology Stack:

### 1. Developed using a modular and scalable architecture based on widely adopted open-source

```
technologies.
```
2. Incorporates historical sales data, festival calendars, and weather APIs to capture real-world
    demand drivers.
3. Utilizes Pandas and NumPy for comprehensive data processing and the implementation of
    advanced feature engineering techniques (including lags, rolling averages, and event flags).
4. Achieves accurate forecasting through the application of time-series models
    (SARIMA/ARIMAX) and regression-based Machine Learning models.
5. Designed for local execution on standard computing hardware, with inherent cloud scalability
    and optional integration with Flask/FastAPI to facilitate expansion.

## Use Case & System Architecture:


