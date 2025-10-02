# Airline Fuel Optimization - Data Sources

## Overview
This system uses a **hybrid approach** combining real-time APIs and scientific models via the MCP server.

## ✅ Current Data Sources (All via MCP Server)

### 1. **Flight Tracking** - AviationStack API (Real-time)
- **Endpoint**: `/v1/flights`
- **Type**: Commercial API (Free tier available)
- **Provides**:
  - Flight status, departure/arrival airports
  - Aircraft registration and type
  - Live position, altitude, speed
  - Gate, terminal information
- **MCP Tool**: `get_flight_details`

### 2. **Weather Data** - CheckWX API (Real-time)
- **Endpoint**: `/metar/{icao}/decoded`
- **Type**: Aviation weather API
- **Provides**:
  - METAR reports for airports
  - Temperature, wind, visibility
  - Cloud conditions, pressure
- **MCP Tool**: `get_aviation_weather`

### 3. **Aircraft Performance** - OpenAP Library (Scientific Model)
- **Source**: TU Delft Open Aircraft Performance Model
- **Type**: Open-source scientific library
- **Provides**:
  - Fuel flow calculations (kg/s, kg/min, kg/hr)
  - Thrust and drag models
  - Aircraft specifications (MTOW, engine type)
  - Performance at different altitudes
- **MCP Tool**: `get_aircraft_performance`
- **Data Based On**:
  - ICAO Emission Databank
  - Published aircraft specifications
  - Validated aeronautical models

## 🔍 Why OpenAP Instead of an API?

### The Problem
**No free public APIs exist for aircraft performance data** because:
1. **Proprietary**: Airlines/manufacturers keep fuel data confidential
2. **Commercial sensitivity**: Fuel efficiency is competitive advantage
3. **Licensing**: BADA (Eurocontrol) requires paid license
4. **No business model**: No one offers free fuel burn APIs

###Available Commercial Options (Very Expensive)
- **Cirium**: $10,000+/year (Enterprise only)
- **FlightAware**: Premium plans, limited performance data
- **BADA**: Requires academic/commercial license from Eurocontrol

### Why OpenAP is the Best Solution
1. ✅ **Free & Open Source**: No API costs or rate limits
2. ✅ **Scientific Accuracy**: Validated by aerospace researchers
3. ✅ **Well Maintained**: Active development by TU Delft
4. ✅ **Comprehensive**: Covers 100+ aircraft types
5. ✅ **Integrated as MCP Tool**: Works like any other API

## 📊 Data Flow Architecture

```
User Request (Flight ID)
         ↓
    Agent System
         ↓
    MCP Client
         ↓
    MCP Server (localhost:8000)
         ├── get_flight_details → AviationStack API (Internet)
         ├── get_aviation_weather → CheckWX API (Internet)
         └── get_aircraft_performance → OpenAP (Local Library)
```

## 🎯 Benefits of This Approach

1. **Unified Interface**: All data accessed through MCP tools
2. **No Rate Limits**: OpenAP runs locally
3. **Cost Effective**: Free for all components
4. **Reliable**: No dependency on external performance APIs
5. **Accurate**: OpenAP models are peer-reviewed and validated

## 📚 Data Sources Summary

| Data Type | Source | Access Method | Cost | Real-time |
|-----------|--------|---------------|------|-----------|
| Flight Status | AviationStack | API | Free tier | ✅ Yes |
| Weather | CheckWX | API | Free tier | ✅ Yes |
| Performance | OpenAP | Python Library | Free | ❌ No (Calculated) |
| Route Waypoints | CSV/Manual | Local File | Free | ❌ No |

## 🚀 Future Enhancements

### Potential Additions:
1. **FlightPlan Database API**: For actual flight routes with waypoints
2. **ADS-B Exchange**: Real-time aircraft tracking backup
3. **Machine Learning**: Train models on historical fuel consumption
4. **Airline Integration**: Direct data feeds (enterprise partnerships)

### OpenAP Extensions:
- **openap-top**: Trajectory optimization module
- **Emission calculations**: CO2, NOx, CO tracking
- **Custom aircraft models**: Add proprietary aircraft data

## 📖 References

- **OpenAP Documentation**: https://openap.dev
- **AviationStack API**: https://aviationstack.com/documentation
- **CheckWX API**: https://www.checkwx.com/api
- **TU Delft Research**: https://github.com/TUDelft-CNS-ATM/openap
