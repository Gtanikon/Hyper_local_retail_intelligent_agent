

````markdown
# Hyper Local Retail Intelligence System

## Project Overview

The Hyper Local Retail Intelligence System is an AI-powered retail analytics platform designed to improve inventory visibility, operational decision-making, and retail risk management.

The system combines machine learning forecasting, business rule intelligence, inventory optimization, Streamlit dashboards, and secure MCP-based LLM integration to create an end-to-end retail intelligence workflow.

The platform predicts next-day sales, identifies inventory risks, detects phantom inventory, recommends inventory transfers, and provides operational insights through both dashboards and natural language AI interaction.

A key objective of this project is to support operational analytics while protecting sensitive retail business data from direct exposure to external large language models.

---

# Core Objectives

The system was developed to solve major retail operational problems such as:

- Stockouts
- Overstock situations
- Phantom inventory
- Shelf imbalance
- Inefficient replenishment
- Delayed operational visibility
- Manual inventory analysis
- Lack of centralized retail intelligence

The project provides predictive analytics and AI-assisted operational monitoring for retail environments.

---

# Main Functionalities

## 1. Next-Day Sales Forecasting

The forecasting system predicts future daily sales at the store-SKU level.

### Forecast Inputs

The model uses features such as:

- Historical sales
- Rolling average sales
- Sales standard deviation
- Promotions
- Inventory availability
- Lead time metrics
- Product characteristics
- Store behavior
- Shelf metrics
- Inventory movement patterns

### Forecast Output

Primary prediction:
- `predicted_sales`

Additional derived outputs:
- expected inventory requirements
- replenishment indicators
- operational risk signals

---

# 2. Inventory Risk Detection

The system detects operational inventory risks using machine learning outputs combined with business logic.

### Risk Categories

Examples include:
- Normal
- Medium Risk
- High Risk
- Critical Risk

### Risk Signals

Generated features include:
- `stockout_risk`
- `risk_category`
- `priority_score`
- `cause_label`
- `action`

### Example Risks

- Low inventory
- High forecast demand
- Delayed replenishment
- Shelf imbalance
- Sales spikes
- Promotion-driven shortages

---

# 3. Phantom Inventory Detection

The system identifies inventory mismatches between recorded inventory and actual operational inventory behavior.

### Phantom Inventory Examples

- Inventory shown in system but unavailable on shelf
- Shelf empty despite stock recorded
- Replenishment inconsistency
- Abnormal inventory movement

### Detection Logic

The detection combines:
- stock ratios
- sales movement
- shelf fill ratios
- replenishment behavior
- inventory anomalies

Generated fields:
- `phantom_flag_rule`
- `cause_label`

---

# 4. Shelf Optimization

The platform recommends shelf balancing actions based on inventory pressure and demand forecasting.

### Optimization Goals

- Increase shelf efficiency
- Reduce dead inventory
- Improve product availability
- Minimize shelf waste

### Generated Recommendations

Examples:
- Increase shelf space
- Reduce shelf allocation
- Prioritize replenishment
- Move excess inventory

---

# 5. Inventory Transfer Recommendations

The system recommends inventory transfers between stores and regions.

### Transfer Types

#### Intra-Region Transfers
Transfers within the same region.

#### Inter-Region Transfers
Transfers across different regions.

### Transfer Logic Uses

- excess inventory
- shortage inventory
- expected demand
- regional balancing
- supply pressure

Generated fields:
- `transfer_qty`
- `region_donor`
- `region_receiver`
- `replenishment_nearby`

---

# 6. Streamlit Dashboard

The project includes a fully interactive Streamlit dashboard for operational monitoring.

The dashboard provides dynamic filtering and drill-down analysis.

---

# Dashboard Tabs

## Executive Overview

Provides:
- latest operational date
- risk summaries
- transfer summaries
- overall inventory health

---

## Phantom Inventory

Displays:
- phantom inventory stores
- inventory anomalies
- root causes
- affected SKUs

---

## Forecasting

Displays:
- predicted sales
- expected inventory
- forecast comparisons
- sales trend charts

---

## Risk & Cause Labels

Displays:
- risk classification
- priority ranking
- operational root causes
- action recommendations

---

## Shelf Optimization

Displays:
- shelf recommendations
- shelf shortages
- shelf balancing opportunities

---

## Transfers

Displays:
- inventory movement recommendations
- donor stores
- receiver stores
- transfer quantities

---

## Latest Manager View

Displays:
- latest operational incidents
- high-risk stores
- store-specific operational actions
- dynamic filtering by region/store/SKU

---

## Email Alerts

Supports operational alert generation using Gmail SMTP integration.

---

# Dynamic Dashboard Features

The dashboard supports interactive filtering using:

- Region
- Store
- SKU
- Date
- Risk Category

All tabs dynamically update based on selected filters.

This allows users to:
- inspect specific stores
- analyze operational incidents
- track inventory movement
- monitor store-level risks

---

# Privacy-Preserving LLM Integration

One of the most important features of the project is the secure LLM integration architecture.

The system prevents direct exposure of sensitive business identifiers to the external language model.

---

# Pseudo Mapping System

Instead of exposing real:
- store names
- product names
- inventory identifiers

the system generates pseudo identifiers.

Examples:
- STORE_1042
- SKU_8831

The LLM only interacts with pseudo entities.

---

# Verification Dashboard

A separate verification dashboard was developed for authorized business users.

This dashboard allows users to:
- verify pseudo identifiers
- map operational issues to real stores
- inspect real product mappings

This creates a privacy layer between:
- operational data
- external AI systems

---

# MCP Integration

The project integrates Claude using the Model Context Protocol (MCP).

The MCP server acts as a secure tool layer between:
- the retail data system
- the LLM

---

# MCP Architecture

The MCP server exposes operational tools such as:

- latest issue summaries
- transfer analytics
- risk lookups
- shelf optimization insights
- operational intelligence queries

Claude can call these tools and generate natural language summaries from the results.

---

# Important Clarification

This system is currently:

- an AI-assisted analytics platform
- a tool-integrated intelligence system

It is NOT yet a fully autonomous AI agent.

The current system:
- predicts
- analyzes
- summarizes
- recommends

but does not autonomously execute operational actions.

---

# Future Agent Extension

The architecture supports future expansion into:
- autonomous retail agents
- automated replenishment agents
- multi-step operational workflows
- decision automation systems

---

# Project Architecture

```text
Notebook (Data + ML + Business Logic)
        ↓
Generated CSV Outputs
        ↓
Streamlit Dashboard
        ↓
MCP Tool Server
        ↓
Claude LLM Integration
        ↓
Verification Dashboard
````

---

# Folder Structure

```text
Hyper_local_retail_system/
│
├── phantom_inventory.ipynb
│
│   Main notebook containing:
│   - data loading
│   - feature engineering
│   - forecasting models
│   - inventory logic
│   - risk logic
│   - transfer recommendations
│   - shelf optimization
│
├── app.py
│
│   Main Streamlit dashboard
│
├── inventory_mcp_server.py
│
│   MCP tool server used by Claude
│
├── create_secure_mappings.py
│
│   Generates pseudo mappings
│
├── verification_tool.py
│
│   Client-side verification dashboard
│
├── outputs/
│
│   Generated CSV outputs
│
└── README.md
```

---

# Technologies Used

## Languages

* Python

## Libraries

* pandas
* numpy
* scikit-learn
* streamlit
* matplotlib
* plotly
* mcp

## AI Integration

* Claude Desktop
* MCP SDK

---

# Installation

## Install Required Packages

```bash
pip install pandas numpy scikit-learn matplotlib plotly streamlit mcp
```

Optional:

```bash
pip install xgboost lightgbm
```

---

# Running the Project

## Step 1 — Run the Notebook

Open:

```text
phantom_inventory.ipynb
```

Run all cells to:

* generate features
* train models
* generate outputs
* save CSV files

---

# Step 2 — Run Streamlit Dashboard

```bash
streamlit run app.py
```

Dashboard URL:

```text
http://localhost:8501
```

---

# Step 3 — Run MCP Server

```bash
py -3.13 inventory_mcp_server.py
```

---

# Step 4 — Configure Claude MCP

Example configuration:

```json
{
  "mcpServers": {
    "inventory-intelligence": {
      "command": "py",
      "args": [
        "-3.13",
        "C:\\Users\\YOUR_USERNAME\\Downloads\\inventory_mcp_server.py"
      ]
    }
  }
}
```

Restart Claude Desktop after configuration.

---

# Email Alerts Setup

The dashboard supports Gmail SMTP alerts.

For Gmail:

1. Enable 2-Step Verification
2. Generate App Password
3. Use App Password inside dashboard

Do NOT use your normal Gmail password.

---

# Model Evaluation Metrics

## MAE — Mean Absolute Error

Measures average prediction error.

Lower MAE indicates:

* better forecasting accuracy

---

## RMSE — Root Mean Squared Error

Measures prediction error while penalizing larger mistakes more heavily.

Lower RMSE indicates:

* more stable predictions
* fewer large forecasting errors

---

# Business Value

The system helps organizations:

* reduce stockouts
* improve inventory visibility
* detect phantom inventory
* improve replenishment decisions
* optimize shelf allocation
* improve operational response time
* support retail intelligence workflows
* enable AI-assisted operational analytics

---

# Security Design

The project was intentionally designed to minimize direct exposure of business-sensitive data to external AI systems.

Security measures include:

* pseudo mapping
* separated verification dashboard
* tool-based data exposure
* controlled operational summaries

---

# Future Improvements

Potential future extensions include:

* autonomous AI agents
* live retail monitoring
* API integrations
* automated replenishment execution
* reinforcement learning optimization
* real-time streaming analytics
* supply chain optimization
* advanced retail simulations

---

# Final Summary

This project combines:

* machine learning
* inventory intelligence
* business logic
* Streamlit visualization
* MCP integration
* privacy-preserving AI workflows

to create a modern retail operational intelligence platform capable of assisting managers through predictive analytics and natural language AI interaction.

```
```
